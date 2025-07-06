#!/usr/bin/env python3
"""
Scheduled sync script for asset management system.
This script is designed to be run by Windows Task Scheduler.
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from app.sync import sync_snipeit_assets
    from app.settings import settings
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Configure logging
log_dir = backend_dir / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"sync_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main sync function with error handling and logging."""
    try:
        logger.info("Starting scheduled asset sync...")
        start_time = datetime.now()
        
        # Validate settings
        if not settings.snipeit_api_url or not settings.snipeit_token:
            logger.error("Missing required Snipe-IT configuration")
            return 1
        
        # Perform the sync
        sync_snipeit_assets()
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Sync completed successfully in {duration.total_seconds():.2f} seconds")
        
        return 0
        
    except Exception as e:
        logger.error(f"Sync failed with error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 