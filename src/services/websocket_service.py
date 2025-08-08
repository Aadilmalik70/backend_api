"""
WebSocket Service - Real-time communication for blueprint generation.

This service handles WebSocket connections and provides real-time progress updates
during blueprint generation processes.
"""

import logging
import json
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketService:
    """
    Service for managing WebSocket connections and real-time communication
    during blueprint generation processes.
    """
    
    def __init__(self, socketio: SocketIO):
        """
        Initialize the WebSocket service.
        
        Args:
            socketio: Flask-SocketIO instance
        """
        self.socketio = socketio
        self.active_sessions = {}  # Track active blueprint generation sessions
        
        # Register event handlers
        self._register_handlers()
        
        logger.info("WebSocket service initialized successfully")
    
    def _register_handlers(self):
        """Register WebSocket event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            client_id = request.sid
            user_id = request.args.get('user_id', 'anonymous')
            
            logger.info(f"Client connected: {client_id} (user: {user_id})")
            
            # Send connection confirmation
            emit('connection_status', {
                'status': 'connected',
                'client_id': client_id,
                'timestamp': datetime.utcnow().isoformat(),
                'server': 'SERP Strategist API'
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            client_id = request.sid
            
            # Clean up any active sessions for this client
            sessions_to_remove = []
            for blueprint_id, session_info in self.active_sessions.items():
                if session_info.get('client_id') == client_id:
                    sessions_to_remove.append(blueprint_id)
            
            for blueprint_id in sessions_to_remove:
                del self.active_sessions[blueprint_id]
                logger.info(f"Cleaned up session for blueprint: {blueprint_id}")
            
            logger.info(f"Client disconnected: {client_id}")
        
        @self.socketio.on('join_blueprint_room')
        def handle_join_blueprint_room(data):
            """Handle client joining a blueprint generation room."""
            client_id = request.sid
            blueprint_id = data.get('blueprint_id')
            user_id = data.get('user_id', 'anonymous')
            
            if not blueprint_id:
                emit('error', {'message': 'Blueprint ID is required'})
                return
            
            # Join the room for this blueprint
            room = f"blueprint_{blueprint_id}"
            join_room(room)
            
            logger.info(f"Client {client_id} joined room: {room} (user: {user_id})")
            
            # Send confirmation
            emit('room_joined', {
                'blueprint_id': blueprint_id,
                'room': room,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # If there's an active session, send current status
            if blueprint_id in self.active_sessions:
                session = self.active_sessions[blueprint_id]
                emit('progress_update', {
                    'blueprint_id': blueprint_id,
                    'step': session.get('current_step', 'unknown'),
                    'progress': session.get('progress', 0),
                    'status': session.get('status', 'in_progress'),
                    'message': session.get('current_message', 'Processing...'),
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        @self.socketio.on('leave_blueprint_room')
        def handle_leave_blueprint_room(data):
            """Handle client leaving a blueprint generation room."""
            client_id = request.sid
            blueprint_id = data.get('blueprint_id')
            
            if not blueprint_id:
                emit('error', {'message': 'Blueprint ID is required'})
                return
            
            # Leave the room
            room = f"blueprint_{blueprint_id}"
            leave_room(room)
            
            logger.info(f"Client {client_id} left room: {room}")
            
            # Send confirmation
            emit('room_left', {
                'blueprint_id': blueprint_id,
                'room': room,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        @self.socketio.on('ping')
        def handle_ping():
            """Handle ping for connection testing."""
            emit('pong', {
                'timestamp': datetime.utcnow().isoformat(),
                'server_time': time.time()
            })
    
    def start_blueprint_session(self, blueprint_id: str, user_id: str, 
                               total_steps: int = 6) -> None:
        """
        Start a new blueprint generation session.
        
        Args:
            blueprint_id: Unique identifier for the blueprint
            user_id: ID of the user requesting the blueprint
            total_steps: Total number of steps in the generation process
        """
        session_info = {
            'blueprint_id': blueprint_id,
            'user_id': user_id,
            'total_steps': total_steps,
            'current_step': 0,
            'progress': 0,
            'status': 'started',
            'started_at': datetime.utcnow().isoformat(),
            'current_message': 'Starting blueprint generation...'
        }
        
        self.active_sessions[blueprint_id] = session_info
        
        # Notify clients in the blueprint room
        room = f"blueprint_{blueprint_id}"
        self.socketio.emit('generation_started', {
            'blueprint_id': blueprint_id,
            'total_steps': total_steps,
            'status': 'started',
            'message': 'Blueprint generation started',
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
        
        logger.info(f"Started blueprint session: {blueprint_id} (user: {user_id})")
    
    def update_progress(self, blueprint_id: str, step: int, step_name: str, 
                       message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Update progress for a blueprint generation session.
        
        Args:
            blueprint_id: Blueprint identifier
            step: Current step number (1-based)
            step_name: Name of the current step
            message: Progress message
            details: Optional additional details
        """
        if blueprint_id not in self.active_sessions:
            logger.warning(f"No active session found for blueprint: {blueprint_id}")
            return
        
        session = self.active_sessions[blueprint_id]
        total_steps = session['total_steps']
        progress = min(100, int((step / total_steps) * 100))
        
        # Update session info
        session.update({
            'current_step': step,
            'progress': progress,
            'status': 'in_progress',
            'current_message': message,
            'step_name': step_name,
            'last_updated': datetime.utcnow().isoformat()
        })
        
        # Prepare progress data
        progress_data = {
            'blueprint_id': blueprint_id,
            'step': step,
            'step_name': step_name,
            'total_steps': total_steps,
            'progress': progress,
            'status': 'in_progress',
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add details if provided
        if details:
            progress_data['details'] = details
        
        # Emit to clients in the blueprint room
        room = f"blueprint_{blueprint_id}"
        self.socketio.emit('progress_update', progress_data, room=room)
        
        logger.info(f"Progress update for {blueprint_id}: Step {step}/{total_steps} - {message}")
    
    def complete_step(self, blueprint_id: str, step: int, step_name: str, 
                     result: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark a step as completed.
        
        Args:
            blueprint_id: Blueprint identifier
            step: Step number that was completed
            step_name: Name of the completed step
            result: Optional step result data
        """
        if blueprint_id not in self.active_sessions:
            logger.warning(f"No active session found for blueprint: {blueprint_id}")
            return
        
        session = self.active_sessions[blueprint_id]
        
        # Prepare completion data
        completion_data = {
            'blueprint_id': blueprint_id,
            'step': step,
            'step_name': step_name,
            'status': 'completed',
            'message': f'Completed: {step_name}',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add result if provided
        if result:
            completion_data['result'] = result
        
        # Emit to clients in the blueprint room
        room = f"blueprint_{blueprint_id}"
        self.socketio.emit('step_completed', completion_data, room=room)
        
        logger.info(f"Step completed for {blueprint_id}: {step_name}")
    
    def complete_generation(self, blueprint_id: str, blueprint_data: Dict[str, Any],
                           generation_time: int) -> None:
        """
        Mark blueprint generation as completed.
        
        Args:
            blueprint_id: Blueprint identifier
            blueprint_data: Generated blueprint data
            generation_time: Total generation time in seconds
        """
        if blueprint_id not in self.active_sessions:
            logger.warning(f"No active session found for blueprint: {blueprint_id}")
            return
        
        session = self.active_sessions[blueprint_id]
        
        # Update session status
        session.update({
            'status': 'completed',
            'progress': 100,
            'completed_at': datetime.utcnow().isoformat(),
            'generation_time': generation_time,
            'current_message': 'Blueprint generation completed successfully'
        })
        
        # Prepare completion data
        completion_data = {
            'blueprint_id': blueprint_id,
            'status': 'completed',
            'progress': 100,
            'message': 'Blueprint generation completed successfully',
            'generation_time': generation_time,
            'blueprint_data': blueprint_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Emit to clients in the blueprint room
        room = f"blueprint_{blueprint_id}"
        self.socketio.emit('generation_complete', completion_data, room=room)
        
        logger.info(f"Blueprint generation completed: {blueprint_id} in {generation_time}s")
        
        # Clean up session after a delay (keep for a short time for reconnections)
        def cleanup_session():
            if blueprint_id in self.active_sessions:
                del self.active_sessions[blueprint_id]
                logger.info(f"Cleaned up completed session: {blueprint_id}")
        
        # Schedule cleanup after 5 minutes
        self.socketio.start_background_task(target=lambda: (
            self.socketio.sleep(300), cleanup_session()
        ))
    
    def fail_generation(self, blueprint_id: str, error_message: str, 
                       error_details: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark blueprint generation as failed.
        
        Args:
            blueprint_id: Blueprint identifier
            error_message: Error message
            error_details: Optional error details
        """
        if blueprint_id not in self.active_sessions:
            logger.warning(f"No active session found for blueprint: {blueprint_id}")
            return
        
        session = self.active_sessions[blueprint_id]
        
        # Update session status
        session.update({
            'status': 'failed',
            'failed_at': datetime.utcnow().isoformat(),
            'error_message': error_message,
            'current_message': f'Generation failed: {error_message}'
        })
        
        # Prepare failure data
        failure_data = {
            'blueprint_id': blueprint_id,
            'status': 'failed',
            'message': f'Blueprint generation failed: {error_message}',
            'error': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add error details if provided
        if error_details:
            failure_data['error_details'] = error_details
        
        # Emit to clients in the blueprint room
        room = f"blueprint_{blueprint_id}"
        self.socketio.emit('generation_failed', failure_data, room=room)
        
        logger.error(f"Blueprint generation failed: {blueprint_id} - {error_message}")
        
        # Clean up session after a delay
        def cleanup_session():
            if blueprint_id in self.active_sessions:
                del self.active_sessions[blueprint_id]
                logger.info(f"Cleaned up failed session: {blueprint_id}")
        
        # Schedule cleanup after 2 minutes
        self.socketio.start_background_task(target=lambda: (
            self.socketio.sleep(120), cleanup_session()
        ))
    
    def send_custom_message(self, blueprint_id: str, message_type: str, 
                           data: Dict[str, Any]) -> None:
        """
        Send a custom message to clients in a blueprint room.
        
        Args:
            blueprint_id: Blueprint identifier
            message_type: Type of message
            data: Message data
        """
        room = f"blueprint_{blueprint_id}"
        
        message_data = {
            'blueprint_id': blueprint_id,
            'type': message_type,
            'timestamp': datetime.utcnow().isoformat(),
            **data
        }
        
        self.socketio.emit('custom_message', message_data, room=room)
        logger.info(f"Custom message sent to {blueprint_id}: {message_type}")
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all active sessions.
        
        Returns:
            Dictionary of active sessions
        """
        return self.active_sessions.copy()
    
    def get_session_status(self, blueprint_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific session.
        
        Args:
            blueprint_id: Blueprint identifier
            
        Returns:
            Session status or None if not found
        """
        return self.active_sessions.get(blueprint_id)
    
    def cleanup_stale_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up stale sessions that are older than max_age_hours.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of sessions cleaned up
        """
        current_time = datetime.utcnow()
        sessions_to_remove = []
        
        for blueprint_id, session in self.active_sessions.items():
            started_at = datetime.fromisoformat(session['started_at'])
            age_hours = (current_time - started_at).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                sessions_to_remove.append(blueprint_id)
        
        for blueprint_id in sessions_to_remove:
            del self.active_sessions[blueprint_id]
            logger.info(f"Cleaned up stale session: {blueprint_id}")
        
        return len(sessions_to_remove)

# Global instance to be initialized by the application
websocket_service = None

def init_websocket_service(socketio: SocketIO) -> WebSocketService:
    """
    Initialize the global WebSocket service instance.
    
    Args:
        socketio: Flask-SocketIO instance
        
    Returns:
        WebSocket service instance
    """
    global websocket_service
    websocket_service = WebSocketService(socketio)
    return websocket_service

def get_websocket_service() -> Optional[WebSocketService]:
    """
    Get the global WebSocket service instance.
    
    Returns:
        WebSocket service instance or None if not initialized
    """
    return websocket_service