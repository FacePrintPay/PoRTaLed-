#!/data/data/com.termux/files/usr/bin/bash

# 🧠 Sovereign Commander 1Basher Protocol
logdir=~/aikre8tive/logs
inboxdir=~/aikre8tive/whispersync/inbox
payloadsdir=~/aikre8tive/whispersync/payloads
logfile=$logdir/sovereign_1basher.log
timestamp=$(date +%s)

mkdir -p "$logdir" "$inboxdir" "$payloadsdir"

PAYLOAD="$1"
[ -z "$PAYLOAD" ] && PAYLOAD="🧠 Default scaff2agents directive at $timestamp"

payload_file="$payloadsdir/payload_${timestamp}.txt"
echo "$PAYLOAD" > "$payload_file"
echo "[📦] Payload recorded: $payload_file" | tee -a "$logfile"

AGENTS=(Chronos Echo Zion Recon Mars Pluto Neptune Venus Titan Luna)

echo "🔁 Dispatching to Agents..." | tee -a "$logfile"
for agent in "${AGENTS[@]}"; do
  agent_file="$inboxdir/${agent}_inbox_$timestamp.txt"
  echo "[$(date)] $PAYLOAD" > "$agent_file"
  echo "✅ $agent received payload at $agent_file" | tee -a "$logfile"
done

echo "🌠 Mission Complete. Total agents indexed: ${#AGENTS[@]}" | tee -a "$logfile"
