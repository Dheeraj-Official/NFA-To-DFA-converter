/*
    ============================================================
    NFA to DFA Converter — Object-Oriented Design
    ============================================================
    Algorithm : Subset Construction (with epsilon-transition support)
    Output    : Console transition table + Graphviz (.dot) diagrams
                for BOTH the NFA and the resulting DFA.

    DESIGN
    ------
    - class NFA : owns the NFA's data (states, alphabet, transitions).
                Knows how to read itself from input, compute
                epsilon-closures / moves, and export itself as a
                Graphviz diagram.
    - class DFA : owns the DFA's data. Knows how to *build* itself
                from an NFA (subset construction), print itself as
                a transition table, and export itself as a Graphviz
                diagram.
    - main()    : just wires the two classes together. No algorithm
                logic lives in main — that's the point of the design.

    INPUT FORMAT (stdin or a file passed as argv[1]):
    --------------------------------------------------
    n                          -> number of NFA states (0..n-1)
    m                          -> number of alphabet symbols
    s1 s2 ... sm               -> the alphabet symbols (e.g. a b)
    start                      -> NFA start state
    f                          -> number of final states
    fs1 ... fsf                -> the final states
    t                          -> number of transitions
    from sym to   (x t lines)  -> use 'e' for epsilon

    example 
    3
    2
    a b
    0
    1
    2
    4
    0 a 0
    0 b 0
    0 a 1
    1 b 2

    COMPILE (works on any C++11-or-later compiler — g++, clang++, MSVC):
        g++ -std=c++17 -O2 -o nfa_to_dfa nfa_to_dfa_oop.cpp

    RENDER THE DIAGRAMS:
        dot -Tpng nfa.dot -o nfa.png
        dot -Tpng dfa.dot -o dfa.png
    ============================================================
*/
#include <bits/stdc++.h>
using namespace std;

// ============================================================
//  Small shared JSON helpers — used by both NFA::exportJson()
//  and DFA::exportJson() so the "turn a set/vector into a JSON
//  array" logic exists in exactly one place.
// ============================================================
static string jsonIntArray(const set<int> &s)
{
    string result = "[";
    bool first = true;
    for (set<int>::const_iterator it = s.begin(); it != s.end(); ++it)
    {
        result += (first ? "" : ", ") + to_string(*it);
        first = false;
    }
    result += "]";
    return result;
}

static string jsonAlphabetArray(const vector<char> &alphabet)
{
    string result = "[";
    for (size_t i = 0; i < alphabet.size(); ++i)
        result += (i ? ", \"" : "\"") + string(1, alphabet[i]) + "\"";
    result += "]";
    return result;
}

// ============================================================
//  class NFA
//  Represents a (possibly non-deterministic, epsilon-capable)
//  finite automaton read from user input.
// ============================================================
class NFA
{
public:
    // Reads the NFA description from an input stream in the
    // format documented at the top of this file.
    void readFromInput(istream &in)
    {
        in >> numStates_;

        int alphabetSize;
        in >> alphabetSize;
        alphabet_.resize(alphabetSize);
        for (int i = 0; i < alphabetSize; ++i)
            in >> alphabet_[i];

        in >> startState_;

        int finalCount;
        in >> finalCount;
        for (int i = 0; i < finalCount; ++i)
        {
            int state;
            in >> state;
            finalStates_.insert(state);
        }

        int transitionCount;
        in >> transitionCount;
        for (int i = 0; i < transitionCount; ++i)
        {
            int from, to;
            char symbol;
            in >> from >> symbol >> to;
            transitions_[make_pair(from, symbol)].insert(to);
        }
    }

    // Epsilon-closure of a set of states: every state reachable
    // using only epsilon ('e') transitions.
    set<int> epsilonClosure(const set<int> &states) const
    {
        set<int> closure = states;
        stack<int> pending;
        for (set<int>::const_iterator it = states.begin(); it != states.end(); ++it)
            pending.push(*it);

        while (!pending.empty())
        {
            int current = pending.top();
            pending.pop();

            map<pair<int, char>, set<int>>::const_iterator found =
                transitions_.find(make_pair(current, 'e'));

            if (found != transitions_.end())
            {
                const set<int> &reachable = found->second;
                for (set<int>::const_iterator it = reachable.begin(); it != reachable.end(); ++it)
                {
                    if (closure.insert(*it).second) // .second == true if newly inserted
                        pending.push(*it);
                }
            }
        }
        return closure;
    }

