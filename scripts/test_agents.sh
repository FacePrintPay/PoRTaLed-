#!/bin/bash
# Planetary Agent Testing Script

echo "🌌 Testing AiKre8tive Planetary Agents..."

# Test each agent
AGENTS_DIR="backend/agents"
PASSED=0
FAILED=0

test_agent() {
    local agent=$1
    echo "Testing $agent..."
    
    if [ -f "$AGENTS_DIR/$agent.py" ]; then
        # Try to run the agent
        if python3 "$AGENTS_DIR/$agent.py" --test 2>/dev/null; then
            echo "✅ $agent: PASSED"
            ((PASSED++))
        else
            echo "❌ $agent: FAILED"
            ((FAILED++))
        fi
    else
        echo "⚠️  $agent: FILE NOT FOUND"
        ((FAILED++))
    fi
}

# Test all planetary agents
for agent in Sun Mercury Venus Earth Mars Jupiter Saturn Uranus Neptune Pluto; do
    test_agent "$agent"
done

# Test moon agents
for agent in Luna Phobos Deimos Io Europa Ganymede Callisto Titan Enceladus Triton Charon; do
    test_agent "$agent"
done

# Test dwarf planet agents
for agent in Ceres Eris Haumea Makemake; do
    test_agent "$agent"
done

echo ""
echo "📊 Test Results:"
echo "   ✅ Passed: $PASSED"
echo "   ❌ Failed: $FAILED"
echo "   📈 Success Rate: $(( PASSED * 100 / (PASSED + FAILED) ))%"

if [ $FAILED -eq 0 ]; then
    echo "🎉 All agents are working correctly!"
    exit 0
else
    echo "⚠️  Some agents need attention"
    exit 1
fi
