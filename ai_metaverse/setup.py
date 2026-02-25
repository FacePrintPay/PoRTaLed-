import os
import sys
import subprocess
import logging
from pathlib import Path
from setup.initialize_resources import ResourceInitializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AI_Metaverse_Setup')

class AIMetaverseSetup:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.venv_path = self.base_path / 'venv'
        self.requirements_path = self.base_path / 'requirements.txt'

    def check_python_version(self):
        """Check if Python version meets requirements"""
        logger.info("Checking Python version...")
        
        major, minor = sys.version_info[:2]
        if major < 3 or (major == 3 and minor < 8):
            logger.error("Python 3.8 or higher is required")
            return False
            
        logger.info(f"Python version {major}.{minor} meets requirements")
        return True

    def create_virtual_environment(self):
        """Create a virtual environment"""
        logger.info("Creating virtual environment...")
        
        try:
            if not self.venv_path.exists():
                subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)], check=True)
                logger.info("Virtual environment created successfully")
            else:
                logger.info("Virtual environment already exists")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create virtual environment: {e}")
            return False

    def install_requirements(self):
        """Install required packages"""
        logger.info("Installing required packages...")
        
        try:
            # Determine the pip executable path based on the operating system
            if sys.platform == 'win32':
                pip_path = self.venv_path / 'Scripts' / 'pip'
            else:
                pip_path = self.venv_path / 'bin' / 'pip'

            # Upgrade pip
            subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], check=True)
            
            # Install requirements
            subprocess.run([str(pip_path), 'install', '-r', str(self.requirements_path)], check=True)
            
            logger.info("Required packages installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install requirements: {e}")
            return False

    def setup_environment_variables(self):
        """Set up environment variables"""
        logger.info("Setting up environment variables...")
        
        try:
            env_vars = {
                'AWS_ACCESS_KEY_ID': 'cygel.co',
                'AWS_SECRET_ACCESS_KEY': 'aimetaverse_beta',
                'AI_METAVERSE_ENV': 'development'
            }
            
            # Create .env file
            with open(self.base_path / '.env', 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            logger.info("Environment variables set up successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set up environment variables: {e}")
            return False

    def initialize_resources(self):
        """Initialize AI Metaverse resources"""
        logger.info("Initializing AI Metaverse resources...")
        
        try:
            initializer = ResourceInitializer()
            
            # Create directory structure
            if not initializer.create_directory_structure():
                return False
            
            # Initialize datasets
            if not initializer.initialize_datasets():
                return False
            
            # Initialize models
            if not initializer.initialize_models():
                return False
            
            # Validate resources
            if not initializer.validate_resources():
                return False
            
            logger.info("AI Metaverse resources initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize resources: {e}")
            return False

    def verify_setup(self):
        """Verify the setup was successful"""
        logger.info("Verifying setup...")
        
        try:
            # Check virtual environment
            if not self.venv_path.exists():
                logger.error("Virtual environment not found")
                return False
            
            # Check installed packages
            if sys.platform == 'win32':
                pip_path = self.venv_path / 'Scripts' / 'pip'
            else:
                pip_path = self.venv_path / 'bin' / 'pip'
            
            result = subprocess.run([str(pip_path), 'freeze'], capture_output=True, text=True)
            installed_packages = result.stdout.split('\n')
            
            with open(self.requirements_path, 'r') as f:
                required_packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            missing_packages = []
            for package in required_packages:
                package_name = package.split('>=')[0]
                if not any(p.startswith(package_name) for p in installed_packages):
                    missing_packages.append(package_name)
            
            if missing_packages:
                logger.error(f"Missing packages: {', '.join(missing_packages)}")
                return False
            
            # Check environment variables
            if not (self.base_path / '.env').exists():
                logger.error(".env file not found")
                return False
            
            logger.info("Setup verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Setup verification failed: {e}")
            return False

    def run_example(self):
        """Run an example task to verify system functionality"""
        logger.info("Running example task...")
        
        try:
            # Determine the Python executable path based on the operating system
            if sys.platform == 'win32':
                python_path = self.venv_path / 'Scripts' / 'python'
            else:
                python_path = self.venv_path / 'bin' / 'python'
            
            # Run example
            subprocess.run([str(python_path), str(self.base_path / 'examples' / 'run_examples.py')], check=True)
            
            logger.info("Example task completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to run example task: {e}")
            return False

def main():
    """Main setup function"""
    logger.info("Starting AI Metaverse setup...")
    logger.info("="*50)
    
    setup = AIMetaverseSetup()
    
    # Check Python version
    if not setup.check_python_version():
        return
    
    # Create virtual environment
    if not setup.create_virtual_environment():
        return
    
    # Install requirements
    if not setup.install_requirements():
        return
    
    # Set up environment variables
    if not setup.setup_environment_variables():
        return
    
    # Initialize resources
    if not setup.initialize_resources():
        return
    
    # Verify setup
    if not setup.verify_setup():
        return
    
    # Run example task
    if not setup.run_example():
        return
    
    logger.info("\nAI Metaverse setup completed successfully!")
    logger.info("="*50)
    logger.info("\nNext steps:")
    logger.info("1. Activate the virtual environment:")
    if sys.platform == 'win32':
        logger.info("   .\\venv\\Scripts\\activate")
    else:
        logger.info("   source venv/bin/activate")
    logger.info("2. Review the example tasks in examples/tasks/example_tasks.json")
    logger.info("3. Start developing with the AI Metaverse system")
    logger.info("\nRefer to README.md for detailed documentation and usage instructions")

if __name__ == '__main__':
    main()