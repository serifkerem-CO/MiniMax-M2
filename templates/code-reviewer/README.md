# MiniMax-M2 Kod İnceleme Şablonu

AI destekli kod inceleme ve kalite analizi aracı.

## Özellikler

- **Kod Kalitesi**: Okunabilirlik, best practice kontrolleri
- **Güvenlik Taraması**: OWASP güvenlik açıkları tespiti
- **Performans Analizi**: Optimizasyon önerileri
- **Git Diff İnceleme**: PR/commit değişiklik analizi

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
# Dosya incele
python main.py review file.py

# Güvenlik odaklı inceleme
python main.py review file.py --focus security

# Git diff incele
python main.py diff HEAD~1

# Güvenlik taraması
python main.py security src/

# Demo
python main.py demo
```

## İnceleme Türleri

| Odak | Açıklama |
|------|----------|
| general | Genel kod kalitesi |
| security | Güvenlik açıkları |
| performance | Performans sorunları |
| style | Kod stili |

## Örnek Çıktı

```
📝 MiniMax-M2 Code Review
Dil: python | Puan: 75/100

Bulunan Sorunlar:
| Seviye   | Kategori | Satır | Mesaj                    |
|----------|----------|-------|--------------------------|
| critical | security | 5     | Hardcoded şifre tespit   |
| warning  | quality  | 12    | Fonksiyon çok uzun       |

Öneriler:
1. Satır 5: Şifreleri ortam değişkeninde saklayın
2. Satır 12: Fonksiyonu küçük parçalara bölün
```