    // States reachable from 'states' by reading exactly one 'symbol'
    // (no epsilon-closure applied here — caller combines as needed).
    set<int> move(const set<int> &states, char symbol) const
    {
        set<int> result;
        for (set<int>::const_iterator it = states.begin(); it != states.end(); ++it)
        {
            map<pair<int, char>, set<int>>::const_iterator found =
                transitions_.find(make_pair(*it, symbol));
            if (found != transitions_.end())
                result.insert(found->second.begin(), found->second.end());
        }
        return result;
    }

    // Writes this NFA out as machine-readable JSON — meant for any
    // downstream tool (e.g. a Python visualizer) to consume directly,
    // instead of re-parsing the human-readable console output.
    void exportJson(const string &filename) const
    {
        ofstream out(filename.c_str());
        out << "{\n";
        out << "  \"numStates\": " << numStates_ << ",\n";
        out << "  \"alphabet\": " << jsonAlphabetArray(alphabet_) << ",\n";
        out << "  \"start\": " << startState_ << ",\n";
        out << "  \"finalStates\": " << jsonIntArray(finalStates_) << ",\n";

        out << "  \"transitions\": [\n";
        bool firstT = true;
        for (map<pair<int, char>, set<int>>::const_iterator it = transitions_.begin();
            it != transitions_.end(); ++it)
        {
            int from = it->first.first;
            char symbol = it->first.second;
            for (set<int>::const_iterator dit = it->second.begin(); dit != it->second.end(); ++dit)
            {
                out << (firstT ? "    " : ",\n    ");
                out << "{\"from\": " << from << ", \"symbol\": \"" << symbol
                    << "\", \"to\": " << *dit << "}";
                firstT = false;
            }
        }
        out << "\n  ]\n";
        out << "}\n";
        out.close();
        cout << "JSON file written: " << filename << "\n";
    }

    // ---- read-only accessors, used by DFA::build() ----
    int stateCount() const { return numStates_; }
    int startState() const { return startState_; }
    const vector<char> &alphabet() const { return alphabet_; }
    const set<int> &finalStates() const { return finalStates_; }

private:
    int numStates_ = 0;
    vector<char> alphabet_;
    int startState_ = 0;
    set<int> finalStates_;
    map<pair<int, char>, set<int>> transitions_;
};

// ============================================================
//  class DFA
//  Built FROM an NFA via the subset-construction algorithm.
//  Each DFA state corresponds to a *set* of NFA states.
// ============================================================
class DFA
{
public:
    // Runs subset construction on the given NFA and stores the result.
    void build(const NFA &nfa)
    {
        alphabet_ = nfa.alphabet();

        map<set<int>, int> idOfStateSet;
        queue<int> pending;

        set<int> startSet = nfa.epsilonClosure(singleton(nfa.startState()));
        idOfStateSet[startSet] = 0;
        stateSets_.push_back(startSet);
        pending.push(0);

        while (!pending.empty())
        {
            int currentId = pending.front();
            pending.pop();
            const set<int> currentSet = stateSets_[currentId];

            for (size_t k = 0; k < alphabet_.size(); ++k)
            {
                char symbol = alphabet_[k];
                set<int> closure = nfa.epsilonClosure(nfa.move(currentSet, symbol));
                if (closure.empty())
                    continue; // no transition -> implicit dead state

                int nextId;
                map<set<int>, int>::iterator found = idOfStateSet.find(closure);
                if (found == idOfStateSet.end())
                {
                    nextId = static_cast<int>(stateSets_.size());
                    idOfStateSet[closure] = nextId;
                    stateSets_.push_back(closure);
                    pending.push(nextId);
                }
                else
                {
                    nextId = found->second;
                }
                transitions_[make_pair(currentId, symbol)] = nextId;
            }
        }

        // A DFA state is final if the NFA-state-set it represents
        // contains at least one NFA final state.
        for (size_t i = 0; i < stateSets_.size(); ++i)
        {
            const set<int> &stateSet = stateSets_[i];
            for (set<int>::const_iterator it = stateSet.begin(); it != stateSet.end(); ++it)
            {
                if (nfa.finalStates().count(*it))
                {
                    finalStates_.insert(static_cast<int>(i));
                    break;
                }
            }
        }
    }

