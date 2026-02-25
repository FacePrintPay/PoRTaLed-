# Configuration for AI Metaverse Planetary Assistants

import os

# AWS Configuration
AWS_CONFIG = {
    "access_key_id": "cygel.co",
    "secret_access_key": "aimetaverse_beta",
    "region": "us-east-1"
}

# Assistant Configurations
ASSISTANTS = {
    "Earth": {
        "task": "Generate foundational code structures",
        "models": ["OpenAI Codex", "GitHub Copilot"],
        "dataset": "datasets/earth/code_structures.json",
        "queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/earth_tasks",
        "capabilities": ["code_generation", "structure_analysis"]
    },
    "Moon": {
        "task": "Identify and resolve syntax errors",
        "models": ["SyntaxNet", "ErrorDetector"],
        "dataset": "datasets/moon/syntax_errors.json",
        "queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/moon_tasks",
        "capabilities": ["error_detection", "code_correction"]
    },
    "Sun": {
        "task": "Analyze and optimize code performance",
        "models": ["PerformanceOptimizer", "CodeProfiler"],
        "dataset": "datasets/sun/performance_metrics.json",
        "queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/sun_tasks",
        "capabilities": ["performance_analysis", "code_optimization"]
    },
    "Mercury": {
        "task": "Generate unit tests",
        "models": ["TestGenerator", "CodeCoverage"],
        "dataset": "datasets/mercury/unit_tests.json",
        "queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/mercury_tasks",
        "capabilities": ["test_generation", "coverage_analysis"]
    },
    "Venus": {
        "task": "Perform automated regression testing",
        "models": ["RegressionTester", "TestAutomation"],
        "dataset": "datasets/venus/regression_tests.json",
        "queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/venus_tasks",
        "capabilities": ["regression_testing", "test_automation"]
    },
    "Mars": {
        "task": "Identify security vulnerabilities",
        "models": ["SecurityScanner", "VulnerabilityDetector"],
        "dataset": "datasets/mars/security_vulnerabilities.json",
        "queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/mars_tasks",
        "capabilities": ["security_analysis", "vulnerability_detection"]
    },
    "Jupiter": {
        "task": "Analyze and document code",
        "models": ["DocumentationGenerator", "CodeAnalyzer"],
        "dataset": "datasets/jupiter/code_documentation.json",
        "queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/jupiter_tasks",
        "capabilities": ["documentation_generation", "code_analysis"]
    }
}

# Model Paths
MODEL_PATHS = {
    "OpenAI Codex": "models/openai_codex",
    "GitHub Copilot": "models/github_copilot",
    "SyntaxNet": "models/syntaxnet",
    "ErrorDetector": "models/error_detector",
    "PerformanceOptimizer": "models/performance_optimizer",
    "CodeProfiler": "models/code_profiler",
    "TestGenerator": "models/test_generator",
    "CodeCoverage": "models/code_coverage",
    "RegressionTester": "models/regression_tester",
    "TestAutomation": "models/test_automation",
    "SecurityScanner": "models/security_scanner",
    "VulnerabilityDetector": "models/vulnerability_detector",
    "DocumentationGenerator": "models/documentation_generator",
    "CodeAnalyzer": "models/code_analyzer"
}

# Task Queue Configuration
QUEUE_CONFIG = {
    "max_messages": 10,
    "wait_time": 20,
    "visibility_timeout": 300
}

# GitHub Repository Configuration
GITHUB_CONFIG = {
    "repository_url": "https://github.com/your-organization/planetary-ai-metaverse",
    "access_token": os.getenv("GITHUB_ACCESS_TOKEN")
}