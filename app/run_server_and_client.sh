#!/bin/bash
# Start the FastAPI server
cd server
uvicorn main:app --reload &
SERVER_PID=$!
cd ../client
# Wait a bit to ensure the server is up
sleep 2
npm start &
CLIENT_PID=$!

# Wait for both processes
wait $SERVER_PID $CLIENT_PID 