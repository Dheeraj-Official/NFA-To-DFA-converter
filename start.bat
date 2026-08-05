@echo off
echo Starting NFA to DFA Converter Application...
echo.

echo Starting Backend Server...
start cmd /k "cd backend && python app.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting Frontend Development Server...
start cmd /k "cd frontend && npm run dev"

echo.
echo Application is starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
