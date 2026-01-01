# MiniMax-M2 Ses Asistanı Şablonu

Sesle etkileşimli AI asistanı.

## Özellikler

- **Konuşma Tanıma**: Google Speech API
- **Metin Sentezi**: pyttsx3
- **Sürekli Dinleme**: Hands-free kullanım
- **Wake Word**: Özelleştirilebilir aktivasyon kelimesi
- **Metin Modu**: Ses donanımı olmadan çalışma

## Kurulum

### Temel
```bash
pip install -r requirements.txt
```

### macOS
```bash
brew install portaudio
pip install pyaudio
```

### Linux
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### Windows
```bash
pip install pyaudio
```

## Kullanım

```bash
python main.py
```

## Modlar

### Sesli Mod
- Mikrofonu dinler
- Konuşmayı metne çevirir
- AI yanıtını seslendirir

### Metin Modu
- Klavyeden giriş
- Ses donanımı gerektirmez
- Test ve geliştirme için ideal

## Yapılandırma

```bash
# Ortam değişkenleri
export WAKE_WORD="hey max"
export LANGUAGE="tr-TR"
export VOICE_RATE="150"
```

## Sesli Komutlar

| Komut | İşlev |
|-------|-------|
| "kapat" / "dur" | Asistanı kapat |
| "temizle" | Sohbet geçmişini sil |

## API Kullanımı

```python
from main import VoiceAssistant, VoiceConfig

config = VoiceConfig(
    language="tr-TR",
    voice_rate=150,
    wake_word="hey max"
)

assistant = VoiceAssistant(config)

# Sürekli dinleme
assistant.run_continuous()

# Tek seferlik
response = assistant.run_once("Hava durumu nasıl?")
```

## Ses Olmadan Kullanım

```python
from main import TextVoiceAssistant

assistant = TextVoiceAssistant()
response = assistant.chat("Merhaba!")
print(response)
```

## Sorun Giderme

### "No module named 'pyaudio'"
```bash
# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Mikrofon bulunamadı
- Mikrofon izinlerini kontrol edin
- Varsayılan mikrofonu ayarlayın
