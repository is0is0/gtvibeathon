"""
WebSocket Manager for Voxel API
Handles real-time communication with clients for generation progress updates.
"""

import json
import asyncio
from typing import Dict, Set, Optional, Any
from datetime import datetime
import logging

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections for real-time updates.
    Supports broadcasting messages to specific project subscribers.
    """

    def __init__(self):
        """Initialize WebSocket manager."""
        # Active connections: {project_id: {websocket1, websocket2, ...}}
        self.active_connections: Dict[str, Set[WebSocket]] = {}

        # Connection metadata: {websocket: {project_id, user_id, connected_at}}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

        logger.info("WebSocketManager initialized")

    # ==================== CONNECTION MANAGEMENT ====================

    async def connect(
        self,
        websocket: WebSocket,
        project_id: str,
        user_id: Optional[str] = None,
    ):
        """
        Accept a WebSocket connection and register it.

        Args:
            websocket: WebSocket connection
            project_id: Project to subscribe to
            user_id: User identifier (optional)
        """
        await websocket.accept()

        # Add to active connections
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()

        self.active_connections[project_id].add(websocket)

        # Store metadata
        self.connection_metadata[websocket] = {
            "project_id": project_id,
            "user_id": user_id,
            "connected_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"WebSocket connected: project={project_id}, "
            f"connections={len(self.active_connections[project_id])}"
        )

        # Send connection confirmation
        await self.send_personal_message(
            websocket,
            {
                "type": "connected",
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to generation updates",
            },
        )

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket to disconnect
        """
        if websocket not in self.connection_metadata:
            return

        metadata = self.connection_metadata[websocket]
        project_id = metadata["project_id"]

        # Remove from active connections
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)

            # Clean up empty project sets
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

        # Remove metadata
        del self.connection_metadata[websocket]

        logger.info(f"WebSocket disconnected: project={project_id}")

    def get_connection_count(self, project_id: str) -> int:
        """
        Get number of active connections for a project.

        Args:
            project_id: Project identifier

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(project_id, set()))

    def get_total_connections(self) -> int:
        """Get total number of active connections."""
        return sum(len(connections) for connections in self.active_connections.values())

    # ==================== MESSAGE SENDING ====================

    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send a message to a specific WebSocket connection.

        Args:
            websocket: Target WebSocket
            message: Message dictionary
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)

    async def broadcast_to_project(self, project_id: str, message: Dict[str, Any]):
        """
        Broadcast a message to all connections subscribed to a project.

        Args:
            project_id: Project identifier
            message: Message dictionary to broadcast
        """
        if project_id not in self.active_connections:
            logger.debug(f"No connections for project {project_id}")
            return

        connections = self.active_connections[project_id].copy()  # Copy to avoid modification during iteration
        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to WebSocket: {e}")
                disconnected.append(websocket)

        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)

        logger.debug(
            f"Broadcast to project {project_id}: {len(connections)} connections, "
            f"{len(disconnected)} failed"
        )

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """
        Broadcast a message to all active connections.

        Args:
            message: Message dictionary
        """
        total = 0
        for project_id in list(self.active_connections.keys()):
            await self.broadcast_to_project(project_id, message)
            total += len(self.active_connections.get(project_id, set()))

        logger.info(f"Broadcast to all: {total} connections")

    # ==================== GENERATION UPDATES ====================

    async def send_stage_update(
        self,
        project_id: str,
        stage: str,
        status: str,
        progress: float,
        message: Optional[str] = None,
    ):
        """
        Send a generation stage update.

        Args:
            project_id: Project identifier
            stage: Stage name (e.g., "concept", "builder", "texture")
            status: Status (pending, processing, completed, failed)
            progress: Progress percentage (0.0 to 1.0)
            message: Optional status message
        """
        update = {
            "type": "stage_update",
            "project_id": project_id,
            "stage": stage,
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.broadcast_to_project(project_id, update)

    async def send_progress_update(
        self,
        project_id: str,
        progress: float,
        current_stage: Optional[str] = None,
        message: Optional[str] = None,
    ):
        """
        Send an overall progress update.

        Args:
            project_id: Project identifier
            progress: Overall progress (0.0 to 1.0)
            current_stage: Current stage name
            message: Progress message
        """
        update = {
            "type": "progress",
            "project_id": project_id,
            "progress": progress,
            "current_stage": current_stage,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.broadcast_to_project(project_id, update)

    async def send_asset_generated(
        self,
        project_id: str,
        asset_type: str,
        filename: str,
        url: str,
        preview_url: Optional[str] = None,
    ):
        """
        Notify that an asset has been generated.

        Args:
            project_id: Project identifier
            asset_type: Type of asset (render, model, script, etc.)
            filename: Asset filename
            url: Download URL
            preview_url: Preview image URL (optional)
        """
        update = {
            "type": "asset_generated",
            "project_id": project_id,
            "asset": {
                "asset_type": asset_type,
                "filename": filename,
                "url": url,
                "preview_url": preview_url,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.broadcast_to_project(project_id, update)

    async def send_generation_complete(
        self,
        project_id: str,
        assets: list,
        total_time: Optional[float] = None,
    ):
        """
        Notify that generation is complete.

        Args:
            project_id: Project identifier
            assets: List of generated assets
            total_time: Total generation time in seconds
        """
        update = {
            "type": "complete",
            "project_id": project_id,
            "status": "completed",
            "assets": assets,
            "total_time": total_time,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Generation completed successfully!",
        }

        await self.broadcast_to_project(project_id, update)

    async def send_generation_error(
        self,
        project_id: str,
        error_message: str,
        stage: Optional[str] = None,
    ):
        """
        Notify that an error occurred.

        Args:
            project_id: Project identifier
            error_message: Error description
            stage: Stage where error occurred
        """
        update = {
            "type": "error",
            "project_id": project_id,
            "status": "failed",
            "error": error_message,
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.broadcast_to_project(project_id, update)

    # ==================== HEARTBEAT ====================

    async def send_heartbeat(self, websocket: WebSocket):
        """
        Send a heartbeat message to keep connection alive.

        Args:
            websocket: Target WebSocket
        """
        try:
            await self.send_personal_message(
                websocket,
                {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
        except Exception:
            self.disconnect(websocket)

    async def heartbeat_loop(self, websocket: WebSocket, interval: int = 30):
        """
        Continuously send heartbeats to a connection.

        Args:
            websocket: Target WebSocket
            interval: Heartbeat interval in seconds
        """
        try:
            while websocket in self.connection_metadata:
                await asyncio.sleep(interval)
                await self.send_heartbeat(websocket)
        except WebSocketDisconnect:
            self.disconnect(websocket)
        except Exception as e:
            logger.error(f"Heartbeat loop error: {e}")
            self.disconnect(websocket)

    # ==================== STATISTICS ====================

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get WebSocket statistics.

        Returns:
            Dictionary with connection statistics
        """
        return {
            "total_connections": self.get_total_connections(),
            "active_projects": len(self.active_connections),
            "projects": {
                project_id: len(connections)
                for project_id, connections in self.active_connections.items()
            },
        }


