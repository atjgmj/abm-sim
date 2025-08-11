#!/bin/bash

# ABM Communication Campaign Simulator Launcher

echo "Starting ABM Communication Campaign Simulator..."

# Kill existing processes
echo "Cleaning up existing processes..."
pkill -f "run_backend.py" 2>/dev/null || true
pkill -f "pnpm dev" 2>/dev/null || true
sleep 2

# Start backend
echo "Starting backend server on port 8000..."
python3 run_backend.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "Backend ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Backend failed to start. Check backend.log for details."
        exit 1
    fi
    sleep 1
done

# Start frontend
echo "Starting frontend server on port 5173..."
cd frontend && pnpm dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
echo "Waiting for frontend to start..."
for i in {1..30}; do
    if curl -s http://localhost:5173/ > /dev/null 2>&1; then
        echo "Frontend ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Frontend failed to start. Check frontend.log for details."
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎉 ABM Simulator is now running!"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait and handle shutdown
trap 'echo "Shutting down..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' SIGINT SIGTERM

# Keep script running
while true; do
    sleep 1
done