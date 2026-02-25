import os
import json
import time
import sys
import logging
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from main import AIMetaverseSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_example_tasks():
    """Load example tasks from JSON file"""
    try:
        with open('examples/tasks/example_tasks.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Example tasks file not found")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing example tasks file: {e}")
        return None

def run_single_task(system, task):
    """Run a single task and monitor its progress"""
    try:
        logger.info(f"Submitting task: {task['task_id']}")
        logger.info(f"Task type: {task['type']}")
        logger.info(f"Requirements: {json.dumps(task['requirements'], indent=2)}")
        
        # Submit the task
        task_id = system.submit_task(task)
        logger.info(f"Task submitted successfully. Task ID: {task_id}")
        
        # Monitor task progress
        while True:
            status = system.get_task_status(task_id)
            logger.info(f"Task status: {status['status']}")
            
            if status['status'] in ['success', 'error', 'completed_with_feedback']:
                logger.info(f"Task completed with status: {status['status']}")
                logger.info(f"Results: {json.dumps(status.get('final_result', {}), indent=2)}")
                break
                
            time.sleep(5)  # Wait before checking status again
            
        return status
        
    except Exception as e:
        logger.error(f"Error running task: {e}")
        return None

def run_all_examples():
    """Run all example tasks"""
    try:
        # Initialize the AI Metaverse system
        logger.info("Initializing AI Metaverse system...")
        system = AIMetaverseSystem()
        
        if not system.initialize_system():
            logger.error("Failed to initialize system")
            return
            
        # Load example tasks
        task_data = load_example_tasks()
        if not task_data:
            logger.error("Failed to load example tasks")
            return
            
        # Process each task
        results = {}
        for task in task_data['tasks']:
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing task: {task['task_id']}")
            logger.info(f"{'='*50}\n")
            
            result = run_single_task(system, task)
            results[task['task_id']] = result
            
        # Display summary
        logger.info("\nExecution Summary:")
        logger.info("="*50)
        for task_id, result in results.items():
            status = result['status'] if result else 'failed'
            logger.info(f"Task {task_id}: {status}")
            
        # Get final system status
        system_status = system.get_system_status()
        logger.info("\nFinal System Status:")
        logger.info(f"Active Assistants: {system_status['active_assistants']}")
        logger.info(f"Completed Tasks: {system_status['completed_tasks']}")
        logger.info(f"Pending Tasks: {system_status['pending_tasks']}")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")

def main():
    """Main entry point for running examples"""
    logger.info("Starting AI Metaverse System Examples")
    logger.info("="*50)
    
    run_all_examples()
    
    logger.info("\nExamples completed")
    logger.info("="*50)

if __name__ == '__main__':
    main()