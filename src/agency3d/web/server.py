"""Web server startup script."""

import logging
import sys
from pathlib import Path

from agency3d import Config
from agency3d.web.app import create_app

logger = logging.getLogger(__name__)


def main():
    """Start the Voxel web server."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        # Load configuration
        config = Config()

        # Validate configuration
        try:
            config.validate_api_keys()
            config.validate_paths()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            logger.error("\nPlease ensure:")
            logger.error("1. You have a .env file (copy from .env.example)")
            logger.error("2. Your API key is set")
            logger.error("3. BLENDER_PATH is correct")
            sys.exit(1)

        # Create Flask app
        app = create_app(config)

        # Get host and port from environment or use defaults
        import os
        host = os.getenv('WEB_HOST', '0.0.0.0')
        port = int(os.getenv('WEB_PORT', 5000))

        logger.info(f"Starting Voxel web interface on http://{host}:{port}")
        logger.info("Press Ctrl+C to stop")

        # Start server with SocketIO
        app.socketio.run(
            app,
            host=host,
            port=port,
            debug=False,
            use_reloader=False
        )

    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
