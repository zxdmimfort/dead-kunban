#!/bin/bash
(cd backend && fastapi dev src) &
BACKEND_PID=$!

(cd frontend && npm run dev) &
FRONTEND_PID=$!

wait $BACKEND_PID $FRONTEND_PID