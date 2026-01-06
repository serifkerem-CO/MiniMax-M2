# Fractal 60 Calendar API

## Proje Hakkında
Bu proje, 13 aylık (28 gün) takvim sistemi ile 60'lık (12 Hayvan x 5 Element) döngüyü birleştiren fraktal bir zaman hesaplama API'sidir.

## Kurulum ve Çalıştırma

1. Backend klasörüne git:
   ```bash
   cd backend
   ```

2. Gerekli paketleri yükle:
   ```bash
   pip install -r requirements.txt
   ```

3. Sunucuyu başlat:
   ```bash
   python main.py
   ```

4. Tarayıcıdan test et:
   - `http://localhost:8000/now` - Şu anki fraktal zamanı gösterir.
   - `http://localhost:8000/docs` - API dokümantasyonunu gösterir.

## Mimari
- **Core Logic:** `core.py` içinde 60 tabanlı matematiksel dönüşüm.
- **API:** FastAPI kullanılarak mikroservis mimarisi.

## API Endpoints

### GET /
Sistem durumunu kontrol eder.

### GET /now
Şu anki zamanı fraktal formatta döndürür.

### GET /convert/{timestamp}
Belirtilen Unix timestamp'i fraktal formata çevirir.

## Takvim Sistemi

### 13 Aylık Takvim
- Her ay 28 gün
- Yılda toplam 364 gün
- 13 ay = daha dengeli bir sistem

### 60'lık Döngü (Sexagenary Cycle)
- 12 Hayvan (Çin Zodyağı): Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, Pig
- 5 Element: Wood, Fire, Earth, Metal, Water
- 12 x 5 = 60 yıllık döngü

## Örnek Çıktı

```json
{
  "timestamp": 1735689600.0,
  "fractal": {
    "year": {
      "val": 2024,
      "signature": {
        "animal": "Dragon",
        "element": "Wood",
        "cycle_position": 40
      }
    },
    "month": {
      "val": 12,
      "signature": {
        "animal": "Rat",
        "element": "Metal",
        "cycle_position": 24
      }
    },
    "day": {
      "val": 15,
      "signature": {
        "animal": "Tiger",
        "element": "Fire",
        "cycle_position": 26
      }
    }
  }
}
```
