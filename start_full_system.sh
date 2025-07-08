#!/bin/bash
#
# This script orchestrates the startup of the entire application,
# including the virtual display, backend server, ngrok tunnel, and automation client.
#

# --- Configuration ---
XVFB_DISPLAY=":99"
VNC_PORT="5900"
NGROK_AUTH_TOKEN="${NGROK_AUTH_TOKEN}" # Make sure to set this environment variable

# --- Cleanup previous runs ---
echo "--- Cleaning up previous processes ---"
pkill -f x11vnc
pkill -f ngrok
pkill -f Xvfb
pkill -f api_bridge_with_database.py
pkill -f ai_job_automation.py
sleep 2

# --- Start Virtual Display (Xvfb) ---
echo "--- Starting Virtual Display (Xvfb) on display ${XVFB_DISPLAY} ---"
Xvfb ${XVFB_DISPLAY} -screen 0 1280x1024x24 &
export DISPLAY=${XVFB_DISPLAY}
sleep 2

# --- Start VNC Server to view the virtual display ---
echo "--- Starting VNC Server on port ${VNC_PORT} ---"
x11vnc -display ${XVFB_DISPLAY} -ncache 10 -forever -shared -bg -rfbport ${VNC_PORT}
sleep 2

# --- Start ngrok Tunnel ---
echo "--- Starting ngrok tunnel to VNC port ${VNC_PORT} ---"
if [ -z "${NGROK_AUTH_TOKEN}" ]; then
    echo "ERROR: NGROK_AUTH_TOKEN is not set. Please set it and re-run."
    exit 1
fi
ngrok authtoken ${NGROK_AUTH_TOKEN}
ngrok tcp ${VNC_PORT} > ngrok.log 2>&1 &
sleep 5 # Give ngrok time to start up

# --- Get ngrok URL ---
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r ".tunnels[0].public_url")
if [ -z "${NGROK_URL}" ] || [ "${NGROK_URL}" == "null" ]; then
    echo "--- Could not get ngrok URL. Here is the log: ---"
    cat ngrok.log
    exit 1
fi
echo "------------------------------------------------------------------"
echo "--- Your virtual desktop is ready! ---"
echo "--- Connect with a VNC client to: ${NGROK_URL} ---"
echo "--- You will see a browser window open. Please log in. ---"
echo "------------------------------------------------------------------"


# --- Start the Backend Server ---
echo "--- Starting Backend Server (api_bridge_with_database.py) ---"
python3 api_bridge_with_database.py &
API_BRIDGE_PID=$!
sleep 5 # Give the server time to start

# --- Run the Automation Script ---
echo "--- Starting the Automation Script (ai_job_automation.py) ---"
python3 ai_job_automation.py

# --- Final Cleanup ---
echo "--- Automation finished. Cleaning up all processes. ---"
kill $API_BRIDGE_PID
pkill -f x11vnc
pkill -f ngrok
pkill -f Xvfb