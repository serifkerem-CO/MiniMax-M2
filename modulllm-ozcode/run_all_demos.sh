#!/bin/bash
# MODULllm.com - Tüm Demo'ları Çalıştır
# Sistemin tüm yeteneklerini göster!

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         🎬 MODULllm.com - TÜM DEMO'LAR                      ║"
echo "║         111 Akıl Sistemini Canlı Görün!                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if platform is running
echo -e "${BLUE}📦 Platform kontrolü...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Platform çalışıyor!${NC}\n"
else
    echo -e "${YELLOW}⚠️  Platform çalışmıyor, başlatılıyor...${NC}"
    ./modulllm-ozcode/deploy_everything.sh
    echo -e "${BLUE}⏳ Servislerin hazır olması bekleniyor (20 saniye)...${NC}"
    sleep 20
fi

# Demo 1: Basit Test
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🧪 DEMO 1: BASİT SORU TESTİ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

curl -X POST http://localhost:8000/api/soru \
  -H "Content-Type: application/json" \
  -d '{"soru": "Python ile hello world nasıl yazılır?"}' \
  2>/dev/null | python3 -m json.tool | head -n 30

echo ""
echo -e "${GREEN}✅ Demo 1 tamamlandı!${NC}\n"
sleep 3

# Demo 2: Teknik Soru
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🧪 DEMO 2: TEKNİK SORU (DETAYLI)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

python3 modulllm-ozcode/demo_technical.py

echo -e "${GREEN}✅ Demo 2 tamamlandı!${NC}\n"
sleep 3

# Demo 3: n8n 111 Akıl
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🧪 DEMO 3: n8n 111 AKIL (5 LLM PARALEL)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if curl -s http://localhost:5678 > /dev/null 2>&1; then
    echo -e "${BLUE}n8n webhook tetikleniyor...${NC}\n"
    curl -X POST http://localhost:5678/webhook/111-akil \
      -H "Content-Type: application/json" \
      -d '{"soru": "AI teknolojisi 2026-2030 arası nasıl gelişecek?"}' \
      2>/dev/null | python3 -m json.tool | head -n 50
    echo ""
    echo -e "${GREEN}✅ Demo 3 tamamlandı!${NC}\n"
else
    echo -e "${YELLOW}⚠️  n8n çalışmıyor, demo atlanıyor${NC}\n"
fi
sleep 3

# Demo 4: Öz Veritabanı Öğrenme
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🧪 DEMO 4: ÖZ VERİTABANI ÖĞRENME DÖNGÜSÜ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

python3 modulllm-ozcode/demo_oz_learning.py

echo -e "${GREEN}✅ Demo 4 tamamlandı!${NC}\n"
sleep 3

# Demo 5: LLM Performance Karşılaştırma
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🧪 DEMO 5: LLM PERFORMANS KARŞILAŞTIRMASI${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

python3 modulllm-ozcode/demo_llm_comparison.py

echo -e "${GREEN}✅ Demo 5 tamamlandı!${NC}\n"
sleep 3

# Demo 6: Code Review
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🧪 DEMO 6: CODE REVIEW (JUNIOR DEVELOPER)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

python3 modulllm-ozcode/demo_code_review.py

echo -e "${GREEN}✅ Demo 6 tamamlandı!${NC}\n"
sleep 2

# Final Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ TÜM DEMO'LAR TAMAMLANDI!                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📊 DEMO ÖZET:${NC}"
echo "   ✅ Demo 1: Basit soru testi"
echo "   ✅ Demo 2: Karmaşık teknik soru"
echo "   ✅ Demo 3: n8n 111 Akıl (5 LLM paralel)"
echo "   ✅ Demo 4: Öz Veritabanı öğrenme döngüsü"
echo "   ✅ Demo 5: LLM performans karşılaştırması"
echo "   ✅ Demo 6: Code review & mentoring"
echo ""
echo -e "${CYAN}🌟 MODULllm.com Yetenekleri:${NC}"
echo "   - 111 Akıl sistemi (11 Akıl + Gemini Ultra)"
echo "   - Öz Veritabanı (kendi cevaplarından öğrenir)"
echo "   - n8n multi-LLM orchestration"
echo "   - Real-time code analysis & review"
echo "   - Çoklu perspektif sentezi"
echo ""
echo -e "${YELLOW}📝 Sonraki Adımlar:${NC}"
echo "   1. http://localhost:8000/api/docs - API dokümantasyonu"
echo "   2. http://localhost:5678 - n8n workflow editor"
echo "   3. Kendi sorularınızı sorun!"
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      🌌 MODULllm.com - Öz Kodundan Doğan Güç!              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
