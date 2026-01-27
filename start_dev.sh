#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping all services..."
    kill $(jobs -p) 2>/dev/null
    exit
}
trap cleanup SIGINT SIGTERM

echo "Starting Jinder Development Environment..."

# Backend Setup & Run
echo "-----------------------------------------------------"
echo "Setting up Backend..."
echo "-----------------------------------------------------"
cd backend

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment exists."
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing/Updating backend dependencies..."
pip install -r requirements.txt

# Start Backend Server
echo "Starting Backend Server..."
uvicorn app.main:app --reload &
BACKEND_PID=$!
cd ..

# Frontend Setup & Run
echo "-----------------------------------------------------"
echo "Setting up Frontend..."
echo "-----------------------------------------------------"
cd frontend

# Install dependencies
echo "Installing/Updating frontend dependencies..."
npm install

# Start Frontend Server
echo "Starting Frontend Server..."
ng serve &
FRONTEND_PID=$!
cd ..

# Wait a moment for services to initialize (optional, but good for output clarity)
sleep 5

echo "-----------------------------------------------------"
echo "JINDER IS RUNNING!"
echo "-----------------------------------------------------"
echo "Backend API:   http://localhost:8000"
echo "Frontend App:  http://localhost:4200"
echo ""
echo "👉 Navigate to http://localhost:4200 to use the app"
echo ""
echo "Press Ctrl+C to stop all services."
echo "-----------------------------------------------------"

# Wait for background processes
wait
