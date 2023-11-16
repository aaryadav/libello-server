import asyncio
import json
from typing import Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect, APIRouter

router = APIRouter()

# This global dictionary will hold active WebSocket connections for status updates
active_connections: Dict[str, WebSocket] = {}

async def send_status_update(user_id: str, container_id: str, status: str):
    # Construct the message to send
    message = json.dumps({
        "container_id": container_id,
        "status": status,
    })
    # Check if the user has an active WebSocket connection
    if user_id in active_connections:
        # Send the update
        await active_connections[user_id].send_text(message)

@router.websocket("/ws/status/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    # Store the WebSocket connection in the global dictionary
    active_connections[user_id] = websocket
    try:
        while True:
            # Wait for a message from the client (if necessary)
            # For status updates, we may not need to receive messages from the client
            # _ = await websocket.receive_text()

            # Here you would have logic that determines when to send a status update
            # For example, a background task could check Redis for updates and use send_status_update
            # to send them to the WebSocket. For now, we'll just sleep.
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        # Remove the WebSocket connection if it gets disconnected
        active_connections.pop(user_id, None)
