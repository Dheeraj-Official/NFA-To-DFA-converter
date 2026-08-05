"""
draw_automata.py
-----------------
Reads nfa.json / dfa.json (machine-readable data dumped by the C++
program) and renders nicer, styled Graphviz diagrams using the Python
`graphviz` library.

This deliberately does NOT parse output.txt (the human-readable console
text) — that format is for humans to read, not for other programs to
consume. The C++ side already owns the automaton data, so it exports
that data as JSON; this script only reads the JSON.

Usage:
    python3 draw_automata.py                 # looks for nfa.json / dfa.json
                                            # in the current directory
    python3 draw_automata.py --dir /path/to  # look in a specific folder

Output:
    nfa_pretty.dot
    dfa_pretty.dot
    dfa_minimized_pretty.dot
    (render with: dot -Tpng nfa_pretty.dot -o nfa_pretty.png)
"""

import json
import argparse
import os
import graphviz

# Per-automaton-type styling: everything draw_automaton() needs to tell
# an NFA apart from a DFA visually.
STYLES = {
    "nfa": {
        "graph_name": "NFA",
        "prefix": "N",
        "node_color": "#2f6fab",
        "start_fill": "#c9e4ff",
        "node_label": lambda i, data: str(i),
        "symbol": lambda sym: sym,  # display symbols as-is
    },
    "dfa": {
        "graph_name": "DFA",
        "prefix": "D",
        "node_color": "#a56b19",
        "start_fill": "#ffe1a8",
        # DFA nodes show the underlying NFA state-set, e.g. "D1\n{0,1}"
        "node_label": lambda i, data: f"D{i}\\n{{{','.join(str(x) for x in data['stateSets'][i])}}}",
        "symbol": lambda sym: sym,  # display symbols as-is
    },
    "dfa_minimized": {
        "graph_name": "Minimized DFA\\n(Optimized)",
        "prefix": "M",
        "node_color": "#d97706",
        "start_fill": "#f0e68c",
        # Minimized DFA nodes show the original DFA states they represent
        "node_label": lambda i, data: f"M{i}\\n{{{','.join(str(x) for x in data['stateSets'][i])}}}",
        "symbol": lambda sym: sym,  # display symbols as-is
    },
}

FINAL_FILL = "#b7f0c0"
DEFAULT_FILL = "#f2f2f2"


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def merge_parallel_edges(transitions, symbol_fn):
    """Group transitions sharing a (from, to) pair into one comma-joined label."""
    merged = {}
    for t in transitions:
        key = (t["from"], t["to"])
        merged.setdefault(key, []).append(symbol_fn(t["symbol"]))
    return merged


def minimize_dfa(dfa_data):
    """
    Minimize DFA using the table-filling method (Hopcroft's algorithm simplified).
    Returns a new DFA data structure with minimized states.
    """
    num_states = dfa_data["numStates"]
    alphabet = dfa_data["alphabet"]
    final_states = set(dfa_data["finalStates"])
    transitions = dfa_data["transitions"]
    
    # Create transition table: state -> symbol -> state
    trans_table = {}
    for t in transitions:
        from_state = t["from"]
        symbol = t["symbol"]
        to_state = t["to"]
        if from_state not in trans_table:
            trans_table[from_state] = {}
        trans_table[from_state][symbol] = to_state
    
    # Mark distinguishable pairs using table-filling method
    distinguishable = {}
    
    # Initialize: all pairs of final and non-final states are distinguishable
    for i in range(num_states):
        for j in range(i + 1, num_states):
            is_i_final = i in final_states
            is_j_final = j in final_states
            if is_i_final != is_j_final:
                distinguishable[(i, j)] = True
    
    # Table-filling algorithm
    changed = True
    while changed:
        changed = False
        for i in range(num_states):
            for j in range(i + 1, num_states):
                if (i, j) not in distinguishable:
                    # Check if there's a symbol that leads to distinguishable states
                    for symbol in alphabet:
                        i_next = trans_table.get(i, {}).get(symbol)
                        j_next = trans_table.get(j, {}).get(symbol)
                        
                        # Handle missing transitions (treat as same state)
                        if i_next is None and j_next is None:
                            continue
                        
                        # If one has transition and other doesn't, they're distinguishable
                        if (i_next is None) != (j_next is None):
                            distinguishable[(i, j)] = True
                            changed = True
                            break
                        
                        if i_next is not None and j_next is not None and i_next != j_next:
                            # Check if the target states are distinguishable
                            a, b = min(i_next, j_next), max(i_next, j_next)
                            if (a, b) in distinguishable:
                                distinguishable[(i, j)] = True
                                changed = True
                                break
    
    # Group equivalent states
    groups = []
    state_to_group = {}
    
    for i in range(num_states):
        found_group = False
        for group in groups:
            representative = group[0]
            if (min(i, representative), max(i, representative)) not in distinguishable:
                group.append(i)
                state_to_group[i] = group
                found_group = True
                break
        if not found_group:
            new_group = [i]
            groups.append(new_group)
            state_to_group[i] = new_group
    
    # Create minimized DFA
    group_to_id = {tuple(sorted(group)): idx for idx, group in enumerate(groups)}
    
    # Build minimized transitions
    minimized_transitions = []
    for group in groups:
        group_key = tuple(sorted(group))
        group_id = group_to_id[group_key]
        
        # Get transitions from any state in the group (they should be equivalent)
        representative = group[0]
        for symbol in alphabet:
            next_state = trans_table.get(representative, {}).get(symbol)
            if next_state is not None:
                # Find which group the next state belongs to
                for g in groups:
                    if next_state in g:
                        next_group_key = tuple(sorted(g))
                        next_group_id = group_to_id[next_group_key]
                        # Avoid duplicate transitions
                        existing = False
                        for t in minimized_transitions:
                            if t["from"] == group_id and t["symbol"] == symbol and t["to"] == next_group_id:
                                existing = True
                                break
                        if not existing:
                            minimized_transitions.append({
                                "from": group_id,
                                "symbol": symbol,
                                "to": next_group_id
                            })
                        break
    
    # Find new start state
    start_state = dfa_data["start"]
    start_group = state_to_group[start_state]
    start_group_key = tuple(sorted(start_group))
    minimized_start = group_to_id[start_group_key]
    
    # Find new final states
    minimized_final = []
    for group in groups:
        group_key = tuple(sorted(group))
        group_id = group_to_id[group_key]
        if any(state in final_states for state in group):
            minimized_final.append(group_id)
    
    # Create state sets for display (show original DFA states)
    minimized_state_sets = [sorted(group) for group in groups]
    
    return {
        "numStates": len(groups),
        "alphabet": alphabet,
        "start": minimized_start,
        "finalStates": minimized_final,
        "stateSets": minimized_state_sets,
        "transitions": minimized_transitions
    }


