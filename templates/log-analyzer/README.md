# MiniMax-M2 Log Analizci Şablonu

AI destekli log analizi ve anomali tespiti aracı.

## Özellikler

- **Çoklu Format**: Apache, Nginx, Syslog, Python, Java, JSON
- **Anomali Tespiti**: Spike, yeni hata türleri
- **Root Cause Analizi**: Hata zinciri analizi
- **Desen Çıkarma**: Tekrar eden log kalıpları

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
# Genel analiz
python main.py analyze app.log

# Özel soru ile analiz
python main.py analyze app.log --question "performans sorunları neler?"

# Hata analizi
python main.py errors app.log --top 10

# Root cause analizi
python main.py errors app.log --root-cause

# Desen analizi
python main.py patterns app.log

# Anomali tespiti
python main.py anomalies app.log

# Demo
python main.py demo
```

## Desteklenen Log Formatları

| Format | Örnek |
|--------|-------|
| Apache | `127.0.0.1 - - [10/Oct/2024:13:55:36] "GET /" 200 2326` |
| Python | `2024-01-15 10:00:01 - app - INFO - Message` |
| JSON | `{"timestamp": "...", "level": "INFO", "message": "..."}` |
| Syslog | `Jan 15 10:00:01 hostname process: message` |

## Örnek Çıktı

```
📊 Log Özeti
| Seviye   | Sayı | Oran  |
|----------|------|-------|
| INFO     | 850  | %85   |
| ERROR    | 100  | %10   |
| WARN     | 50   | %5    |

⚠️ Anomalies
• [CRITICAL] spike
  Yüksek hata oranı: 100/1000 (%10)

🤖 AI Analizi
Veritabanı bağlantı sorunları tespit edildi...
```
