# MiniMax-M2 Test Üretici Şablonu

AI destekli otomatik test üretimi aracı.

## Özellikler

- **Unit Test Üretimi**: Fonksiyon/sınıf için otomatik test
- **Edge Case Tespiti**: Sınır değerler ve özel durumlar
- **Çoklu Framework**: pytest, unittest desteği
- **Kapsam Analizi**: Test coverage değerlendirmesi

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
# Dosya için test üret
python main.py generate file.py

# Belirli fonksiyon için test
python main.py generate file.py --function calculate_total

# Test dosyası oluştur
python main.py generate file.py --output test_file.py

# unittest formatında
python main.py generate file.py --framework unittest

# Kapsam analizi
python main.py coverage file.py

# Demo
python main.py demo
```

## Test Kategorileri

| Kategori | Açıklama |
|----------|----------|
| unit | Normal kullanım testleri |
| edge | Sınır değer testleri |
| error | Hata durumu testleri |
| integration | Entegrasyon testleri |

## Örnek

```python
# Kaynak kod
def calculate_discount(price: float, percent: float) -> float:
    if price < 0:
        raise ValueError("Fiyat negatif olamaz")
    return price * (1 - percent / 100)

# Üretilen testler
def test_calculate_discount_normal():
    assert calculate_discount(100, 10) == 90.0

def test_calculate_discount_zero_percent():
    assert calculate_discount(100, 0) == 100.0

def test_calculate_discount_negative_price():
    with pytest.raises(ValueError):
        calculate_discount(-100, 10)
```
