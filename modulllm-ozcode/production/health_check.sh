#!/bin/bash
# MODULllm.com - Comprehensive Health Check
# Verify all services are operational

echo "🏥 MODULllm.com Health Check"
echo "="*80
echo ""

FAILURES=0

# Check Platform API
echo "1️⃣  Platform API (http://localhost:8000)..."
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    RESPONSE=$(curl -s http://localhost:8000/health)
    echo "   ✅ Platform API is healthy"
    echo "   Status: $(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")"
else
    echo "   ❌ Platform API is down!"
    FAILURES=$((FAILURES + 1))
fi

# Check n8n
echo ""
echo "2️⃣  n8n Workflow Automation (http://localhost:5678)..."
if curl -f -s http://localhost:5678 > /dev/null 2>&1; then
    echo "   ✅ n8n is healthy"
else
    echo "   ❌ n8n is down!"
    FAILURES=$((FAILURES + 1))
fi

# Check Redis
echo ""
echo "3️⃣  Redis Cache..."
if docker exec modulllm-redis redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis is healthy"
else
    echo "   ❌ Redis is down!"
    FAILURES=$((FAILURES + 1))
fi

# Check PostgreSQL (for n8n)
echo ""
echo "4️⃣  PostgreSQL (n8n database)..."
if docker exec modulllm-postgres pg_isready -U n8n > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL is healthy"
else
    echo "   ❌ PostgreSQL is down!"
    FAILURES=$((FAILURES + 1))
fi

# Check Ollama (optional)
echo ""
echo "5️⃣  Ollama (Local LLM)..."
if curl -f -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama is healthy"
    MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('models', [])))" 2>/dev/null || echo "0")
    echo "   Models loaded: $MODELS"
else
    echo "   ⚠️  Ollama is down (optional service)"
fi

# Check Öz Veritabanı
echo ""
echo "6️⃣  Öz Veritabanı..."
if [ -f "$OZ_DB_PATH" ] || [ -f "./data/modulllm_oz.db" ]; then
    DB_PATH="${OZ_DB_PATH:-./data/modulllm_oz.db}"
    COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM oz_icerik" 2>/dev/null || echo "0")
    echo "   ✅ Öz Veritabanı is accessible"
    echo "   Total content: $COUNT items"
else
    echo "   ⚠️  Öz Veritabanı file not found (will be created on first query)"
fi

# Check Docker containers
echo ""
echo "7️⃣  Docker Containers..."
EXPECTED_CONTAINERS=(
    "modulllm-platform"
    "modulllm-n8n"
    "modulllm-redis"
    "modulllm-postgres"
)

for container in "${EXPECTED_CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "$container"; then
        STATUS=$(docker ps --filter "name=$container" --format '{{.Status}}')
        echo "   ✅ $container: $STATUS"
    else
        echo "   ❌ $container is not running!"
        FAILURES=$((FAILURES + 1))
    fi
done

# System resources
echo ""
echo "8️⃣  System Resources..."
if command -v free &> /dev/null; then
    MEM_USAGE=$(free | awk 'NR==2{printf "%.0f%%", $3*100/$2}')
    echo "   Memory usage: $MEM_USAGE"
fi

if command -v df &> /dev/null; then
    DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}')
    echo "   Disk usage: $DISK_USAGE"
fi

# Final result
echo ""
echo "="*80
if [ "$FAILURES" -eq 0 ]; then
    echo "✅ ALL HEALTH CHECKS PASSED!"
    echo "MODULllm.com is fully operational."
    exit 0
else
    echo "❌ HEALTH CHECKS FAILED!"
    echo "Found $FAILURES failed service(s)."
    echo ""
    echo "Troubleshooting:"
    echo "  - Check logs: docker-compose logs -f"
    echo "  - Restart services: docker-compose restart"
    echo "  - Full restart: docker-compose down && docker-compose up -d"
    exit 1
fi
