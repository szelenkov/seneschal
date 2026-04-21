"""
Main entry point for Seneschal application
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    try:
        from seneschal.ui.main_window import SeneschalApp
        
        logger.info("Starting Seneschal v0.1.0")
        
        # Create and run application
        app = SeneschalApp(theme='darkly')
        app.run()
        
        logger.info("Application closed")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

