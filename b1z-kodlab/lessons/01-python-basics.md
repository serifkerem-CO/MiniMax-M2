# Ders 1: Python Temelleri 🐍

**Zorluk:** ⭐
**Puan:** 111
**Süre:** ~2 saat

## 📚 Öğrenme Hedefleri

Bu derste şunları öğreneceksin:
- Python'da değişkenler ve veri tipleri
- Kontrol yapıları (if/else, loops)
- Fonksiyonlar ve parametreler
- Liste ve dictionary kullanımı

## 🎯 Giriş

Python, öğrenmesi kolay ama güçlü bir programlama dilidir. Web geliştirmeden yapay zeka uygulamalarına kadar geniş bir kullanım alanı vardır.

## 💡 Temel Kavramlar

### 1. Değişkenler ve Veri Tipleri

```python
# Değişken tanımlama
isim = "B1Z KODLAB"
sayi = 111
ondalik = 3.14
dogru_mu = True

# Veri tipi öğrenme
print(type(isim))  # <class 'str'>
print(type(sayi))  # <class 'int'>
```

### 2. Listeler ve Dictionary

```python
# Liste oluşturma
dersler = ["Python", "JavaScript", "Rust"]
print(dersler[0])  # Python

# Liste metodları
dersler.append("Go")
dersler.remove("Rust")

# Dictionary
ogrenci = {
    "isim": "Şerif",
    "puan": 1111,
    "level": 11
}
print(ogrenci["puan"])  # 1111
```

### 3. Kontrol Yapıları

```python
# If-else
puan = 111

if puan >= 1111:
    print("Mükemmel! 🎉")
elif puan >= 111:
    print("İyi gidiyorsun! 🚀")
else:
    print("Devam et! 💪")

# For döngüsü
for i in range(11):
    print(f"Sayı: {i}")

# While döngüsü
sayac = 0
while sayac < 11:
    print(sayac)
    sayac += 1
```

### 4. Fonksiyonlar

```python
def selamla(isim):
    """Kullanıcıyı selamlar"""
    return f"Merhaba, {isim}! B1Z KODLAB'a hoş geldin! 🚀"

# Fonksiyon çağırma
mesaj = selamla("Şerif")
print(mesaj)

# Varsayılan parametreli fonksiyon
def toplam_hesapla(a, b=0):
    return a + b

print(toplam_hesapla(10))      # 10
print(toplam_hesapla(10, 5))   # 15
```

## 🏋️ Alıştırmalar

### Alıştırma 1: Fibonacci Dizisi

Fibonacci dizisinin ilk 11 elemanını hesaplayan bir fonksiyon yaz.

```python
def fibonacci(n):
    """İlk n fibonacci sayısını hesapla"""
    # Kodunu buraya yaz
    pass

# Test
print(fibonacci(11))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

**Beklenen Çıktı:** `[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]`

### Alıştırma 2: Asal Sayı Kontrolü

Verilen bir sayının asal olup olmadığını kontrol eden fonksiyon yaz.

```python
def asal_mi(sayi):
    """Sayının asal olup olmadığını kontrol et"""
    # Kodunu buraya yaz
    pass

# Test
print(asal_mi(11))   # True
print(asal_mi(111))  # False
```

### Alıştırma 3: Liste Comprehension

1'den 11'e kadar olan sayıların karelerini liste comprehension ile hesapla.

```python
# Kodunu buraya yaz
kareler = # ???

print(kareler)  # [1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121]
```

## 🎯 Challenge: B1Z Puan Hesaplayıcı

Öğrencilerin toplam puanını hesaplayan bir program yaz:

```python
ogrenciler = [
    {"isim": "Ali", "tamamlanan_dersler": 5},
    {"isim": "Ayşe", "tamamlanan_dersler": 11},
    {"isim": "Mehmet", "tamamlanan_dersler": 3}
]

def toplam_puan_hesapla(ogrenciler):
    """
    Her ders 111 puan değerinde
    11. ders 1111 puan değerinde
    """
    # Kodunu buraya yaz
    pass

# Test
for ogrenci in ogrenciler:
    puan = toplam_puan_hesapla([ogrenci])
    print(f"{ogrenci['isim']}: {puan} puan")
```

## 📖 Ekstra Kaynaklar

- **Python Official Docs:** https://docs.python.org/3/
- **B1Z KODLAB Python Örnekleri:** Platformdaki kod örneklerini incele
- **MiniMax-M2 AI:** Takıldığın yerlerde AI'ya sor!

## ✅ Dersi Tamamla

Tüm alıştırmaları çözdüğünde **111 puan** kazanırsın! 🎉

**Sonraki Ders:** JavaScript/TypeScript Basics →

---

**B1Z KODLAB** - Kodla, Kodlat, B1Z Ol 🚀
