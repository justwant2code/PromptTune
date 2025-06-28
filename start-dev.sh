#!/bin/bash

# Prompt Tune MVP - Development Startup Script

echo "🚀 Starting Prompt Tune MVP Development Environment"

# Check if backend dependencies are installed
echo "📦 Checking backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start backend server
echo "🔧 Starting FastAPI backend server..."
nohup python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1 &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 5

# Check backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "🎨 Starting React frontend..."
cd ../frontend

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend development server
echo "🌐 Starting frontend development server..."
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Prompt Tune MVP is starting up!"
echo ""
echo "📍 Backend API: http://localhost:8000"
echo "📍 Frontend App: http://localhost:3000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 To stop the servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📊 Backend logs: backend/server.log"
echo ""

# Save PIDs for easy cleanup
echo "$BACKEND_PID" > ../pids.txt
echo "$FRONTEND_PID" >> ../pids.txt

echo "✨ Development environment ready!"
