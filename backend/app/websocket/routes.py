"""
WebSocket endpoint
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

from app.websocket.manager import manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time attack updates
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle the message
            await manager.handle_client_message(websocket, message)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON received on WebSocket")
        await websocket.send_json({
            "type": "error",
            "message": "Invalid JSON format"
        })
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
