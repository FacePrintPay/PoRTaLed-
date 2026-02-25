#!/usr/bin/env python3
"""
Agent Health Check for AiKre8tive Sovereign Agent System
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime

def load_agent(agent_path):
    """Load an agent module from file path"""
    try:
        spec = importlib.util.spec_from_file_location("agent", agent_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        return None

def check_agent_health(agent_name, agent_path):
    """Check health of a single agent"""
    health_status = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "status": "unknown",
        "errors": []
    }
    
    # Check if file exists
    if not os.path.exists(agent_path):
        health_status["status"] = "missing"
        health_status["errors"].append("Agent file not found")
        return health_status
    
    # Try to load the agent
    module = load_agent(agent_path)
    if module is None:
        health_status["status"] = "error"
        health_status["errors"].append("Failed to load agent module")
        return health_status
    
    # Check for required methods/classes
    required_attributes = ["main", "__doc__"]
    for attr in required_attributes:
        if not hasattr(module, attr):
            health_status["errors"].append(f"Missing required attribute: {attr}")
    
    # If no errors, agent is healthy
    if not health_status["errors"]:
        health_status["status"] = "healthy"
    else:
        health_status["status"] = "warning"
    
    return health_status

def main():
    """Main health check execution"""
    print("🏥 AiKre8tive Agent Health Check")
    print("================================")
    
    agents_dir = Path("backend/agents")
    if not agents_dir.exists():
        print("❌ Agents directory not found!")
        return 1
    
    all_agents = [
        "Sun", "Mercury", "Venus", "Earth", "Mars", 
        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
        "Luna", "Phobos", "Deimos", "Io", "Europa", "Ganymede", 
        "Callisto", "Titan", "Enceladus", "Triton", "Charon",
        "Ceres", "Eris", "Haumea", "Makemake"
    ]
    
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "total_agents": len(all_agents),
        "healthy": 0,
        "warnings": 0,
        "errors": 0,
        "missing": 0,
        "agents": []
    }
    
    for agent_name in all_agents:
        agent_path = agents_dir / f"{agent_name}.py"
        health_status = check_agent_health(agent_name, agent_path)
        health_report["agents"].append(health_status)
        
        # Update counters
        status = health_status["status"]
        if status == "healthy":
            health_report["healthy"] += 1
            print(f"✅ {agent_name}: Healthy")
        elif status == "warning":
            health_report["warnings"] += 1
            print(f"⚠️  {agent_name}: Warning - {', '.join(health_status['errors'])}")
        elif status == "error":
            health_report["errors"] += 1
            print(f"❌ {agent_name}: Error - {', '.join(health_status['errors'])}")
        elif status == "missing":
            health_report["missing"] += 1
            print(f"📁 {agent_name}: Missing")
    
    # Save detailed report
    os.makedirs("logs", exist_ok=True)
    with open("logs/agent_health_report.json", "w") as f:
        json.dump(health_report, f, indent=2)
    
    # Print summary
    print("\n📊 Health Summary:")
    print(f"   ✅ Healthy: {health_report['healthy']}")
    print(f"   ⚠️  Warnings: {health_report['warnings']}")
    print(f"   ❌ Errors: {health_report['errors']}")
    print(f"   📁 Missing: {health_report['missing']}")
    print(f"   📈 Health Rate: {health_report['healthy'] * 100 // len(all_agents)}%")
    
    print(f"\n📄 Detailed report saved to: logs/agent_health_report.json")
    
    return 0 if health_report['errors'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
