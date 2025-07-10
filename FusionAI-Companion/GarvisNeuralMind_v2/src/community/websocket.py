"""
WebSocket Manager - Real-time communication for community features.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time community features."""
    
    def __init__(self):
        # Active connections: user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        
        # User rooms/channels: room_id -> Set[user_id]
        self.user_rooms: Dict[str, Set[str]] = {}
        
        # User to rooms mapping: user_id -> Set[room_id]
        self.user_to_rooms: Dict[str, Set[str]] = {}
        
        # Message handlers
        self.message_handlers = {
            "chat_message": self._handle_chat_message,
            "join_room": self._handle_join_room,
            "leave_room": self._handle_leave_room,
            "typing_indicator": self._handle_typing_indicator,
            "user_status": self._handle_user_status,
            "community_update": self._handle_community_update,
            "post_update": self._handle_post_update
        }
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a user's WebSocket."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_to_rooms[user_id] = set()
        
        logger.info(f"🔌 User {user_id} connected via WebSocket")
        
        # Send welcome message
        await self.send_personal_message(user_id, {
            "type": "connection_established",
            "message": "Welcome to GarvisNeuralMind Community!",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        })
        
        # Notify online status change
        await self.broadcast_to_all({
            "type": "user_online",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, user_id: str):
        """Disconnect a user's WebSocket."""
        if user_id in self.active_connections:
            # Remove from all rooms
            for room_id in list(self.user_to_rooms.get(user_id, [])):
                self._remove_user_from_room(user_id, room_id)
            
            # Clean up connections
            del self.active_connections[user_id]
            if user_id in self.user_to_rooms:
                del self.user_to_rooms[user_id]
            
            logger.info(f"🔌 User {user_id} disconnected")
            
            # Notify offline status change
            asyncio.create_task(self.broadcast_to_all({
                "type": "user_offline",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }))
    
    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except WebSocketDisconnect:
                self.disconnect(user_id)
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any], 
                               exclude_user: Optional[str] = None):
        """Broadcast a message to all users in a room."""
        if room_id not in self.user_rooms:
            return
        
        disconnected_users = []
        
        for user_id in self.user_rooms[room_id]:
            if exclude_user and user_id == exclude_user:
                continue
            
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].send_text(json.dumps(message))
                except (WebSocketDisconnect, Exception):
                    disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any], 
                              exclude_user: Optional[str] = None):
        """Broadcast a message to all connected users."""
        disconnected_users = []
        
        for user_id, websocket in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_text(json.dumps(message))
            except (WebSocketDisconnect, Exception):
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    async def handle_message(self, user_id: str, data: Dict[str, Any]):
        """Handle incoming WebSocket message."""
        message_type = data.get("type")
        
        if message_type in self.message_handlers:
            try:
                await self.message_handlers[message_type](user_id, data)
            except Exception as e:
                logger.error(f"Error handling message type {message_type} from {user_id}: {e}")
                await self.send_personal_message(user_id, {
                    "type": "error",
                    "message": f"Error processing {message_type}",
                    "timestamp": datetime.utcnow().isoformat()
                })
        else:
            logger.warning(f"Unknown message type: {message_type} from user {user_id}")
            await self.send_personal_message(user_id, {
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    # Message Handlers
    
    async def _handle_chat_message(self, user_id: str, data: Dict[str, Any]):
        """Handle chat message."""
        room_id = data.get("room_id")
        content = data.get("content", "").strip()
        message_type = data.get("message_type", "text")
        
        if not room_id or not content:
            await self.send_personal_message(user_id, {
                "type": "error",
                "message": "Room ID and content are required",
                "timestamp": datetime.utcnow().isoformat()
            })
            return
        
        # Validate user is in the room
        if room_id not in self.user_to_rooms.get(user_id, set()):
            await self.send_personal_message(user_id, {
                "type": "error",
                "message": "You are not in this room",
                "timestamp": datetime.utcnow().isoformat()
            })
            return
        
        # Create message object
        message = {
            "type": "chat_message",
            "room_id": room_id,
            "user_id": user_id,
            "content": content,
            "message_type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
            "message_id": f"{user_id}_{datetime.utcnow().timestamp()}"
        }
        
        # Broadcast to room
        await self.broadcast_to_room(room_id, message)
        
        logger.info(f"💬 Chat message from {user_id} in room {room_id}")
    
    async def _handle_join_room(self, user_id: str, data: Dict[str, Any]):
        """Handle user joining a room."""
        room_id = data.get("room_id")
        room_type = data.get("room_type", "community")  # community, direct_message, group
        
        if not room_id:
            await self.send_personal_message(user_id, {
                "type": "error",
                "message": "Room ID is required",
                "timestamp": datetime.utcnow().isoformat()
            })
            return
        
        # Add user to room
        if room_id not in self.user_rooms:
            self.user_rooms[room_id] = set()
        
        self.user_rooms[room_id].add(user_id)
        self.user_to_rooms[user_id].add(room_id)
        
        # Notify user
        await self.send_personal_message(user_id, {
            "type": "room_joined",
            "room_id": room_id,
            "room_type": room_type,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Notify others in room
        await self.broadcast_to_room(room_id, {
            "type": "user_joined_room",
            "room_id": room_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
        
        logger.info(f"🏠 User {user_id} joined room {room_id}")
    
    async def _handle_leave_room(self, user_id: str, data: Dict[str, Any]):
        """Handle user leaving a room."""
        room_id = data.get("room_id")
        
        if not room_id:
            return
        
        self._remove_user_from_room(user_id, room_id)
        
        # Notify user
        await self.send_personal_message(user_id, {
            "type": "room_left",
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Notify others in room
        await self.broadcast_to_room(room_id, {
            "type": "user_left_room",
            "room_id": room_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"🏠 User {user_id} left room {room_id}")
    
    async def _handle_typing_indicator(self, user_id: str, data: Dict[str, Any]):
        """Handle typing indicator."""
        room_id = data.get("room_id")
        is_typing = data.get("is_typing", False)
        
        if not room_id or room_id not in self.user_to_rooms.get(user_id, set()):
            return
        
        # Broadcast typing indicator to room
        await self.broadcast_to_room(room_id, {
            "type": "typing_indicator",
            "room_id": room_id,
            "user_id": user_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
    
    async def _handle_user_status(self, user_id: str, data: Dict[str, Any]):
        """Handle user status update."""
        status = data.get("status")  # online, away, busy, invisible
        custom_message = data.get("custom_message", "")
        
        if status not in ["online", "away", "busy", "invisible"]:
            return
        
        # Broadcast status update
        await self.broadcast_to_all({
            "type": "user_status_update",
            "user_id": user_id,
            "status": status,
            "custom_message": custom_message,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
        
        logger.info(f"📊 User {user_id} status updated to {status}")
    
    async def _handle_community_update(self, user_id: str, data: Dict[str, Any]):
        """Handle community update notifications."""
        community_id = data.get("community_id")
        update_type = data.get("update_type")  # new_post, new_member, etc.
        
        if not community_id or not update_type:
            return
        
        # Broadcast to community room
        room_id = f"community_{community_id}"
        await self.broadcast_to_room(room_id, {
            "type": "community_update",
            "community_id": community_id,
            "update_type": update_type,
            "user_id": user_id,
            "data": data.get("update_data", {}),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_post_update(self, user_id: str, data: Dict[str, Any]):
        """Handle post update notifications (votes, comments)."""
        post_id = data.get("post_id")
        update_type = data.get("update_type")  # vote, comment, edit
        
        if not post_id or not update_type:
            return
        
        # Broadcast to interested users (could be community members or post subscribers)
        await self.broadcast_to_all({
            "type": "post_update",
            "post_id": post_id,
            "update_type": update_type,
            "user_id": user_id,
            "data": data.get("update_data", {}),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _remove_user_from_room(self, user_id: str, room_id: str):
        """Remove user from a specific room."""
        if room_id in self.user_rooms and user_id in self.user_rooms[room_id]:
            self.user_rooms[room_id].remove(user_id)
            
            # Clean up empty rooms
            if not self.user_rooms[room_id]:
                del self.user_rooms[room_id]
        
        if user_id in self.user_to_rooms and room_id in self.user_to_rooms[user_id]:
            self.user_to_rooms[user_id].remove(room_id)
    
    # Utility methods for external use
    
    def get_online_users(self) -> List[str]:
        """Get list of online user IDs."""
        return list(self.active_connections.keys())
    
    def get_room_users(self, room_id: str) -> List[str]:
        """Get list of user IDs in a specific room."""
        return list(self.user_rooms.get(room_id, set()))
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if a user is online."""
        return user_id in self.active_connections
    
    def get_user_rooms(self, user_id: str) -> List[str]:
        """Get list of rooms a user is in."""
        return list(self.user_to_rooms.get(user_id, set()))
    
    async def notify_new_post(self, community_id: int, post_data: Dict[str, Any]):
        """Notify community members about a new post."""
        room_id = f"community_{community_id}"
        await self.broadcast_to_room(room_id, {
            "type": "new_post",
            "community_id": community_id,
            "post": post_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def notify_new_comment(self, post_id: int, comment_data: Dict[str, Any]):
        """Notify about a new comment on a post."""
        await self.broadcast_to_all({
            "type": "new_comment",
            "post_id": post_id,
            "comment": comment_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def notify_user_level_up(self, user_id: str, new_level: int):
        """Notify about user level up."""
        await self.send_personal_message(user_id, {
            "type": "level_up",
            "new_level": new_level,
            "message": f"Congratulations! You reached level {new_level}!",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Also broadcast to user's communities
        for room_id in self.user_to_rooms.get(user_id, set()):
            await self.broadcast_to_room(room_id, {
                "type": "user_achievement",
                "user_id": user_id,
                "achievement_type": "level_up",
                "new_level": new_level,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user=user_id)