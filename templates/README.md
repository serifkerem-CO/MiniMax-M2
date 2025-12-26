# MiniMax-M2 Proje Şablonları / Project Templates

MiniMax-M2 ile hızlıca başlamak için kullanıma hazır proje şablonları.

Ready-to-use project templates to quickly get started with MiniMax-M2.

## Mevcut Şablonlar / Available Templates

| Şablon | Açıklama | Kullanım Alanı |
|--------|----------|----------------|
| [basic-api](./basic-api) | Basit API etkileşimi | Başlangıç, temel sorgular |
| [tool-calling-agent](./tool-calling-agent) | Fonksiyon çağırmalı ajan | Agentic iş akışları, otomasyon |
| [coding-assistant](./coding-assistant) | Kod analizi ve üretimi | Geliştirme yardımı |
| [streaming-chat](./streaming-chat) | Gerçek zamanlı sohbet | İnteraktif uygulamalar |
| [batch-processing](./batch-processing) | Toplu istek işleme | Veri işleme, değerlendirme |
| [rag-system](./rag-system) | RAG sistemi | Belge tabanlı soru-cevap |
| [fastapi-server](./fastapi-server) | REST API sunucusu | Web servisleri, API |
| [langchain-integration](./langchain-integration) | LangChain entegrasyonu | Framework kullanımı |
| [discord-bot](./discord-bot) | Discord botu | Sohbet botu |
| [evaluation](./evaluation) | Değerlendirme/Benchmark | Model performans testi |

## Hızlı Başlangıç / Quick Start

1. İhtiyacınıza uygun şablonu seçin
2. Şablon dizinini projenize kopyalayın
3. Bağımlılıkları yükleyin: `pip install -r requirements.txt`
4. API anahtarınızı ve endpoint'inizi yapılandırın
5. Çalıştırın: `python main.py`

## Şablon Yapısı / Template Structure

```
template-name/
├── main.py           # Ana uygulama kodu
├── requirements.txt  # Python bağımlılıkları
├── README.md         # Şablon dokümantasyonu
└── .env.example      # Ortam değişkenleri (varsa)
```

## Yapılandırma / Configuration

Tüm şablonlar şu ortam değişkenlerini kullanır:

```bash
API_BASE_URL=http://localhost:8000/v1  # Yerel dağıtım için
API_KEY=your-api-key-here
MODEL_NAME=MiniMax-M2
```

### Yerel Dağıtım / Local Deployment
```bash
API_BASE_URL=http://localhost:8000/v1
```

### Bulut API / Cloud API
```bash
API_BASE_URL=https://api.minimax.chat/v1
```

## Şablon Açıklamaları / Template Descriptions

### 🚀 Basic API
Başlangıç için en basit şablon:
- API istemcisi oluşturma
- Basit tamamlamalar
- Streaming yanıtlar

### 🤖 Tool-Calling Agent
Araç kullanabilen AI ajanları:
- Araç/fonksiyon tanımları
- Otomatik araç çalıştırma
- Çok turlu konuşmalar
- Genişletilebilir araç kaydı

### 💻 Coding Assistant
Güçlü kodlama yardımcısı:
- Kod analizi ve inceleme
- Kod üretimi
- Hata düzeltme
- Refactoring önerileri
- Çoklu dil desteği

### 💬 Streaming Chat
Gerçek zamanlı sohbet uygulaması:
- Token-token streaming
- Çoklu konuşma
- Düşünme modu toggle
- Zengin terminal görüntüsü

### 📦 Batch Processing
Verimli toplu istek işleme:
- Eşzamanlı çalıştırma
- Otomatik yeniden deneme
- İlerleme takibi
- JSON/CSV dışa aktarma
- İstatistik raporlama

### 📚 RAG System
Retrieval Augmented Generation:
- Belge indeksleme
- Semantik arama
- Bağlamlı yanıtlar
- Kaynak takibi

### 🌐 FastAPI Server
Production-ready REST API:
- OpenAI uyumlu endpoints
- Streaming desteği
- Rate limiting
- Docker desteği

### 🔗 LangChain Integration
LangChain framework entegrasyonu:
- Prompt şablonları
- Hafıza yönetimi
- Zincir bileşimi
- Agent desteği

### 🎮 Discord Bot
Discord sohbet botu:
- Slash komutları
- Kod işlemleri
- Kullanıcı bazlı geçmiş
- Mention yanıtı

### 📊 Evaluation
Model değerlendirme araçları:
- Özel test setleri
- Çeşitli metrikler
- Performans ölçümü
- Görsel raporlar

## Gereksinimler / Requirements

- Python 3.9+
- OpenAI SDK (`pip install openai`)
- Şablona özel bağımlılıklar (her requirements.txt'e bakın)

## MiniMax-M2 Özellikleri / MiniMax-M2 Highlights

Bu şablonlar MiniMax-M2'nin güçlü yönlerinden yararlanır:

- **Kod Mükemmelliği**: SWE-bench'te #1 (%69.4) ve LiveCodeBench (%83)
- **Agentic İş Akışları**: Hata kurtarma ile karmaşık araç kullanımı
- **Verimlilik**: Hızlı çıkarım için sadece 10B aktif parametre
- **Düşünme Modu**: `<think>` etiketleri ile genişletilmiş muhakeme

## Katkıda Bulunma / Contributing

Yeni şablon eklemek için:

1. `templates/` altında yeni dizin oluşturun
2. `main.py`, `requirements.txt` ve `README.md` ekleyin
3. Mevcut şablon kalıplarını takip edin
4. Pull request gönderin

## Kaynaklar / Resources

- [MiniMax-M2 Dokümantasyonu](../README.md)
- [Tool Calling Kılavuzu](../docs/tool_calling_guide.md)
- [Dağıtım Kılavuzları](../docs/)
- [MiniMax Platformu](https://platform.minimax.io/)
