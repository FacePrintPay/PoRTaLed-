#!/usr/bin/env python3
"""
Whisper Sync Module for AiKre8tive Sovereign Agent System
Handles audio transcription and synchronization across planetary agents
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/whisper_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WhisperSync:
    """
    Whisper synchronization handler for planetary agent communication
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize WhisperSync with configuration"""
        self.config_path = config_path or "config/whisper_config.json"
        self.config = self._load_config()
        self.sync_directory = Path(self.config.get('sync_directory', 'sync_data'))
        self.sync_directory.mkdir(exist_ok=True)
        
        # Create logs directory if it doesn't exist
        Path('logs').mkdir(exist_ok=True)
        
        logger.info("WhisperSync initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default config
                default_config = {
                    "sync_directory": "sync_data",
                    "max_retries": 3,
                    "sync_interval": 30,
                    "agents": [
                        "Sun", "Mercury", "Venus", "Earth", "Mars", 
                        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
                    ],
                    "whisper_model": "base",
                    "language": "auto"
                }
                
                # Create config directory if needed
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                
                logger.info(f"Created default config at {self.config_path}")
                return default_config
                
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {"sync_directory": "sync_data", "max_retries": 3}
    
    def sync_agent_data(self, agent_name: str, data: Dict[str, Any]) -> bool:
        """
        Synchronize data from a planetary agent
        
        Args:
            agent_name: Name of the planetary agent
            data: Data to synchronize
            
        Returns:
            bool: Success status
        """
        try:
            timestamp = datetime.now().isoformat()
            sync_file = self.sync_directory / f"{agent_name}_{timestamp}.json"
            
            sync_payload = {
                "agent": agent_name,
                "timestamp": timestamp,
                "data": data,
                "sync_id": f"{agent_name}_{int(time.time())}"
            }
            
            with open(sync_file, 'w') as f:
                json.dump(sync_payload, f, indent=2)
            
            logger.info(f"Successfully synced data for agent {agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync data for {agent_name}: {e}")
            return False
    
    def get_latest_sync(self, agent_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the latest sync data for an agent or all agents
        
        Args:
            agent_name: Specific agent name, or None for all agents
            
        Returns:
            Latest sync data or None if not found
        """
        try:
            sync_files = list(self.sync_directory.glob(f"{agent_name or '*'}_*.json"))
            if not sync_files:
                return None
            
            # Get the most recent file
            latest_file = max(sync_files, key=os.path.getctime)
            
            with open(latest_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error getting latest sync: {e}")
            return None
    
    def cleanup_old_syncs(self, days_old: int = 7) -> int:
        """
        Clean up sync files older than specified days
        
        Args:
            days_old: Number of days after which to delete files
            
        Returns:
            Number of files deleted
        """
        try:
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for sync_file in self.sync_directory.glob("*.json"):
                if os.path.getctime(sync_file) < cutoff_time:
                    os.remove(sync_file)
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old sync files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the whisper sync system
        
        Returns:
            Health status information
        """
        try:
            status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "config_loaded": bool(self.config),
                "sync_directory_exists": self.sync_directory.exists(),
                "sync_directory_writable": os.access(self.sync_directory, os.W_OK),
                "total_sync_files": len(list(self.sync_directory.glob("*.json")))
            }
            
            # Check if all required agents have recent syncs
            agents = self.config.get('agents', [])
            recent_syncs = {}
            
            for agent in agents:
                latest_sync = self.get_latest_sync(agent)
                recent_syncs[agent] = latest_sync is not None
            
            status['agent_sync_status'] = recent_syncs
            status['agents_synced'] = sum(recent_syncs.values())
            status['total_agents'] = len(agents)
            
            # Overall health
            if status['agents_synced'] < len(agents) * 0.8:  # Less than 80% synced
                status['status'] = 'warning'
            
            return status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

def main():
    """Main execution function for testing"""
    try:
        # Initialize WhisperSync
        whisper_sync = WhisperSync()
        
        # Perform health check
        health = whisper_sync.health_check()
        print(f"Health Check: {json.dumps(health, indent=2)}")
        
        # Test sync with sample data
        test_data = {
            "message": "System initialized successfully",
            "status": "active",
            "capabilities": ["transcription", "sync", "monitoring"]
        }
        
        success = whisper_sync.sync_agent_data("Earth", test_data)
        print(f"Test sync successful: {success}")
        
        # Get latest sync
        latest = whisper_sync.get_latest_sync("Earth")
        if latest:
            print(f"Latest sync: {json.dumps(latest, indent=2)}")
        
        logger.info("WhisperSync test completed successfully")
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
