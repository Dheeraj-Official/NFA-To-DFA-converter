from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os
import tempfile
import shutil

app = FastAPI()

# Get environment variables
PORT = int(os.getenv("PORT", 5000))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths to executables and scripts
# On Linux (Render) the executable won't have .exe extension
# On Windows (local) it will have .exe extension
base_executable = os.path.join(os.path.dirname(__file__), 'cpp', '01_NFA_To_DFA')
PYTHON_SCRIPT = os.path.join(os.path.dirname(__file__), 'python', 'draw_automata.py')

# Determine which executable to use based on OS
if os.name == 'nt':  # Windows
    CPP_EXECUTABLE = base_executable + '.exe'
else:  # Linux/Unix (Render)
    CPP_EXECUTABLE = base_executable

# Pydantic models for request/response
class Transition(BaseModel):
    from_state: int
    symbol: str
    to_state: int

class NFARequest(BaseModel):
    numStates: int
    alphabet: list[str]
    startState: int
    finalStates: list[int]
    transitions: list[Transition]

class NFAResponse(BaseModel):
    numStates: int
    alphabet: list[str]
    start: int
    finalStates: list[int]
    transitions: list[dict]

class DFAResponse(BaseModel):
    numStates: int
    alphabet: list[str]
    start: int
    finalStates: list[int]
    stateSets: list[list[int]]
    transitions: list[dict]

class ConversionResponse(BaseModel):
    nfa: dict
    dfa: dict
    dfaMinimized: dict
    nfaImage: str
    dfaImage: str
    dfaMinimizedImage: str

@app.post("/api/convert", response_model=ConversionResponse)
async def convert_nfa_to_dfa(data: NFARequest):
    try:
        # Create temporary input file for C++ program
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            # Write input in the format expected by C++ program
            f.write(f"{data.numStates}\n")
            f.write(f"{len(data.alphabet)}\n")
            f.write(' '.join(data.alphabet) + '\n')
            f.write(f"{data.startState}\n")
            f.write(f"{len(data.finalStates)}\n")
            f.write(' '.join(map(str, data.finalStates)) + '\n')
            f.write(f"{len(data.transitions)}\n")
            for transition in data.transitions:
                f.write(f"{transition.from_state} {transition.symbol} {transition.to_state}\n")
            input_file = f.name
        
        print(f"Created input file: {input_file}")
        print(f"Input data: states={data.numStates}, alphabet={data.alphabet}, start={data.startState}")
        
        # Create temporary directory for output files
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Run C++ program to convert NFA to DFA
            current_dir = os.path.dirname(__file__)
            
            # Copy input file to backend directory
            backend_input = os.path.join(current_dir, 'input.txt')
            shutil.copy(input_file, backend_input)
            
            # Check if C++ executable exists
            if not os.path.exists(CPP_EXECUTABLE):
                # Try to compile it if it doesn't exist
                cpp_source = os.path.join(os.path.dirname(base_executable), '01_NFA_To_DFA.cpp')
                print(f"Looking for C++ source at: {cpp_source}")
                print(f"Source exists: {os.path.exists(cpp_source)}")
                
                if os.path.exists(cpp_source):
                    print("Compiling C++ program...")
                    # Compile without .exe extension for Linux
                    output_executable = base_executable
                    try:
                        result = subprocess.run(['g++', '-std=c++17', '-O2', cpp_source, '-o', output_executable], 
                                              capture_output=True, text=True, check=True)
                        print(f"Compilation successful. Output: {result.stdout}")
                        # Update the executable path
                        CPP_EXECUTABLE = output_executable
                    except subprocess.CalledProcessError as e:
                        print(f"Compilation failed: {e.stderr}")
                        raise HTTPException(status_code=500, detail=f'C++ compilation failed: {e.stderr}')
                else:
                    print(f"C++ source file not found at {cpp_source}")
                    raise HTTPException(status_code=500, detail='C++ executable not found and source file missing')
            
            print(f"Using C++ executable: {CPP_EXECUTABLE}")
            print(f"Executable exists: {os.path.exists(CPP_EXECUTABLE)}")
            
            # Run C++ program (assuming it outputs to current directory)
            print(f"Running C++ executable: {CPP_EXECUTABLE} with input: {backend_input}")
            try:
                result = subprocess.run([CPP_EXECUTABLE, backend_input], cwd=current_dir, 
                                      capture_output=True, text=True, check=True)
                print(f"C++ execution successful. Output: {result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"C++ execution failed: {e.stderr}")
                raise HTTPException(status_code=500, detail=f'C++ execution failed: {e.stderr}')
            
            # Read the generated JSON files
            with open(os.path.join(current_dir, 'nfa.json'), 'r') as f:
                nfa_data = json.load(f)
            
            with open(os.path.join(current_dir, 'dfa.json'), 'r') as f:
                dfa_data = json.load(f)
            
            # Run Python script to generate .dot files
            print(f"Running Python script: {PYTHON_SCRIPT}")
            try:
                result = subprocess.run(['python', PYTHON_SCRIPT, '--dir', current_dir], 
                                      capture_output=True, text=True, check=True)
                print(f"Python script execution successful. Output: {result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"Python script execution failed: {e.stderr}")
                raise HTTPException(status_code=500, detail=f'Python script execution failed: {e.stderr}')
            
            # Use Graphviz to convert .dot files to SVG
            nfa_dot_path = os.path.join(current_dir, 'nfa_pretty.dot')
            dfa_dot_path = os.path.join(current_dir, 'dfa_pretty.dot')
            dfa_minimized_dot_path = os.path.join(current_dir, 'dfa_minimized_pretty.dot')
            nfa_svg_path = os.path.join(current_dir, 'nfa_pretty.svg')
            dfa_svg_path = os.path.join(current_dir, 'dfa_pretty.svg')
            dfa_minimized_svg_path = os.path.join(current_dir, 'dfa_minimized_pretty.svg')
            
            subprocess.run(['dot', '-Tsvg', nfa_dot_path, '-o', nfa_svg_path], check=True)
            subprocess.run(['dot', '-Tsvg', dfa_dot_path, '-o', dfa_svg_path], check=True)
            subprocess.run(['dot', '-Tsvg', dfa_minimized_dot_path, '-o', dfa_minimized_svg_path], check=True)
            
            # Read the generated SVG files
            with open(nfa_svg_path, 'r') as f:
                nfa_svg = f.read()
            
            with open(dfa_svg_path, 'r') as f:
                dfa_svg = f.read()
            
            with open(dfa_minimized_svg_path, 'r') as f:
                dfa_minimized_svg = f.read()
            
            # Read the minimized DFA JSON
            with open(os.path.join(current_dir, 'dfa_minimized.json'), 'r') as f:
                dfa_minimized = json.load(f)
            
            return {
                'nfa': nfa_data,
                'dfa': dfa_data,
                'dfaMinimized': dfa_minimized,
                'nfaImage': nfa_svg,
                'dfaImage': dfa_svg,
                'dfaMinimizedImage': dfa_minimized_svg
            }
            
        finally:
            # Clean up temporary files
            if os.path.exists(input_file):
                os.unlink(input_file)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    except subprocess.CalledProcessError as e:
        error_msg = f'Conversion failed: {str(e)}'
        print(f"ERROR: {error_msg}")
        print(f"stderr: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f'Unexpected error: {str(e)}'
        print(f"ERROR: {error_msg}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/")
async def root():
    return {"message": "NFA to DFA Converter API"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