    // Prints the DFA states, start/final states, and transition table.
    void print() const
    {
        cout << "\n===== Resulting DFA =====\n";
        cout << "Number of DFA states: " << stateSets_.size() << "\n\n";

        cout << "DFA states (name : corresponding NFA state set):\n";
        for (size_t i = 0; i < stateSets_.size(); ++i)
            cout << "  D" << i << " : " << setToString(stateSets_[i]) << "\n";

        cout << "\nStart state: D0\n";

        cout << "\nFinal states: ";
        if (finalStates_.empty())
            cout << "(none)";
        for (set<int>::const_iterator it = finalStates_.begin(); it != finalStates_.end(); ++it)
            cout << "D" << *it << " ";
        cout << "\n";

        cout << "\nTransition table:\n";
        cout << left << setw(10) << "State";
        for (size_t k = 0; k < alphabet_.size(); ++k)
            cout << setw(10) << alphabet_[k];
        cout << "\n";

        for (size_t i = 0; i < stateSets_.size(); ++i)
        {
            cout << left << setw(10) << ("D" + to_string(i));
            for (size_t k = 0; k < alphabet_.size(); ++k)
            {
                map<pair<int, char>, int>::const_iterator found =
                    transitions_.find(make_pair(static_cast<int>(i), alphabet_[k]));
                cout << setw(10) << (found != transitions_.end() ? "D" + to_string(found->second) : "-");
            }
            cout << "\n";
        }
    }

    // Writes this DFA out as machine-readable JSON, including each DFA
    // state's underlying NFA-state-set, for a downstream visualizer.
    void exportJson(const string &filename) const
    {
        ofstream out(filename.c_str());
        out << "{\n";
        out << "  \"numStates\": " << stateSets_.size() << ",\n";
        out << "  \"alphabet\": " << jsonAlphabetArray(alphabet_) << ",\n";
        out << "  \"start\": 0,\n";
        out << "  \"finalStates\": " << jsonIntArray(finalStates_) << ",\n";

        out << "  \"stateSets\": [\n";
        for (size_t i = 0; i < stateSets_.size(); ++i)
        {
            out << "    " << jsonIntArray(stateSets_[i]);
            out << (i + 1 < stateSets_.size() ? ",\n" : "\n");
        }
        out << "  ],\n";

        out << "  \"transitions\": [\n";
        bool firstT = true;
        for (map<pair<int, char>, int>::const_iterator it = transitions_.begin();
            it != transitions_.end(); ++it)
        {
            int from = it->first.first;
            char symbol = it->first.second;
            int to = it->second;
            out << (firstT ? "    " : ",\n    ");
            out << "{\"from\": " << from << ", \"symbol\": \"" << symbol
                << "\", \"to\": " << to << "}";
            firstT = false;
        }
        out << "\n  ]\n";
        out << "}\n";
        out.close();
        cout << "JSON file written: " << filename << "\n";
    }

private:
    static set<int> singleton(int x)
    {
        set<int> s;
        s.insert(x);
        return s;
    }

    static string setToString(const set<int> &s)
    {
        if (s.empty())
            return "{}";
        string result = "{";
        bool first = true;
        for (set<int>::const_iterator it = s.begin(); it != s.end(); ++it)
        {
            if (!first)
                result += ",";
            result += to_string(*it);
            first = false;
        }
        result += "}";
        return result;
    }

    vector<set<int>> stateSets_;            // DFA state id -> the NFA states it represents
    map<pair<int, char>, int> transitions_; // DFA transition function
    set<int> finalStates_;
    vector<char> alphabet_;
};

// ============================================================
//  main — just orchestration, no algorithm logic here
// ============================================================
int main(int argc, char *argv[])
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    ifstream fileInput;
    if (argc > 1)
    {
        fileInput.open(argv[1]);
        if (!fileInput)
        {
            cerr << "Could not open file: " << argv[1] << "\n";
            return 1;
        }
        cin.rdbuf(fileInput.rdbuf());
    }

    NFA nfa;
    nfa.readFromInput(cin);
    nfa.exportJson("nfa.json");

    DFA dfa;
    dfa.build(nfa);
    dfa.print();
    dfa.exportJson("dfa.json");

    return 0;
}