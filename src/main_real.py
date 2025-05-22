"""
Main application entry point for the real data implementation.

This module serves as the main entry point for the application,
using the real data implementations instead of mock data.
"""

import os
import logging
from flask import Flask
from .app_real import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    logger.info(f"Starting application with real data implementation on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
