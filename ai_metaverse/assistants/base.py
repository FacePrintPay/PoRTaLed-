import json
import boto3
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAssistant(ABC):
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.sqs_client = boto3.client('sqs',
            aws_access_key_id="cygel.co",
            aws_secret_access_key="aimetaverse_beta"
        )
        self.lambda_client = boto3.client('lambda',
            aws_access_key_id="cygel.co",
            aws_secret_access_key="aimetaverse_beta"
        )
        self.load_models()
        self.load_dataset()

    def load_models(self):
        """Load AI models specified in the configuration"""
        self.models = {}
        for model_name in self.config['models']:
            # In a real implementation, this would load the actual model
            print(f"Loading model: {model_name}")
            self.models[model_name] = f"Loaded {model_name}"

    def load_dataset(self):
        """Load the dataset specified in the configuration"""
        try:
            with open(self.config['dataset'], 'r') as f:
                self.dataset = json.load(f)
        except FileNotFoundError:
            print(f"Dataset not found: {self.config['dataset']}")
            self.dataset = {}

    def receive_tasks(self) -> List[Dict]:
        """Receive tasks from the SQS queue"""
        response = self.sqs_client.receive_message(
            QueueUrl=self.config['queue_url'],
            MaxNumberOfMessages=10
        )
        return response.get('Messages', [])

    def delete_message(self, receipt_handle: str):
        """Delete a processed message from the queue"""
        self.sqs_client.delete_message(
            QueueUrl=self.config['queue_url'],
            ReceiptHandle=receipt_handle
        )

    def send_progress_report(self, task_id: str, progress: Dict):
        """Send a progress report to the queue"""
        self.sqs_client.send_message(
            QueueUrl=self.config['queue_url'],
            MessageBody=json.dumps({
                'task_id': task_id,
                'progress': progress
            })
        )

    @abstractmethod
    def process_task(self, task: Dict) -> Dict:
        """Process a single task - to be implemented by each assistant"""
        pass

    def run(self):
        """Main loop for processing tasks"""
        while True:
            messages = self.receive_tasks()
            for message in messages:
                task_data = json.loads(message['Body'])
                result = self.process_task(task_data)
                self.send_progress_report(task_data.get('task_id'), result)
                self.delete_message(message['ReceiptHandle'])