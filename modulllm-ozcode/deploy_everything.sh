#!/bin/bash
# MODULllm.com - MASTER DEPLOYMENT SCRIPT
# Tüm sistemleri tek komutla başlat!

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     MODULllm.com - MASTER DEPLOYMENT SYSTEM                 ║"
echo "║     111 Akıl × 100 Site × 30 TB × n8n = ∞ Güç              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}🚀 $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log_step "CHECKING PREREQUISITES"

    # Check Docker
    if command -v docker &> /dev/null; then
        log_success "Docker installed: $(docker --version)"
    else
        log_error "Docker not found! Install: https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose installed: $(docker-compose --version)"
    else
        log_error "Docker Compose not found!"
        exit 1
    fi

    # Check Python
    if command -v python3 &> /dev/null; then
        log_success "Python 3 installed: $(python3 --version)"
    else
        log_error "Python 3 not found!"
        exit 1
    fi

    # Check Node.js
    if command -v node &> /dev/null; then
        log_success "Node.js installed: $(node --version)"
    else
        log_warning "Node.js not found (optional for frontend)"
    fi

    # Check npm
    if command -v npm &> /dev/null; then
        log_success "npm installed: $(npm --version)"
    else
        log_warning "npm not found (optional for frontend)"
    fi
}

# Setup environment
setup_environment() {
    log_step "SETTING UP ENVIRONMENT"

    # Create .env if not exists
    if [ ! -f ".env" ]; then
        log_info "Creating .env from templates..."

        cat > .env <<EOF
# MODULllm.com Master Configuration
PLATFORM_NAME="MODULllm.com"
OZ_KOD_MODE=true
ENVIRONMENT=production

# Gemini Ultra
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXX  # TODO: Add your key!
GEMINI_MODEL=gemini-ultra

# OpenAI (optional)
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXX  # TODO: Add your key!

# Anthropic Claude (optional)
ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXXXXXX  # TODO: Add your key!

# MiniMax
MINIMAX_API_KEY=your_minimax_key  # TODO: Add your key!
MINIMAX_ENDPOINT=https://api.minimax.chat/v1

# n8n
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=modulllm_n8n_2026
N8N_HOST=0.0.0.0
N8N_PORT=5678

# DEAVAEM Gemi
GEMI_ENDPOINT=http://gemi.modulllm.com:8000
GEMI_API_KEY=your_gemi_key

# Database
OZ_DB_PATH=./data/modulllm_oz.db
REDIS_URL=redis://redis:6379/0

# 111 Akıl Configuration
ENABLE_111_AKIL=true
GEMINI_PERSPECTIVES_COUNT=10
PARALLEL_AI_COUNT=11
EOF

        log_success ".env created! Please edit and add your API keys."
        log_warning "Edit .env file and add API keys, then run this script again."
        exit 0
    else
        log_success ".env file found"
    fi
}

