# NFA to DFA Converter Web Application

A beautiful web application that converts Non-Deterministic Finite Automata (NFA) to Deterministic Finite Automata (DFA) with interactive visual diagrams and automatic DFA minimization.

## 🎯 Features

- **Interactive Web Interface**: User-friendly React-based frontend for inputting NFA data
- **Real-time Conversion**: C++ backend powered by subset construction algorithm
- **DFA Minimization**: Automatic DFA optimization using table-filling algorithm
- **Beautiful Visualizations**: Server-side Graphviz diagrams rendered as SVG
- **Modern UI Controls**: 
  - Icon-based zoom controls (reset view, fullscreen)
  - Gradient toolbar with glassmorphism effect
  - Positioned above diagram title for better UX
- **Interactive Navigation**: 
  - Mouse wheel zoom (50% to 1000%)
  - Click and drag to pan around diagrams
  - Fullscreen mode for detailed inspection
- **Three Diagrams**: NFA, regular DFA, and minimized DFA displayed side by side
- **Elegant Title Formatting**: Two-line display with title and subtitle
- **JSON Data Export**: All automata data available in JSON format
- **Epsilon Support**: Handles epsilon transitions in NFA (displayed as 'e')
- **Example Loading**: Pre-built examples with epsilon transitions and multiple alphabets
- **Responsive Design**: Works on desktop and tablet devices

##  Setup Instructions

### Prerequisites

- **Node.js** (v14 or higher)
- **Python** (v3.7 or higher)
- **g++** (for C++ compilation, if needed)
- **pip** (Python package manager)
- **Graphviz** (installed system-wide for diagram generation)

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure the C++ executable exists:**
   - If `01_NFA_To_DFA.exe` exists in `backend/cpp/`, you're ready to go
   - If not, compile it from source:
     ```bash
     g++ -std=c++17 -O2 backend/cpp/01_NFA_To_DFA.cpp -o backend/cpp/01_NFA_To_DFA.exe
     ```

4. **Start the FastAPI server:**
   ```bash
   uvicorn app:app --host 127.0.0.1 --port 5000
   ```
   The server will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173`

## 🎮 Usage

1. **Open the web application** at `http://localhost:5173`

2. **Enter NFA data:**
   - **Number of States**: Total states in your NFA (0 to n-1)
   - **Alphabet**: Comma-separated input symbols (e.g., "a, b, c")
   - **Start State**: The initial state number
   - **Final States**: Comma-separated accepting state numbers
   - **Transitions**: One per line in format "from symbol to" (use 'e' for epsilon)

3. **Click "Convert to DFA"** to process your NFA

4. **View Results:**
   - **NFA Diagram**: Original non-deterministic automaton
   - **DFA Diagram**: Deterministic automaton from subset construction
   - **Minimized DFA Diagram**: Optimized DFA with minimal states
   - **JSON Data**: Expand "View JSON Data" to see automaton details

5. **Navigate Diagrams:**
   - **Zoom**: Use mouse wheel to zoom in/out (50% to 1000%)
   - **Pan**: Click and drag to move around the diagram
   - **Fullscreen**: Click "Fullscreen" for detailed inspection
   - **Reset**: Click "Reset View" to return to original position

### Example

Click the "Load Example" button to populate the form with a sample NFA:
- 5 states (0, 1, 2, 3, 4)
- Alphabet: {a, b, c}
- Start state: 0
- Final state: 4
- Transitions:
  - 0 --a--> 0
  - 0 --b--> 0
  - 0 --c--> 0
  - 0 --e--> 1 (epsilon transition)
  - 0 --e--> 2 (epsilon transition)
  - 1 --a--> 3
  - 2 --b--> 3
  - 3 --c--> 4
  - 4 --a--> 4
  - 4 --b--> 4
  - 4 --c--> 4

## 🔧 How It Works

1. **User Input**: React frontend collects NFA data through a form
2. **API Request**: Frontend sends data to FastAPI backend via REST API
3. **C++ Conversion**: Backend calls C++ program to perform subset construction (NFA → DFA)
4. **JSON Export**: C++ program exports both NFA and DFA as JSON files
5. **DFA Minimization**: Python script applies table-filling algorithm to minimize DFA
6. **Diagram Generation**: Python script uses Graphviz to create .dot files for all three automata
7. **SVG Rendering**: Server-side Graphviz converts .dot files to SVG images
8. **Display**: Frontend renders SVG images with interactive navigation controls

## 🛠️ Technology Stack

- **Frontend**: 
  - React 18.2.0
  - Vite 5.0.8
  - Native fetch API (no axios)
  - CSS3 with modern gradients, glassmorphism, and responsive design
  - useCallback and useEffect optimization for performance

