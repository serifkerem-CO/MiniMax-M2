#!/bin/bash
# MODULllm.com - Disaster Recovery
# Restore from backup

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         MODULllm.com Disaster Recovery                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Usage: ./restore.sh <backup_date>"
    echo ""
    echo "Available backups:"
    ls -lh /var/backups/modulllm/oz_db_*.db 2>/dev/null | awk '{print "  -", $9, "("$5")"}'
    echo ""
    echo "Example: ./restore.sh 20260105_020000"
    exit 1
fi

BACKUP_DIR="${BACKUP_DIR:-/var/backups/modulllm}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         🚨 DISASTER RECOVERY STARTING...                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Backup date: $BACKUP_FILE"
echo ""

# Confirm
read -p "⚠️  This will OVERWRITE current data. Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Stop services
echo ""
echo "🛑 Stopping services..."
docker-compose -f docker-compose.master.yml down

# Backup current state (before restore)
echo ""
echo "💾 Creating emergency backup of current state..."
EMERGENCY_BACKUP_DIR="/var/backups/modulllm/emergency_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$EMERGENCY_BACKUP_DIR"
cp -r ./data "$EMERGENCY_BACKUP_DIR/" 2>/dev/null || true
cp -r ./chroma_db "$EMERGENCY_BACKUP_DIR/" 2>/dev/null || true
echo "   Saved to: $EMERGENCY_BACKUP_DIR"

# Restore Öz Veritabanı
echo ""
echo "📦 Restoring Öz Veritabanı..."
OZ_DB_PATH="${OZ_DB_PATH:-./data/modulllm_oz.db}"

if [ -f "$BACKUP_DIR/oz_db_$BACKUP_FILE.db" ]; then
    mkdir -p $(dirname "$OZ_DB_PATH")
    cp "$BACKUP_DIR/oz_db_$BACKUP_FILE.db" "$OZ_DB_PATH"
    echo "   ✅ Öz Veritabanı restored"
else
    echo "   ❌ Backup file not found: $BACKUP_DIR/oz_db_$BACKUP_FILE.db"
fi

# Restore Vector DB
echo ""
echo "📦 Restoring Vector DB..."
CHROMA_DIR="${CHROMA_DIR:-./chroma_db}"

if [ -f "$BACKUP_DIR/chroma_db_$BACKUP_FILE.tar.gz" ]; then
    rm -rf "$CHROMA_DIR"
    mkdir -p "$CHROMA_DIR"
    tar -xzf "$BACKUP_DIR/chroma_db_$BACKUP_FILE.tar.gz" -C .
    echo "   ✅ Vector DB restored"
else
    echo "   ⏭️  Vector DB backup not found, skipping"
fi

# Restore n8n workflows
echo ""
echo "📦 Preparing n8n workflows restore..."

if [ -f "$BACKUP_DIR/n8n_workflows_$BACKUP_FILE.tar.gz" ]; then
    mkdir -p /tmp/n8n_restore
    tar -xzf "$BACKUP_DIR/n8n_workflows_$BACKUP_FILE.tar.gz" -C /tmp/n8n_restore/
    echo "   ✅ n8n workflows extracted (will be restored after n8n starts)"
else
    echo "   ⏭️  n8n workflows backup not found, skipping"
fi

# Restore configuration
echo ""
echo "📦 Restoring configuration..."

if [ -f "$BACKUP_DIR/config_$BACKUP_FILE.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/config_$BACKUP_FILE.tar.gz"
    echo "   ✅ Configuration restored"
else
    echo "   ⏭️  Configuration backup not found, skipping"
fi

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose -f docker-compose.master.yml up -d

# Wait for services
echo ""
echo "⏳ Waiting for services to be ready (20 seconds)..."
sleep 20

# Restore n8n workflows (now that n8n is running)
echo ""
echo "📦 Restoring n8n workflows to container..."

if [ -d "/tmp/n8n_restore/workflows" ]; then
    docker cp /tmp/n8n_restore/workflows/. modulllm-n8n:/home/node/.n8n/workflows/
    docker restart modulllm-n8n
    echo "   ✅ n8n workflows restored"
    rm -rf /tmp/n8n_restore
else
    echo "   ⏭️  No workflows to restore"
fi

# Health check
echo ""
echo "🏥 Running health check..."
sleep 10

./production/health_check.sh

if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         ✅ RECOVERY COMPLETE!                               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "MODULllm.com has been restored from backup: $BACKUP_FILE"
    echo ""
    echo "Verification:"
    echo "  curl http://localhost:8000/health"
    echo "  curl http://localhost:8000/api/stats"
    echo ""
    echo "Emergency backup saved at: $EMERGENCY_BACKUP_DIR"
else
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         ❌ RECOVERY FAILED!                                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Some services may not be healthy. Check logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "Emergency backup available at: $EMERGENCY_BACKUP_DIR"
fi
