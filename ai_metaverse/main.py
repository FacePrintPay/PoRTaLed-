import os
import json
import argparse
import logging
from typing import Dict, Any
from orchestrator import AIMetaverseOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_metaverse.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('AI_Metaverse')

class AIMetaverseSystem:
    def __init__(self):
        self.orchestrator = AIMetaverseOrchestrator()
        self.logger = logger

    def initialize_system(self):
        """Initialize the AI Metaverse system"""
        try:
            self.logger.info("Initializing AI Metaverse system...")
            
            # Create necessary directories if they don't exist
            directories = [
                'datasets/earth',
                'datasets/moon',
                'datasets/sun',
                'models',
                'logs'
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                self.logger.info(f"Ensured directory exists: {directory}")

            # Initialize example datasets if they don't exist
            self._initialize_example_datasets()
            
            self.logger.info("AI Metaverse system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Metaverse system: {str(e)}")
            return False

    def _initialize_example_datasets(self):
        """Initialize example datasets for assistants"""
        example_datasets = {
            'earth': {
                'code_templates': {
                    'python': {
                        'web_application': '# Flask Web Application Template\n...',
                        'api_service': '# FastAPI Service Template\n...'
                    }
                },
                'structure_patterns': {
                    'python': {
                        'web_application': ['mvc', 'repository'],
                        'api_service': ['resource_based', 'layered']
                    }
                }
            },
            'moon': {
                'error_patterns': {
                    'python': [
                        {
                            'pattern': 'undefined variable',
                            'type': 'NameError',
                            'severity': 'high'
                        }
                    ]
                },
                'correction_templates': {
                    'python': {
                        'NameError': {
                            'description': 'Variable not defined',
                            'example': 'Define the variable before use'
                        }
                    }
                }
            },
            'sun': {
                'performance_metrics': {
                    'python': {
                        'time_complexity': ['O(1)', 'O(n)', 'O(n^2)'],
                        'space_complexity': ['O(1)', 'O(n)']
                    }
                },
                'optimization_patterns': {
                    'python': {
                        'loops': ['list comprehension', 'generator expression'],
                        'data_structures': ['set for lookup', 'dictionary for mapping']
                    }
                }
            }
        }

        for assistant, data in example_datasets.items():
            filepath = f'datasets/{assistant}/{assistant}_data.json'
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                self.logger.info(f"Created example dataset: {filepath}")

    def submit_task(self, task: Dict[str, Any]) -> str:
        """Submit a task to the AI Metaverse system"""
        try:
            self.logger.info(f"Submitting task: {task.get('type', 'unknown')}")
            task_id = self.orchestrator.submit_task(task)
            self.logger.info(f"Task submitted successfully. Task ID: {task_id}")
            return task_id
        except Exception as e:
            self.logger.error(f"Failed to submit task: {str(e)}")
            raise

    def process_tasks(self):
        """Process all pending tasks"""
        try:
            self.logger.info("Starting task processing")
            self.orchestrator.process_tasks()
            self.logger.info("Task processing completed")
        except Exception as e:
            self.logger.error(f"Error during task processing: {str(e)}")
            raise

    def get_task_status(self, task_id: str) -> Dict:
        """Get the status of a specific task"""
        try:
            status = self.orchestrator.get_task_status(task_id)
            self.logger.info(f"Retrieved status for task {task_id}: {status['status']}")
            return status
        except Exception as e:
            self.logger.error(f"Failed to get task status: {str(e)}")
            raise

    def get_system_status(self) -> Dict:
        """Get the overall system status"""
        try:
            status = self.orchestrator.get_system_status()
            self.logger.info("Retrieved system status")
            return status
        except Exception as e:
            self.logger.error(f"Failed to get system status: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='AI Metaverse System')
    parser.add_argument('--task', type=str, help='Task file in JSON format')
    parser.add_argument('--status', type=str, help='Get status for task ID')
    parser.add_argument('--system-status', action='store_true', help='Get system status')
    
    args = parser.parse_args()
    
    # Initialize the system
    system = AIMetaverseSystem()
    if not system.initialize_system():
        logger.error("Failed to initialize system. Exiting.")
        return

    # Process command line arguments
    if args.task:
        try:
            with open(args.task, 'r') as f:
                task = json.load(f)
            task_id = system.submit_task(task)
            system.process_tasks()
            result = system.get_task_status(task_id)
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            logger.error(f"Error processing task file: {str(e)}")
            
    elif args.status:
        try:
            status = system.get_task_status(args.status)
            print(json.dumps(status, indent=2))
            
        except Exception as e:
            logger.error(f"Error getting task status: {str(e)}")
            
    elif args.system_status:
        try:
            status = system.get_system_status()
            print(json.dumps(status, indent=2))
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            
    else:
        parser.print_help()

if __name__ == '__main__':
    main()