#!/bin/bash
# MODULllm.com - Daily Automated Backup
# Backs up Öz Veritabanı, n8n workflows, and configuration

BACKUP_DIR="${BACKUP_DIR:-/var/backups/modulllm}"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/modulllm/backup.log"

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

echo "=====================================================================" | tee -a "$LOG_FILE"
echo "MODULllm.com Backup Starting: $DATE" | tee -a "$LOG_FILE"
echo "=====================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 1. Backup Öz Veritabanı
echo "📦 Backing up Öz Veritabanı..." | tee -a "$LOG_FILE"
OZ_DB_PATH="${OZ_DB_PATH:-./data/modulllm_oz.db}"

if [ -f "$OZ_DB_PATH" ]; then
    sqlite3 "$OZ_DB_PATH" ".backup '$BACKUP_DIR/oz_db_$DATE.db'"

    # Verify backup
    if [ -f "$BACKUP_DIR/oz_db_$DATE.db" ]; then
        SIZE=$(du -h "$BACKUP_DIR/oz_db_$DATE.db" | cut -f1)
        echo "   ✅ Öz Veritabanı backed up: $SIZE" | tee -a "$LOG_FILE"
    else
        echo "   ❌ Öz Veritabanı backup failed!" | tee -a "$LOG_FILE"
    fi
else
    echo "   ⚠️  Öz Veritabanı file not found at: $OZ_DB_PATH" | tee -a "$LOG_FILE"
fi

# 2. Backup Vector DB (ChromaDB)
echo "" | tee -a "$LOG_FILE"
echo "📦 Backing up Vector DB..." | tee -a "$LOG_FILE"
CHROMA_DIR="${CHROMA_DIR:-./chroma_db}"

if [ -d "$CHROMA_DIR" ]; then
    tar -czf "$BACKUP_DIR/chroma_db_$DATE.tar.gz" "$CHROMA_DIR/" 2>&1 | tee -a "$LOG_FILE"

    if [ -f "$BACKUP_DIR/chroma_db_$DATE.tar.gz" ]; then
        SIZE=$(du -h "$BACKUP_DIR/chroma_db_$DATE.tar.gz" | cut -f1)
        echo "   ✅ Vector DB backed up: $SIZE" | tee -a "$LOG_FILE"
    else
        echo "   ❌ Vector DB backup failed!" | tee -a "$LOG_FILE"
    fi
else
    echo "   ⏭️  Vector DB directory not found, skipping" | tee -a "$LOG_FILE"
fi

# 3. Backup n8n workflows (if running in Docker)
echo "" | tee -a "$LOG_FILE"
echo "📦 Backing up n8n workflows..." | tee -a "$LOG_FILE"

if docker ps --format '{{.Names}}' | grep -q "modulllm-n8n"; then
    docker exec modulllm-n8n sh -c 'cd /home/node/.n8n && tar -czf - workflows/' > "$BACKUP_DIR/n8n_workflows_$DATE.tar.gz" 2>> "$LOG_FILE"

    if [ -f "$BACKUP_DIR/n8n_workflows_$DATE.tar.gz" ]; then
        SIZE=$(du -h "$BACKUP_DIR/n8n_workflows_$DATE.tar.gz" | cut -f1)
        echo "   ✅ n8n workflows backed up: $SIZE" | tee -a "$LOG_FILE"
    else
        echo "   ❌ n8n workflows backup failed!" | tee -a "$LOG_FILE"
    fi
else
    echo "   ⏭️  n8n container not running, skipping" | tee -a "$LOG_FILE"
fi

# 4. Backup configuration files
echo "" | tee -a "$LOG_FILE"
echo "📦 Backing up configuration..." | tee -a "$LOG_FILE"

CONFIG_FILES=(
    ".env"
    "docker-compose.master.yml"
    "requirements.txt"
)

tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" "${CONFIG_FILES[@]}" 2>> "$LOG_FILE"

if [ -f "$BACKUP_DIR/config_$DATE.tar.gz" ]; then
    SIZE=$(du -h "$BACKUP_DIR/config_$DATE.tar.gz" | cut -f1)
    echo "   ✅ Configuration backed up: $SIZE" | tee -a "$LOG_FILE"
else
    echo "   ❌ Configuration backup failed!" | tee -a "$LOG_FILE"
fi

# 5. Upload to cloud (optional - requires rclone)
echo "" | tee -a "$LOG_FILE"
echo "☁️  Uploading to cloud storage..." | tee -a "$LOG_FILE"

if command -v rclone &> /dev/null; then
    rclone sync "$BACKUP_DIR" gdrive:MODULllm-Backups/ --progress 2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        echo "   ✅ Cloud upload successful" | tee -a "$LOG_FILE"
    else
        echo "   ❌ Cloud upload failed (check rclone config)" | tee -a "$LOG_FILE"
    fi
else
    echo "   ⏭️  rclone not installed, skipping cloud upload" | tee -a "$LOG_FILE"
    echo "   Install: curl https://rclone.org/install.sh | sudo bash" | tee -a "$LOG_FILE"
fi

# 6. Cleanup old backups (keep last 30 days)
echo "" | tee -a "$LOG_FILE"
echo "🧹 Cleaning up old backups (>30 days)..." | tee -a "$LOG_FILE"

DELETED_COUNT=0
DELETED_COUNT=$((DELETED_COUNT + $(find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete -print | wc -l)))
DELETED_COUNT=$((DELETED_COUNT + $(find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete -print | wc -l)))

echo "   Deleted $DELETED_COUNT old backup file(s)" | tee -a "$LOG_FILE"

# Summary
echo "" | tee -a "$LOG_FILE"
echo "=====================================================================" | tee -a "$LOG_FILE"
echo "✅ Backup Completed: $DATE" | tee -a "$LOG_FILE"

TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
FILE_COUNT=$(ls -1 "$BACKUP_DIR" | wc -l)

echo "Total backup size: $TOTAL_SIZE" | tee -a "$LOG_FILE"
echo "Total files: $FILE_COUNT" | tee -a "$LOG_FILE"
echo "=====================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Crontab entry (add to crontab -e):
# 0 2 * * * /opt/modulllm/backup/daily_backup.sh
