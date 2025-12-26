# MiniMax-M2 RAG Sistemi Şablonu

Belgelerden bilgi alarak sorulara cevap veren bir RAG (Retrieval Augmented Generation) sistemi.

MiniMax-M2, kanıt takipli retrieval ve alıntı yapma konusunda mükemmel performans gösterir.

## Hızlı Başlangıç

1. Bağımlılıkları yükle:
```bash
pip install -r requirements.txt
```

2. API ayarlarını `main.py` dosyasında yapılandır

3. Çalıştır:
```bash
python main.py
```

## Özellikler

- **Belge İndeksleme**: Metin dosyalarını parçalara ayırır ve vektör veritabanında saklar
- **Semantik Arama**: Sorguya en yakın belge parçalarını bulur
- **Bağlamlı Yanıtlar**: Bulunan belgeler kullanılarak doğru yanıtlar üretir
- **Kaynak Takibi**: Her yanıtın hangi belgeden geldiğini gösterir
- **Kalıcı Depolama**: ChromaDB ile vektörler kalıcı olarak saklanır

## Kullanım

### Belge Ekleme

```python
from main import RAGSystem

rag = RAGSystem()

# Metin ekle
rag.add_text("Python bir programlama dilidir...", source="python.txt")

# Dosya ekle
rag.add_file("./docs/manual.md")

# Dizin ekle
rag.add_directory("./docs", extensions=[".txt", ".md"])
```

### Soru Sorma

```python
# Basit sorgu
result = rag.query("Python nedir?")
print(result["answer"])
print(result["sources"])

# Sohbet modu
response = rag.chat("Makine öğrenmesi türleri nelerdir?")
print(response)
```

## Mimari

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Belgeler  │────▶│  Splitter    │────▶│  Embedder   │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
                                                ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  MiniMax-M2 │◀────│  Bağlam      │◀────│  ChromaDB   │
└─────────────┘     └──────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│    Yanıt    │
└─────────────┘
```

## Yapılandırma

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `chunk_size` | Parça boyutu (karakter) | 500 |
| `chunk_overlap` | Parçalar arası örtüşme | 50 |
| `top_k` | Döndürülecek belge sayısı | 5 |
| `embedding_model` | Embedding modeli | all-MiniLM-L6-v2 |

## İpuçları

1. **Küçük Parçalar**: Daha kesin eşleşmeler için küçük parçalar kullanın
2. **Örtüşme**: Bağlam kaybını önlemek için örtüşme ekleyin
3. **Kaynak Takibi**: Her belgeye anlamlı kaynak isimleri verin
4. **Düşük Sıcaklık**: Daha tutarlı yanıtlar için temperature=0.3 kullanın
