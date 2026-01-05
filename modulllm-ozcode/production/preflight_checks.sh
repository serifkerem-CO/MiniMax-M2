#!/bin/bash
# MODULllm.com - Pre-flight Checks
# Run before production deployment

set -e

echo "🔍 MODULllm.com Pre-flight Checks"
echo "="*80
echo ""

ERRORS=0

# Check 1: Environment variables
echo "1️⃣  Checking environment variables..."
REQUIRED_VARS=(
    "GEMINI_API_KEY"
    "PLATFORM_NAME"
    "OZ_DB_PATH"
    "REDIS_URL"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "   ❌ Missing: $var"
        ERRORS=$((ERRORS + 1))
    else
        echo "   ✅ Found: $var"
    fi
done

# Check 2: Docker & Docker Compose
echo ""
echo "2️⃣  Checking Docker..."
if command -v docker &> /dev/null; then
    echo "   ✅ Docker installed: $(docker --version)"
else
    echo "   ❌ Docker not found!"
    ERRORS=$((ERRORS + 1))
fi

if command -v docker-compose &> /dev/null; then
    echo "   ✅ Docker Compose installed: $(docker-compose --version)"
else
    echo "   ❌ Docker Compose not found!"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: Disk space
echo ""
echo "3️⃣  Checking disk space..."
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "   ✅ Disk usage: ${DISK_USAGE}%"
else
    echo "   ❌ Disk usage too high: ${DISK_USAGE}%"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: Memory
echo ""
echo "4️⃣  Checking available memory..."
if command -v free &> /dev/null; then
    MEM_AVAILABLE=$(free -m | awk 'NR==2{print $7}')
    if [ "$MEM_AVAILABLE" -gt 1000 ]; then
        echo "   ✅ Available memory: ${MEM_AVAILABLE} MB"
    else
        echo "   ⚠️  Low memory: ${MEM_AVAILABLE} MB (recommended: >1GB)"
    fi
fi

# Check 5: Network connectivity
echo ""
echo "5️⃣  Checking network connectivity..."
if ping -c 1 google.com &> /dev/null; then
    echo "   ✅ Internet connection OK"
else
    echo "   ❌ No internet connection!"
    ERRORS=$((ERRORS + 1))
fi

# Check 6: API endpoints
echo ""
echo "6️⃣  Checking API endpoint accessibility..."
APIs=(
    "https://generativelanguage.googleapis.com"
    "https://api.openai.com"
    "https://api.anthropic.com"
)

for api in "${APIs[@]}"; do
    if curl -s --head --request GET "$api" | grep "200\|301\|302" > /dev/null; then
        echo "   ✅ $api accessible"
    else
        echo "   ⚠️  $api not accessible (check API key or firewall)"
    fi
done

# Check 7: SSL certificate (if domain configured)
echo ""
echo "7️⃣  Checking SSL certificate..."
if [ -n "$DOMAIN" ]; then
    if echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -dates &> /dev/null; then
        echo "   ✅ Valid SSL certificate for $DOMAIN"
    else
        echo "   ⚠️  No valid SSL certificate (run: certbot --nginx -d $DOMAIN)"
    fi
else
    echo "   ⏭️  DOMAIN not configured, skipping SSL check"
fi

# Check 8: Required files
echo ""
echo "8️⃣  Checking required files..."
REQUIRED_FILES=(
    ".env"
    "docker-compose.master.yml"
    "requirements.txt"
    "core/platform_api.py"
    "orchestration/oz_orchestrator.py"
    "database/oz_database.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ Found: $file"
    else
        echo "   ❌ Missing: $file"
        ERRORS=$((ERRORS + 1))
    fi
done

# Final result
echo ""
echo "="*80
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ ALL PRE-FLIGHT CHECKS PASSED!"
    echo "Ready for production deployment."
    exit 0
else
    echo "❌ PRE-FLIGHT CHECKS FAILED!"
    echo "Found $ERRORS error(s). Fix them before deploying."
    exit 1
fi
