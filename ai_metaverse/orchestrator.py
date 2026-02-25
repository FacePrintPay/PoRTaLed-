import json
import time
import boto3
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
from .config import ASSISTANTS, AWS_CONFIG, QUEUE_CONFIG
from .assistants.earth import EarthAssistant
from .assistants.moon import MoonAssistant
from .assistants.sun import SunAssistant

class AIMetaverseOrchestrator:
    def __init__(self):
        self.assistants = {}
        self.sqs_client = boto3.client('sqs',
            aws_access_key_id=AWS_CONFIG['access_key_id'],
            aws_secret_access_key=AWS_CONFIG['secret_access_key']
        )
        self.initialize_assistants()
        self.task_queue = []
        self.results = {}

    def initialize_assistants(self):
        """Initialize all planetary AI assistants"""
        assistant_classes = {
            'Earth': EarthAssistant,
            'Moon': MoonAssistant,
            'Sun': SunAssistant
        }

        for name, config in ASSISTANTS.items():
            if name in assistant_classes:
                self.assistants[name] = assistant_classes[name](config)
                print(f"Initialized {name} assistant")

    def submit_task(self, task: Dict) -> str:
        """Submit a new task to the orchestrator"""
        task_id = f"task_{int(time.time())}_{len(self.task_queue)}"
        task['task_id'] = task_id
        task['status'] = 'pending'
        task['timestamp'] = time.time()
        
        # Determine which assistants need to process this task
        task['assigned_assistants'] = self._determine_required_assistants(task)
        
        self.task_queue.append(task)
        self.results[task_id] = {
            'status': 'pending',
            'assistant_results': {},
            'final_result': None
        }
        
        return task_id

    def _determine_required_assistants(self, task: Dict) -> List[str]:
        """Determine which assistants are needed for a given task"""
        required_assistants = []
        task_type = task.get('type', '')
        
        # Map task types to required assistants
        task_assistant_mapping = {
            'code_generation': ['Earth'],
            'syntax_check': ['Moon'],
            'performance_optimization': ['Sun'],
            'full_pipeline': ['Earth', 'Moon', 'Sun']
        }
        
        return task_assistant_mapping.get(task_type, ['Earth'])  # Default to Earth if type unknown

    def process_tasks(self):
        """Process all tasks in the queue"""
        with ThreadPoolExecutor(max_workers=len(self.assistants)) as executor:
            while self.task_queue:
                task = self.task_queue.pop(0)
                task_id = task['task_id']
                
                # Submit task to each required assistant
                future_to_assistant = {
                    executor.submit(self._process_task_with_assistant, task, assistant_name): assistant_name
                    for assistant_name in task['assigned_assistants']
                }
                
                # Process results as they complete
                for future in future_to_assistant:
                    assistant_name = future_to_assistant[future]
                    try:
                        result = future.result()
                        self.results[task_id]['assistant_results'][assistant_name] = result
                    except Exception as e:
                        self.results[task_id]['assistant_results'][assistant_name] = {
                            'status': 'error',
                            'error': str(e)
                        }
                
                # Combine results and update task status
                self._combine_results(task_id)

    def _process_task_with_assistant(self, task: Dict, assistant_name: str) -> Dict:
        """Process a task with a specific assistant"""
        assistant = self.assistants.get(assistant_name)
        if not assistant:
            raise ValueError(f"Assistant {assistant_name} not found")
        
        return assistant.process_task(task)

    def _combine_results(self, task_id: str):
        """Combine results from multiple assistants for a single task"""
        task_results = self.results[task_id]
        assistant_results = task_results['assistant_results']
        
        # Check if all assistants completed successfully
        all_successful = all(
            result.get('status') == 'success'
            for result in assistant_results.values()
        )
        
        # Combine the results based on the task type
        combined_result = {
            'status': 'success' if all_successful else 'partial_success',
            'timestamp': time.time(),
            'components': assistant_results
        }
        
        # Add task-specific combined data
        if 'Earth' in assistant_results:
            combined_result['generated_code'] = assistant_results['Earth'].get('generated_code')
        
        if 'Moon' in assistant_results:
            combined_result['syntax_validation'] = assistant_results['Moon'].get('errors')
        
        if 'Sun' in assistant_results:
            combined_result['performance_analysis'] = assistant_results['Sun'].get('performance_analysis')
        
        self.results[task_id]['status'] = combined_result['status']
        self.results[task_id]['final_result'] = combined_result

    def get_task_status(self, task_id: str) -> Dict:
        """Get the status and results of a specific task"""
        return self.results.get(task_id, {
            'status': 'not_found',
            'error': f'Task {task_id} not found'
        })

    def handle_feedback(self, task_id: str, feedback: Dict):
        """Handle feedback for a specific task"""
        if task_id in self.results:
            # Route feedback to appropriate assistants
            for assistant_name, assistant_feedback in feedback.get('assistant_feedback', {}).items():
                if assistant_name in self.assistants:
                    self.assistants[assistant_name].handle_feedback(assistant_feedback)
            
            # Update task results with feedback
            self.results[task_id]['feedback'] = feedback
            self.results[task_id]['status'] = 'completed_with_feedback'

    def get_assistant_status(self, assistant_name: str) -> Dict:
        """Get the status and capabilities of a specific assistant"""
        assistant = self.assistants.get(assistant_name)
        if assistant:
            return {
                'status': 'active',
                'capabilities': ASSISTANTS[assistant_name]['capabilities'],
                'current_load': len([
                    task for task in self.task_queue
                    if assistant_name in task['assigned_assistants']
                ])
            }
        return {
            'status': 'not_found',
            'error': f'Assistant {assistant_name} not found'
        }

    def get_system_status(self) -> Dict:
        """Get the overall system status"""
        return {
            'active_assistants': len(self.assistants),
            'pending_tasks': len(self.task_queue),
            'completed_tasks': len([
                task_id for task_id, result in self.results.items()
                if result['status'] in ['success', 'completed_with_feedback']
            ]),
            'assistant_status': {
                name: self.get_assistant_status(name)
                for name in self.assistants
            }
        }

if __name__ == '__main__':
    # Initialize and start the orchestrator
    orchestrator = AIMetaverseOrchestrator()
    
    # Example task submission
    task = {
        'type': 'full_pipeline',
        'requirements': {
            'programming_language': 'python',
            'project_type': 'web_application'
        }
    }
    
    task_id = orchestrator.submit_task(task)
    orchestrator.process_tasks()
    
    # Print results
    print(json.dumps(orchestrator.get_task_status(task_id), indent=2))