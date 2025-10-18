#!/usr/bin/env python3
"""
Voxel API Server Startup Script
Start the Flask + SocketIO server for the Framer frontend.
"""

import logging
from voxel.web.app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting Voxel API server...")

    # Create Flask app
    app = create_app()

    # Run with SocketIO
    logger.info("Server starting on http://0.0.0.0:5001")
    logger.info("API available at http://0.0.0.0:5001/api")
    logger.info("Health check: http://0.0.0.0:5001/api/health")

    app.socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=True,
        allow_unsafe_werkzeug=True  # For development only
    )
