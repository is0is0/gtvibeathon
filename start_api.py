#!/usr/bin/env python3
"""
Voxel API Server Startup Script
Start the Flask + SocketIO server for the Framer frontend.
"""

import sys
import os
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
    logger.info("Server starting on http://0.0.0.0:5002")
    logger.info("API available at http://0.0.0.0:5002/api")
    logger.info("Health check: http://0.0.0.0:5002/api/health")

    app.socketio.run(
        app,
        host='0.0.0.0',
        port=5002,
        debug=False,  # Disabled to avoid multiple processes with ngrok
        allow_unsafe_werkzeug=True  # For development only
    )