# ==================== FASTAPI WEBSOCKET HANDLER ====================

async def handle_websocket_connection(
    websocket: WebSocket,
    project_id: str,
    ws_manager: WebSocketManager,
    user_id: Optional[str] = None,
):
    """
    Handle a WebSocket connection lifecycle.

    Args:
        websocket: WebSocket connection
        project_id: Project to subscribe to
        ws_manager: WebSocketManager instance
        user_id: User identifier (optional)

    Usage in FastAPI:
        @app.websocket("/api/ws/generation/{project_id}")
        async def websocket_endpoint(websocket: WebSocket, project_id: str):
            await handle_websocket_connection(websocket, project_id, ws_manager)
    """
    await ws_manager.connect(websocket, project_id, user_id)

    try:
        # Start heartbeat in background
        heartbeat_task = asyncio.create_task(ws_manager.heartbeat_loop(websocket))

        # Listen for client messages (optional - mainly for receiving control messages)
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle client messages if needed
                msg_type = message.get("type")

                if msg_type == "ping":
                    await ws_manager.send_personal_message(
                        websocket,
                        {
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )
                elif msg_type == "subscribe":
                    # Could support subscribing to additional projects
                    pass

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON from WebSocket")
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                break

    finally:
        # Cleanup
        heartbeat_task.cancel()
        ws_manager.disconnect(websocket)


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    import asyncio

    async def demo():
        """Demonstrate WebSocket manager usage."""
        logging.basicConfig(level=logging.INFO)

        ws_manager = WebSocketManager()

        # Simulate connection (in real usage, this would be a FastAPI WebSocket)
        class MockWebSocket:
            def __init__(self, name):
                self.name = name
                self.messages = []

            async def accept(self):
                pass

            async def send_json(self, data):
                self.messages.append(data)
                print(f"[{self.name}] Received: {data}")

        # Create mock connections
        ws1 = MockWebSocket("Client1")
        ws2 = MockWebSocket("Client2")

        # Connect clients
        await ws_manager.connect(ws1, "project_123", "user_1")
        await ws_manager.connect(ws2, "project_123", "user_2")

        print(f"\nTotal connections: {ws_manager.get_total_connections()}")
        print(f"Project connections: {ws_manager.get_connection_count('project_123')}")

        # Send stage updates
        await ws_manager.send_stage_update(
            "project_123",
            stage="concept",
            status="processing",
            progress=0.2,
            message="Analyzing prompt...",
        )

        await asyncio.sleep(0.1)

        await ws_manager.send_progress_update(
            "project_123",
            progress=0.5,
            current_stage="builder",
            message="Creating 3D geometry...",
        )

        await asyncio.sleep(0.1)

        # Notify asset generated
        await ws_manager.send_asset_generated(
            "project_123",
            asset_type="render",
            filename="final_render.png",
            url="/api/projects/project_123/assets/final_render.png",
        )

        await asyncio.sleep(0.1)

        # Complete generation
        await ws_manager.send_generation_complete(
            "project_123",
            assets=[
                {
                    "asset_type": "render",
                    "filename": "final_render.png",
                    "url": "/api/projects/project_123/assets/final_render.png",
                }
            ],
            total_time=45.2,
        )

        # Get statistics
        stats = ws_manager.get_statistics()
        print(f"\nStatistics: {stats}")

        # Disconnect
        ws_manager.disconnect(ws1)
        ws_manager.disconnect(ws2)

        print(f"\nConnections after disconnect: {ws_manager.get_total_connections()}")

    # Run demo
    asyncio.run(demo())
