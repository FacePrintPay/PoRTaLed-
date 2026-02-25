#!/data/data/com.termux/files/usr/bin/bash
BASE_DIR="$HOME/ai_metaverse"
LOG_DIR="$HOME/logs/agents"
VAULT_DIR="$HOME/storage/shared/Obsidian/SovereignVault"
BUS_FILE="$BASE_DIR/agents_bus.json"
KEY_STORE="$BASE_DIR/keystore.enc"
CREDS_FILE="$BASE_DIR/server_creds.json"

ROTATION_DATE=$(date +%Y%m%d)
USERNAME="agent_${ROTATION_DATE}"
PASSWORD=$(openssl rand -hex 12)
CURRENT_KEYHOLDER="Keyholder"

# Save creds (encrypted by Keyholder)
echo "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\", \"date\": \"$ROTATION_DATE\"}" \
  | openssl enc -aes-256-cbc -pbkdf2 -salt -out "$CREDS_FILE.enc" -k "CAMEO-LEGACY"

# Init keystore if missing
if [ ! -f "$KEY_STORE" ]; then
  echo "AiMetaverse-Keys" | openssl enc -aes-256-cbc -pbkdf2 -salt -out $KEY_STORE -k "CAMEO-LEGACY"
fi

# Collaboration bus
cat > "$BUS_FILE" <<EOT
{
  "shared_storage": {
    "http": "https://10.75.117.112:8000/",
    "ftp": "ftp://10.75.117.112:2222/",
    "path": "/storage/emulated/0/",
    "username": "$USERNAME",
    "password": "[ENCRYPTED: request from Keyholder]"
  },
  "keyholder": "$CURRENT_KEYHOLDER",
  "rotation_date": "$ROTATION_DATE"
}
EOT

# Vault journal
JOURNAL_FILE="$VAULT_DIR/Keyholder_Rotation_${ROTATION_DATE}.md"
cat > "$JOURNAL_FILE" <<EOT
# Keyholder Rotation – $ROTATION_DATE
- Keyholder: $CURRENT_KEYHOLDER
- Username: $USERNAME
- Password: [ENCRYPTED]
- Rotation Date: $ROTATION_DATE
- Logs: $LOG_DIR/
EOT

echo "[\$(date)] Rotation complete for $ROTATION_DATE" >> "$LOG_DIR/rotation.log"
