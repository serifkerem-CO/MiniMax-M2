# MiniMax-M2 Gradio Web UI Şablonu

Tarayıcı tabanlı interaktif web arayüzü.

## Özellikler

- **Sohbet**: Streaming sohbet arayüzü
- **Kod Analizi**: Kod açıklama, inceleme, düzeltme
- **Kod Üretimi**: Açıklamadan kod oluşturma
- **Özetleme**: Metin özetleme
- **Çeviri**: Çoklu dil çevirisi

## Hızlı Başlangıç

1. Bağımlılıkları yükle:
```bash
pip install -r requirements.txt
```

2. Ortam değişkenlerini ayarla:
```bash
export MINIMAX_API_BASE="http://localhost:8000/v1"
export MINIMAX_API_KEY="your-api-key"
```

3. Çalıştır:
```bash
python main.py
```

4. Tarayıcıda aç: http://localhost:7860

## Ekran Görüntüsü

```
┌─────────────────────────────────────────┐
│  🤖 MiniMax-M2 Web Arayüzü              │
├─────────────────────────────────────────┤
│ [💬 Sohbet] [🔍 Kod Analizi] [✨ Üretim]│
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐│
│  │ Chatbot görüntüsü                   ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│  [Mesajınız...                    ] [📤]│
└─────────────────────────────────────────┘
```

## Sekmeler

### 💬 Sohbet
- Streaming yanıtlar
- Özelleştirilebilir sistem promptu
- Sıcaklık ve token ayarları

### 🔍 Kod Analizi
- Kod açıklama
- Kod inceleme
- Hata düzeltme
- Optimizasyon

### ✨ Kod Üretimi
- Doğal dil açıklamasından kod
- Çoklu dil desteği

### 📝 Özetleme
- Farklı stiller (resmi, günlük, teknik)
- Ayarlanabilir uzunluk

### 🌍 Çeviri
- 7 dil desteği
- İki yönlü çeviri

## Public Paylaşım

Gradio'nun share özelliği ile herkese açık link oluşturabilirsiniz:

```python
demo.launch(share=True)
```

## Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
EXPOSE 7860
CMD ["python", "main.py"]
```

## Özelleştirme

Tema değiştirme:
```python
gr.Blocks(theme=gr.themes.Monochrome())  # Veya: Soft, Glass, Default
```
