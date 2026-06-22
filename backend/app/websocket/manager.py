"""
WebSocket connection manager for real-time updates
"""
import json
import logging
from datetime import datetime
from typing import Set, Optional, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_filters: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_filters[websocket] = {}
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
        
        # Send connection confirmed message
        await websocket.send_json({
            "type": "connection:established",
            "timestamp": datetime.utcnow().isoformat(),
            "active_connections": len(self.active_connections)
        })
    
    def disconnect(self, websocket: WebSocket):
        """Unregister a disconnected WebSocket"""
        self.active_connections.discard(websocket)
        self.connection_filters.pop(websocket, None)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def set_filters(self, websocket: WebSocket, filters: Dict[str, Any]):
        """Set filters for a connection"""
        self.connection_filters[websocket] = filters
        logger.debug(f"Filters set for connection: {filters}")
    
    def _matches_filters(self, event: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if an event matches the connection's filters"""
        if not filters:
            return True
        
        # Check each filter
        if "severity" in filters and "data" in event:
            event_severity = event["data"].get("severity")
            if event_severity and event_severity not in filters["severity"]:
                return False
        
        if "countries" in filters and "data" in event:
            event_country = event["data"].get("country_code")
            if event_country and event_country not in filters["countries"]:
                return False
        
        if "event_types" in filters and "data" in event:
            event_type = event["data"].get("event_type")
            if event_type and event_type not in filters["event_types"]:
                return False
        
        return True
    
    async def broadcast(self, event: Dict[str, Any]):
        """
        Broadcast an event to all connected clients that match filters
        """
        disconnected_clients = []
        
        for websocket, filters in list(self.connection_filters.items()):
            # Check if event matches this connection's filters
            if not self._matches_filters(event, filters):
                continue
            
            try:
                # Add timestamp if not present
                if "timestamp" not in event:
                    event["timestamp"] = datetime.utcnow().isoformat()
                
                await websocket.send_json(event)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected_clients:
            self.disconnect(websocket)
    
    async def broadcast_attack(self, attack_data: Dict[str, Any]):
        """Broadcast a new attack event"""
        event = {
            "type": "attack:new",
            "data": attack_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(event)
    
    async def broadcast_session_update(self, session_data: Dict[str, Any]):
        """Broadcast a session update"""
        event = {
            "type": "session:update",
            "data": session_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(event)
    
    async def broadcast_stats_update(self, stats_data: Dict[str, Any]):
        """Broadcast statistics update"""
        event = {
            "type": "stats:update",
            "data": stats_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(event)
    
    async def handle_client_message(
        self,
        websocket: WebSocket,
        message: Dict[str, Any]
    ):
        """
        Handle incoming WebSocket messages from clients
        """
        message_type = message.get("type")
        
        if message_type == "subscribe:attacks":
            filters = message.get("filters", {})
            await self.set_filters(websocket, filters)
            
            await websocket.send_json({
                "type": "subscription:confirmed",
                "subscription": "attacks",
                "filters": filters
            })
        
        elif message_type == "subscribe:stats":
            await websocket.send_json({
                "type": "subscription:confirmed",
                "subscription": "stats"
            })
        
        elif message_type == "unsubscribe:attacks":
            await self.set_filters(websocket, {})
            
            await websocket.send_json({
                "type": "subscription:cancelled",
                "subscription": "attacks"
            })
        
        elif message_type == "ping":
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about active connections"""
        return {
            "total_connections": len(self.active_connections),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global manager instance
manager = ConnectionManager()
