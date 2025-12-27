# MiniMax-M2 Jupyter Notebook Örnekleri

MiniMax-M2'yi öğrenmek için interaktif notebook'lar.

## Notebook'lar

| Notebook | Açıklama | Seviye |
|----------|----------|--------|
| 01_getting_started.ipynb | Temel kullanım | Başlangıç |
| 02_tool_calling.ipynb | Araç/fonksiyon çağırma | Orta |

## Kurulum

```bash
pip install jupyter openai

# Jupyter başlat
jupyter notebook
```

## İçerikler

### 01 - Getting Started
- API istemcisi oluşturma
- Basit sorgular
- Streaming yanıtlar
- Sohbet geçmişi
- Parametre ayarlama

### 02 - Tool Calling
- Araç tanımlama
- Araç çağrısı algılama
- Fonksiyon uygulama
- Sonuç işleme

## Yapılandırma

Her notebook'un başında yapılandırma hücresi vardır:

```python
API_BASE_URL = "http://localhost:8000/v1"
API_KEY = "your-api-key-here"
MODEL_NAME = "MiniMax-M2"
```

## Google Colab'da Çalıştırma

1. Notebook'u Colab'a yükleyin
2. İlk hücrede bağımlılıkları yükleyin:
   ```python
   !pip install openai -q
   ```
3. API anahtarınızı girin

## İpuçları

- Her hücreyi sırayla çalıştırın
- Hataları anlamak için çıktıları okuyun
- Kendi örneklerinizi deneyin
