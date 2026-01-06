# MiniMax-M2 Proje Şablonları / Project Templates

MiniMax-M2 ile hızlıca başlamak için kullanıma hazır **27 proje şablonu**.

Ready-to-use **27 project templates** to quickly get started with MiniMax-M2.

## Mevcut Şablonlar / Available Templates

### 🚀 Temel Şablonlar / Core Templates

| Şablon | Açıklama | Kullanım |
|--------|----------|----------|
| [basic-api](./basic-api) | Basit API etkileşimi | Başlangıç |
| [streaming-chat](./streaming-chat) | Gerçek zamanlı sohbet | Chat uygulamaları |
| [batch-processing](./batch-processing) | Toplu istek işleme | Veri işleme |

### 🤖 Ajan Şablonları / Agent Templates

| Şablon | Açıklama | Kullanım |
|--------|----------|----------|
| [tool-calling-agent](./tool-calling-agent) | Fonksiyon çağırmalı ajan | Otomasyon |
| [multi-agent](./multi-agent) | Çoklu ajan sistemi | Karmaşık görevler |
| [coding-assistant](./coding-assistant) | Kod asistanı | Geliştirme |

### 🌐 Web & API Şablonları

| Şablon | Açıklama | Kullanım |
|--------|----------|----------|
| [fastapi-server](./fastapi-server) | REST API sunucusu | Web servisi |
| [gradio-ui](./gradio-ui) | Web arayüzü | Demo & prototip |

### 💬 Bot Şablonları

| Şablon | Açıklama | Kullanım |
|--------|----------|----------|
| [discord-bot](./discord-bot) | Discord botu | Sohbet botu |
| [telegram-bot](./telegram-bot) | Telegram botu | Mesajlaşma |
| [slack-bot](./slack-bot) | Slack botu | İş iletişimi |

### 🔧 Araç Şablonları / Tool Templates

| Şablon | Açıklama | Kullanım |
|--------|----------|----------|
| [cli-tool](./cli-tool) | Komut satırı aracı | Terminal |
| [rag-system](./rag-system) | RAG sistemi | Belge sorgulama |
| [document-summarizer](./document-summarizer) | Belge özetleme | Özetleme |
| [translation-service](./translation-service) | Çeviri servisi | Çeviri |
| [evaluation](./evaluation) | Benchmark aracı | Test & değerlendirme |
| [email-assistant](./email-assistant) | Email asistanı | Email yönetimi |
| [voice-assistant](./voice-assistant) | Ses asistanı | Sesli etkileşim |
| [web-scraper](./web-scraper) | Web kazıyıcı | Veri çıkarma |
| [data-pipeline](./data-pipeline) | Veri pipeline | ETL işlemleri |

### 🛠️ Geliştirici Araçları / Developer Tools

| Şablon | Açıklama | Kullanım |
|--------|----------|----------|
| [code-reviewer](./code-reviewer) | Kod inceleme | Kalite analizi |
| [sql-assistant](./sql-assistant) | SQL asistanı | Veritabanı |
| [test-generator](./test-generator) | Test üretici | Test yazma |
| [log-analyzer](./log-analyzer) | Log analizci | Hata ayıklama |
| [api-docs-generator](./api-docs-generator) | API dokümantasyon | OpenAPI/Swagger |

### 📚 Entegrasyonlar / Integrations

| Şablon | Açıklama | Kullanım |
|--------|----------|----------|
| [langchain-integration](./langchain-integration) | LangChain | Framework |
| [jupyter-notebooks](./jupyter-notebooks) | Jupyter örnekleri | Öğrenme |

## Hızlı Başlangıç / Quick Start

```bash
# 1. Şablon dizinine git
cd templates/basic-api

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. API anahtarını ayarla
export MINIMAX_API_KEY="your-api-key"

# 4. Çalıştır
python main.py
```

## Şablon Yapısı / Template Structure

```
template-name/
├── main.py           # Ana kod
├── requirements.txt  # Bağımlılıklar
├── README.md         # Dokümantasyon
└── .env.example      # Ortam değişkenleri (varsa)
```

## Yapılandırma / Configuration

```bash
# Yerel dağıtım
export MINIMAX_API_BASE="http://localhost:8000/v1"
export MINIMAX_API_KEY="your-api-key"
export MINIMAX_MODEL="MiniMax-M2"

# Bulut API
export MINIMAX_API_BASE="https://api.minimax.chat/v1"
```

## Kategorilere Göre Seçim / Choose by Category

### Yeni Başlayanlar İçin
1. `basic-api` - API kullanımını öğren
2. `jupyter-notebooks` - İnteraktif öğrenme
3. `streaming-chat` - Sohbet uygulaması

### Uygulama Geliştirmek İçin
1. `fastapi-server` - Web API
2. `gradio-ui` - Web arayüzü
3. `discord-bot` veya `telegram-bot` - Bot

### İleri Düzey Kullanım
1. `tool-calling-agent` - Araç kullanımı
2. `multi-agent` - Çoklu ajan
3. `rag-system` - Belge tabanlı AI

### Özel Görevler
1. `document-summarizer` - Özetleme
2. `translation-service` - Çeviri
3. `coding-assistant` - Kod yazma
4. `web-scraper` - Web kazıma
5. `data-pipeline` - Veri işleme
6. `email-assistant` - Email yönetimi
7. `voice-assistant` - Sesli asistan

### Geliştirici Araçları
1. `code-reviewer` - Kod inceleme
2. `sql-assistant` - SQL sorgu üretimi
3. `test-generator` - Otomatik test
4. `log-analyzer` - Log analizi
5. `api-docs-generator` - API dokümantasyon

## MiniMax-M2 Avantajları

Bu şablonlar MiniMax-M2'nin güçlü yönlerinden yararlanır:

| Özellik | Benchmark |
|---------|-----------|
| SWE-bench Verified | **69.4%** (Açık kaynak #1) |
| Terminal-Bench | **46.3%** |
| LiveCodeBench | **83%** |
| Aktif Parametreler | **10B** (Hızlı çıkarım) |

## Katkıda Bulunma / Contributing

1. `templates/` altında yeni dizin oluşturun
2. `main.py`, `requirements.txt`, `README.md` ekleyin
3. Mevcut kalıpları takip edin
4. Pull request gönderin

## Kaynaklar / Resources

- [MiniMax-M2 Ana Repo](../README.md)
- [Tool Calling Kılavuzu](../docs/tool_calling_guide.md)
- [Dağıtım Kılavuzları](../docs/)
- [MiniMax Platformu](https://platform.minimax.io/)
