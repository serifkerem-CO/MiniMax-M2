# MiniMax-M2 CLI Aracı Şablonu

Komut satırından MiniMax-M2 ile etkileşim.

## Özellikler

- **İnteraktif Sohbet**: Çok turlu konuşmalar
- **Tek Seferlik Sorgular**: Hızlı sorular
- **Kod Analizi**: Dosya veya stdin'den
- **Kod Üretimi**: Açıklamadan kod
- **Çeviri & Özetleme**: Metin işleme
- **Pipe Desteği**: Unix pipe uyumlu

## Kurulum

```bash
pip install -r requirements.txt

# Ortam değişkenleri
export MINIMAX_API_BASE="http://localhost:8000/v1"
export MINIMAX_API_KEY="your-api-key"
```

## Komutlar

### Sohbet
```bash
python main.py chat
python main.py chat --temperature 0.9
```

### Soru Sor
```bash
python main.py ask "Python nedir?"
python main.py ask "Fibonacci fonksiyonu yaz" --system "Sen Python uzmanısın"
```

### Kod Analizi
```bash
# Dosyadan
python main.py analyze --file code.py

# Stdin'den
cat code.py | python main.py analyze

# Farklı analiz türleri
python main.py analyze --file code.py --type review
python main.py analyze --file code.py --type fix
python main.py analyze --file code.py --type optimize
```

### Kod Üretimi
```bash
python main.py generate "Fibonacci hesaplayan fonksiyon"
python main.py generate "REST API client" --language javascript
python main.py generate "Sorting algorithm" --output sort.py
```

### Çeviri
```bash
python main.py translate "Merhaba dünya" --to İngilizce
python main.py translate "Hello world" --to Türkçe
```

### Özetleme
```bash
python main.py summarize "Uzun metin..." --style short
python main.py summarize "Uzun metin..." --style long
```

## Pipe Kullanımı

```bash
# Kod analizi
cat mycode.py | python main.py analyze

# Çeviri
echo "Hello world" | python main.py translate --to Türkçe

# Zincirleme
python main.py generate "Hello world" | python main.py analyze
```

## Alias Oluşturma

```bash
# .bashrc veya .zshrc'ye ekleyin
alias mm="python /path/to/main.py"

# Kullanım
mm chat
mm ask "Soru"
mm analyze --file code.py
```

## Global Kurulum

```bash
pip install -e .
minimax chat
```