def draw_automaton(data, out_base, kind):
    style = STYLES[kind]
    prefix = style["prefix"]
    final_states = set(data["finalStates"])
    start = data["start"]
    num_states = data["numStates"]

    g = graphviz.Digraph(style["graph_name"], format="png")
    g.attr(rankdir="LR", bgcolor="white", fontname="Helvetica")
    g.attr("node", fontname="Helvetica", fontsize="13", style="filled")
    g.attr("edge", fontname="Helvetica", fontsize="12", color="#555555")

    g.node("__start", shape="point", width="0.05", color="white")
    g.edge("__start", f"{prefix}{start}", color="#333333")

    for i in range(num_states):
        is_final = i in final_states
        fill = style["start_fill"] if i == start else (FINAL_FILL if is_final else DEFAULT_FILL)
        g.node(
            f"{prefix}{i}",
            label=style["node_label"](i, data),
            shape="doublecircle" if is_final else "circle",
            fillcolor=fill,
            color=style["node_color"],
            penwidth="2" if is_final else "1.5",
        )

    merged = merge_parallel_edges(data["transitions"], style["symbol"])
    for (frm, to), syms in merged.items():
        g.edge(f"{prefix}{frm}", f"{prefix}{to}", label=", ".join(syms))

    g.save(f"{out_base}.dot")
    print(f"Wrote {out_base}.dot")


def main():
    parser = argparse.ArgumentParser(description="Render pretty NFA/DFA diagrams from JSON data.")
    parser.add_argument("--dir", default=".", help="Directory containing nfa.json / dfa.json")
    args = parser.parse_args()

    for kind in ("nfa", "dfa"):
        path = os.path.join(args.dir, f"{kind}.json")
        if os.path.exists(path):
            try:
                draw_automaton(load_json(path), os.path.join(args.dir, f"{kind}_pretty"), kind)
            except Exception as e:
                print(f"Error processing {kind.upper()}: {e}")
        else:
            print(f"Skipping {kind.upper()}: {path} not found")
    
    # Process DFA minimization
    dfa_path = os.path.join(args.dir, "dfa.json")
    if os.path.exists(dfa_path):
        try:
            dfa_data = load_json(dfa_path)
            minimized_dfa = minimize_dfa(dfa_data)
            
            # Save minimized DFA as JSON
            minimized_json_path = os.path.join(args.dir, "dfa_minimized.json")
            with open(minimized_json_path, "w") as f:
                json.dump(minimized_dfa, f, indent=2)
            print(f"Wrote {minimized_json_path}")
            
            # Generate diagram for minimized DFA
            draw_automaton(minimized_dfa, os.path.join(args.dir, "dfa_minimized_pretty"), "dfa_minimized")
        except Exception as e:
            print(f"Error processing DFA minimization: {e}")


if __name__ == "__main__":
    main()