# Deploy with Docker Compose
deploy_docker() {
    log_step "DEPLOYING DOCKER CONTAINERS"

    # Create docker-compose master file
    cat > docker-compose.master.yml <<EOF
version: '3.8'

services:
  # MODULllm Platform API
  modulllm-api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: modulllm-platform
    ports:
      - "8000:8000"
    environment:
      - PLATFORM_NAME=\${PLATFORM_NAME}
      - OZ_KOD_MODE=\${OZ_KOD_MODE}
      - GEMINI_API_KEY=\${GEMINI_API_KEY}
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=\${ANTHROPIC_API_KEY}
      - MINIMAX_API_KEY=\${MINIMAX_API_KEY}
      - GEMI_ENDPOINT=\${GEMI_ENDPOINT}
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
    depends_on:
      - redis
      - n8n
    networks:
      - modulllm-network
    restart: unless-stopped

  # n8n Workflow Automation
  n8n:
    image: n8nio/n8n:latest
    container_name: modulllm-n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=\${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=\${N8N_BASIC_AUTH_PASSWORD}
      - N8N_HOST=\${N8N_HOST}
      - N8N_PORT=\${N8N_PORT}
      - N8N_PROTOCOL=http
      - NODE_ENV=production
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=n8n_secure_pass
    volumes:
      - n8n_data:/home/node/.n8n
      - ./integration/workflows:/home/node/.n8n/workflows
    depends_on:
      - postgres
    networks:
      - modulllm-network
    restart: unless-stopped

  # PostgreSQL for n8n
  postgres:
    image: postgres:15-alpine
    container_name: modulllm-postgres
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n_secure_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - modulllm-network
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: modulllm-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - modulllm-network
    restart: unless-stopped

  # Ollama (Local LLM - Optional)
  ollama:
    image: ollama/ollama:latest
    container_name: modulllm-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - modulllm-network
    restart: unless-stopped
    # Uncomment for GPU support:
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

networks:
  modulllm-network:
    driver: bridge

volumes:
  n8n_data:
  postgres_data:
  redis_data:
  ollama_data:
EOF

    log_info "Starting Docker containers..."
    docker-compose -f docker-compose.master.yml up -d

    log_success "All containers started!"

    # Wait for services
    log_info "Waiting for services to be ready..."
    sleep 10

    # Check health
    log_info "Checking service health..."

    # Check Platform API
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "Platform API: ✅ HEALTHY (http://localhost:8000)"
    else
        log_warning "Platform API: ⏳ STARTING... (check logs: docker logs modulllm-platform)"
    fi

    # Check n8n
    if curl -s http://localhost:5678 > /dev/null; then
        log_success "n8n: ✅ HEALTHY (http://localhost:5678)"
    else
        log_warning "n8n: ⏳ STARTING... (check logs: docker logs modulllm-n8n)"
    fi

    # Check Redis
    if docker exec modulllm-redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis: ✅ HEALTHY"
    else
        log_warning "Redis: ⏳ STARTING..."
    fi
}

# Initialize databases
initialize_databases() {
    log_step "INITIALIZING DATABASES"

    log_info "Creating Öz Veritabanı..."
    python3 database/oz_database.py

    log_success "Öz Veritabanı initialized!"
}

# Import n8n workflows
import_n8n_workflows() {
    log_step "IMPORTING n8n WORKFLOWS"

    log_info "Waiting for n8n to be fully ready..."
    sleep 15

    log_info "n8n workflows can be imported manually at:"
    log_info "  http://localhost:5678"
    log_info "  Username: ${N8N_BASIC_AUTH_USER:-admin}"
    log_info "  Password: ${N8N_BASIC_AUTH_PASSWORD:-modulllm_n8n_2026}"
    log_info ""
    log_info "Import file: integration/workflows/111-akil-system.json"

    log_warning "Manual import required (n8n API limitation)"
}

# Setup Ollama models (optional)
setup_ollama() {
    log_step "SETTING UP OLLAMA (OPTIONAL)"

    read -p "Do you want to download Llama 3 model for local inference? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Pulling Llama 3 model... (this may take several minutes)"
        docker exec modulllm-ollama ollama pull llama3
        log_success "Llama 3 model ready!"
    else
        log_info "Skipping Ollama setup. You can do this later with:"
        log_info "  docker exec modulllm-ollama ollama pull llama3"
    fi
}

# Run tests
run_tests() {
    log_step "RUNNING SYSTEM TESTS"

    log_info "Testing Öz Veritabanı..."
    python3 database/oz_database.py > /dev/null 2>&1
    log_success "Öz Veritabanı: ✅"

    log_info "Testing Platform API..."
    response=$(curl -s http://localhost:8000/api/stats)
    if [ ! -z "$response" ]; then
        log_success "Platform API: ✅"
    else
        log_warning "Platform API: ⚠️  May still be starting..."
    fi

    log_info "Testing n8n..."
    if curl -s http://localhost:5678 > /dev/null; then
        log_success "n8n: ✅"
    else
        log_warning "n8n: ⚠️  May still be starting..."
    fi
}

# Display dashboard
show_dashboard() {
    log_step "DEPLOYMENT COMPLETE!"

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              MODULllm.com ACCESS INFORMATION                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${GREEN}🌐 Platform API:${NC}"
    echo "   URL: http://localhost:8000"
    echo "   Docs: http://localhost:8000/api/docs"
    echo "   Stats: http://localhost:8000/api/stats"
    echo ""
    echo -e "${GREEN}🔗 n8n Workflow Automation:${NC}"
    echo "   URL: http://localhost:5678"
    echo "   Username: ${N8N_BASIC_AUTH_USER:-admin}"
    echo "   Password: ${N8N_BASIC_AUTH_PASSWORD:-modulllm_n8n_2026}"
    echo ""
    echo -e "${GREEN}🧠 111 Akıl System:${NC}"
    echo "   Endpoint: http://localhost:8000/api/soru"
    echo "   n8n Webhook: http://localhost:5678/webhook/111-akil"
    echo ""
    echo -e "${GREEN}🤖 Local LLM (Ollama):${NC}"
    echo "   URL: http://localhost:11434"
    echo "   Models: docker exec modulllm-ollama ollama list"
    echo ""
    echo -e "${CYAN}📊 SYSTEM STATUS:${NC}"
    echo "   Platform: $(docker ps --filter name=modulllm-platform --format '{{.Status}}')"
    echo "   n8n: $(docker ps --filter name=modulllm-n8n --format '{{.Status}}')"
    echo "   Redis: $(docker ps --filter name=modulllm-redis --format '{{.Status}}')"
    echo "   Ollama: $(docker ps --filter name=modulllm-ollama --format '{{.Status}}')"
    echo ""
    echo -e "${YELLOW}📝 QUICK COMMANDS:${NC}"
    echo "   View logs: docker-compose -f docker-compose.master.yml logs -f"
    echo "   Stop all: docker-compose -f docker-compose.master.yml down"
    echo "   Restart: docker-compose -f docker-compose.master.yml restart"
    echo ""
    echo -e "${MAGENTA}🚀 NEXT STEPS:${NC}"
    echo "   1. Open n8n and import workflow: integration/workflows/111-akil-system.json"
    echo "   2. Configure LLM credentials in n8n"
    echo "   3. Activate the 111 Akıl workflow"
    echo "   4. Test with: curl -X POST http://localhost:5678/webhook/111-akil -d '{\"soru\":\"Test\"}'"
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         🌌 MODULllm.com - Öz Kodundan Doğan Güç!           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    setup_environment
    deploy_docker
    initialize_databases
    import_n8n_workflows
    setup_ollama
    run_tests
    show_dashboard
}

# Run main
main