- **Backend**: 
  - FastAPI (modern async web framework)
  - Uvicorn (ASGI server)
  - Python 3.7+
  - Secure subprocess calls (no shell=True)

- **Conversion**: 
  - C++17 with subset construction algorithm
  - Python with table-filling algorithm for minimization

- **Visualization**: 
  - Python Graphviz library
  - Server-side SVG rendering
  - Native Graphviz installation
  - Interactive SVG manipulation (zoom, pan, fullscreen)

## 📝 Input Format

The NFA input follows this format:

```
Number of states: n
Alphabet size: m
Alphabet symbols: s1 s2 ... sm
Start state: start
Number of final states: f
Final states: fs1 fs2 ... fsf
Number of transitions: t
Transitions (t lines):
  from symbol to
  from symbol to
  ...
```

Example:
```
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
```

## 📚 Example NFA Inputs

### NFA with Epsilon Transitions (3 Alphabets)
```
Number of States: 5
Alphabet: a, b, c
Start State: 0
Final States: 4
Transitions:
0 a 0
0 b 0
0 c 0
0 e 1
0 e 2
1 a 3
2 b 3
3 c 4
4 a 4
4 b 4
4 c 4
```

### Simple NFA
```
Number of States: 3
Alphabet: a, b
Start State: 0
Final States: 2
Transitions:
0 a 0
0 b 0
0 a 1
1 b 2
```

### NFA with Epsilon Transitions (2 Alphabets)
```
Number of States: 4
Alphabet: a, b
Start State: 0
Final States: 3
Transitions:
0 a 0
0 b 0
0 e 1
0 e 2
1 a 3
2 b 3
3 a 3
3 b 3
```

### Regular Expression (a+b)*ab(a+b)*
```
Number of States: 3
Alphabet: a, b
Start State: 0
Final States: 2
Transitions:
0 a 0
0 b 0
0 a 1
1 b 2
2 a 2
2 b 2
```

## � Deployment

This project is ready for deployment to Render.com with full Docker support and configuration files included.

### Quick Deployment Guide

1. **Prepare your repository**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Render.com**:
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and deploy both services

3. **Configuration files included**:
   - `backend/Dockerfile` - Docker configuration for backend
   - `render.yaml` - Render.com deployment configuration
   - `backend/.env.example` - Backend environment variables template
   - `frontend/.env.example` - Frontend environment variables template

### Detailed Instructions

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions, including:
- Step-by-step Render.com setup
- Environment variable configuration
- Troubleshooting common issues
- CI/CD with automatic deployments
- Custom domain setup

### Deployment Architecture

```
Frontend (Render Static Site)
    ↓ API calls
Backend (Render Web Service - Docker)
    ├── FastAPI server
    ├── C++ NFA→DFA converter
    ├── Python DFA minimization
    └── Graphviz diagram generation
```

### Cost

- **Free tier**: $0/month (750 hours backend, unlimited frontend)
- **Always-on backend**: $7/month (optional upgrade)

## �🐛 Troubleshooting

### Backend Issues

- **C++ executable not found**: Ensure the compiled executable exists in `backend/cpp/`
- **Python script errors**: Check that Graphviz is installed (`pip install graphviz`)
- **Graphviz not found**: Install Graphviz system-wide (e.g., `choco install graphviz` on Windows)
- **Port already in use**: Kill process on port 5000 or change port in startup command

### Frontend Issues

- **Dependencies not installing**: Clear npm cache with `npm cache clean --force`
- **API connection errors**: Ensure backend is running on port 5000
- **Blank diagrams**: Check browser console for errors, verify backend is processing correctly

### Diagram Rendering Issues

- **Invalid .dot format**: Verify Python script executed successfully
- **Missing transitions**: Ensure all NFA transitions are properly defined
- **SVG not rendering**: Check that Graphviz is installed and accessible in PATH

## 📄 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📚 Algorithm Details

### Subset Construction Algorithm (NFA → DFA)
1. Compute epsilon-closure of NFA start state
2. For each DFA state and input symbol, compute the set of reachable NFA states
3. Apply epsilon-closure to the result
4. Create new DFA states for unique state sets
5. Mark states containing NFA final states as DFA final states

### Table-Filling Algorithm (DFA Minimization)
1. Initialize: Mark all pairs of final and non-final states as distinguishable
2. Iteratively mark pairs that lead to distinguishable states
3. Group equivalent states that are not distinguishable
4. Create minimized DFA from state groups
5. Preserve start state and final states in minimized version

These algorithms ensure the resulting DFA is equivalent to the original NFA while being deterministic and minimal.
