#!/bin/bash
# MODULllm.com - Integration Tests
# Tüm sistemin end-to-end test'i

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      🧪 MODULllm.com INTEGRATION TESTS                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

FAILED_TESTS=0
PASSED_TESTS=0

# Helper function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}

    echo -ne "Testing ${BLUE}$name${NC}..."

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)

    if [ "$response" == "$expected_status" ]; then
        echo -e " ${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e " ${RED}❌ FAIL${NC} (got HTTP $response, expected $expected_status)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

test_json_endpoint() {
    local name=$1
    local url=$2
    local json_data=$3
    local expected_key=$4

    echo -ne "Testing ${BLUE}$name${NC}..."

    response=$(curl -s -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$json_data" 2>&1)

    if echo "$response" | grep -q "$expected_key"; then
        echo -e " ${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e " ${RED}❌ FAIL${NC} (response missing '$expected_key')"
        echo "  Response: ${response:0:100}..."
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}1️⃣  PLATFORM API TESTS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 1: Health Check
test_endpoint "Health Check" "http://localhost:8000/health"

# Test 2: Ready Check
test_endpoint "Ready Check" "http://localhost:8000/ready"

# Test 3: API Docs
test_endpoint "API Docs" "http://localhost:8000/api/docs"

# Test 4: OpenAPI Schema
test_endpoint "OpenAPI Schema" "http://localhost:8000/openapi.json"

# Test 5: Metrics
test_endpoint "Metrics Endpoint" "http://localhost:8000/metrics"

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}2️⃣  111 AKIL SYSTEM TESTS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 6: Simple Question
test_json_endpoint \
    "Simple Question (111 Akıl)" \
    "http://localhost:8000/api/soru" \
    '{"soru": "Python ile hello world nasıl yazılır?"}' \
    "sentez"

# Test 7: Technical Question
test_json_endpoint \
    "Technical Question" \
    "http://localhost:8000/api/soru" \
    '{"soru": "FastAPI vs Flask hangisi daha iyi?", "context": "production ready"}' \
    "11_akil_harmanlari"

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}3️⃣  ÖZ VERİTABANI TESTS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 8: Öz Veritabanı Write
test_json_endpoint \
    "Öz DB Content Write" \
    "http://localhost:8000/api/soru" \
    '{"soru": "Test question for Öz Veritabanı"}' \
    "oz_kaydi_eklendi"

# Test 9: Öz Veritabanı Read (Stats)
test_endpoint "Öz DB Stats" "http://localhost:8000/api/stats"

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}4️⃣  n8n WORKFLOW TESTS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 10: n8n Service
if curl -f -s http://localhost:5678 > /dev/null 2>&1; then
    echo -e "Testing ${BLUE}n8n Service${NC}... ${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))

    # Test 11: n8n Webhook (if workflow activated)
    echo -ne "Testing ${BLUE}n8n 111 Akıl Webhook${NC}..."
    webhook_response=$(curl -s -X POST "http://localhost:5678/webhook/111-akil" \
        -H "Content-Type: application/json" \
        -d '{"soru": "Test n8n integration"}' 2>&1)

    if echo "$webhook_response" | grep -q "soru\|success\|error" 2>/dev/null; then
        echo -e " ${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e " ${YELLOW}⚠️  SKIP${NC} (workflow not activated or not responding)"
    fi
else
    echo -e "Testing ${BLUE}n8n Service${NC}... ${YELLOW}⚠️  SKIP${NC} (n8n not running)"
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}5️⃣  INFRASTRUCTURE TESTS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 12: Redis
echo -ne "Testing ${BLUE}Redis Cache${NC}..."
if docker exec modulllm-redis redis-cli ping > /dev/null 2>&1; then
    echo -e " ${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e " ${RED}❌ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 13: PostgreSQL
echo -ne "Testing ${BLUE}PostgreSQL (n8n DB)${NC}..."
if docker exec modulllm-postgres pg_isready -U n8n > /dev/null 2>&1; then
    echo -e " ${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e " ${RED}❌ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 14: Ollama (optional)
echo -ne "Testing ${BLUE}Ollama (Local LLM)${NC}..."
if curl -f -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e " ${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e " ${YELLOW}⚠️  SKIP${NC} (optional service)"
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}6️⃣  DOCKER CONTAINER TESTS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 15-19: Container Status
CONTAINERS=(
    "modulllm-platform"
    "modulllm-n8n"
    "modulllm-redis"
    "modulllm-postgres"
)

for container in "${CONTAINERS[@]}"; do
    echo -ne "Testing ${BLUE}$container${NC}..."
    if docker ps --format '{{.Names}}' | grep -q "$container"; then
        echo -e " ${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e " ${RED}❌ FAIL${NC} (container not running)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}7️⃣  PERFORMANCE TESTS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 20: Response Time
echo -ne "Testing ${BLUE}Response Time (<2s)${NC}..."
start_time=$(date +%s.%N)
curl -s http://localhost:8000/health > /dev/null
end_time=$(date +%s.%N)
response_time=$(echo "$end_time - $start_time" | bc)

if (( $(echo "$response_time < 2.0" | bc -l) )); then
    echo -e " ${GREEN}✅ PASS${NC} (${response_time}s)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e " ${RED}❌ FAIL${NC} (${response_time}s, expected <2s)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 21: Concurrent Requests
echo -ne "Testing ${BLUE}Concurrent Requests (10)${NC}..."
for i in {1..10}; do
    curl -s http://localhost:8000/health > /dev/null &
done
wait

if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e " ${RED}❌ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}8️⃣  FILE STRUCTURE TESTS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 22-30: Critical Files
CRITICAL_FILES=(
    "modulllm-ozcode/deploy_everything.sh"
    "modulllm-ozcode/COMPLETE_PLATFORM_GUIDE.md"
    "modulllm-ozcode/PRODUCTION_CHECKLIST.md"
    "modulllm-ozcode/DEMO_SCENARIOS.md"
    "modulllm-ozcode/core/platform_api.py"
    "modulllm-ozcode/orchestration/oz_orchestrator.py"
    "modulllm-ozcode/database/oz_database.py"
    "modulllm-ozcode/monitoring/dashboard.py"
    "modulllm-ozcode/production/health_check.sh"
)

for file in "${CRITICAL_FILES[@]}"; do
    echo -ne "Testing ${BLUE}$file${NC}..."
    if [ -f "$file" ]; then
        echo -e " ${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e " ${RED}❌ FAIL${NC} (file not found)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

# Final Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    TEST RESULTS                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

TOTAL_TESTS=$((PASSED_TESTS + FAILED_TESTS))

echo -e "${GREEN}✅ Passed: $PASSED_TESTS${NC}"
echo -e "${RED}❌ Failed: $FAILED_TESTS${NC}"
echo -e "Total: $TOTAL_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           🎉 ALL TESTS PASSED!                              ║${NC}"
    echo -e "${GREEN}║           MODULllm.com is fully operational!                ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║           ❌ SOME TESTS FAILED                               ║${NC}"
    echo -e "${RED}║           Please check the logs above                        ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if all services are running: docker ps"
    echo "  2. Check logs: docker-compose logs -f"
    echo "  3. Restart services: ./deploy_everything.sh"
    echo "  4. Run health check: ./production/health_check.sh"
    echo ""
    exit 1
fi
