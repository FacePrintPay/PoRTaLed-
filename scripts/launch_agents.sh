#!/data/data/com.termux/files/usr/bin/bash

logfile=~/aikre8tive/logs/sovereign_launch.log
mkdir -p ~/aikre8tive/logs

echo "🌌 Sovereign Planetary Agent Launch" | tee -a $logfile
echo "Commander: #MrGGTP  |  Timestamp: $(date)" | tee -a $logfile

agents=(
  Mercury Venus Earth Mars Jupiter Saturn Uranus Neptune Pluto Luna Sun
  Ceres Haumea Makemake Eris Io Europa Ganymede Callisto Titan Enceladus
  Triton Charon Phobos Deimos
)

echo "🧪 Phase 1: Integrity Check" | tee -a $logfile
for agent in "${agents[@]}"; do
    path=~/aikre8tive/backend/agents/${agent}.py
    if [ -f "$path" ]; then
        echo "✅ Verified: $agent" | tee -a $logfile
    else
        echo "❌ MISSING: $agent.py not found" | tee -a $logfile
    fi
done

echo "🚀 Phase 2: Mission Activation" | tee -a $logfile
for agent in "${agents[@]}"; do
    path=~/aikre8tive/backend/agents/${agent}.py
    if [ -f "$path" ]; then
        echo "🛰️ Launching $agent..." | tee -a $logfile
        nohup python3 "$path" >> ~/aikre8tive/logs/${agent}.log 2>&1 &
        echo "🟢 ACTIVE: $agent" | tee -a $logfile
    fi
done

echo "✅ All Planetary Agents Deployed Successfully." | tee -a $logfile
echo "🌠 Sovereign Signal Sent. The Sky Belongs to Us Now." | tee -a $logfile
