# Ders 3: Rust Fundamentals 🦀

**Zorluk:** ⭐⭐⭐
**Puan:** 111
**Süre:** ~3 saat

## 📚 Öğrenme Hedefleri

Bu derste şunları öğreneceksin:
- Rust'ın ownership sistemi
- Borrowing ve references
- Pattern matching
- Error handling (Result & Option)
- Struct ve impl blokları

## 🎯 Giriş

Rust, performans ve güvenliği bir arada sunan sistem programlama dili. Memory safety'yi compile-time'da garanti eder - garbage collector olmadan!

## 💡 Rust'a Giriş

### 1. Değişkenler ve Mutability

```rust
fn main() {
    // Immutable (varsayılan)
    let puan = 111;
    // puan = 222; // HATA! Değiştirilemez

    // Mutable
    let mut degisebilen_puan = 111;
    degisebilen_puan = 222; // OK

    // Shadowing
    let x = 5;
    let x = x + 1; // OK (yeni değişken)
    let x = x * 2;
    println!("x: {}", x); // 12

    // Type annotations
    let sayi: i32 = 111;
    let metin: &str = "B1Z KODLAB";
}
```

### 2. Ownership - Rust'ın Süper Gücü!

```rust
fn main() {
    // String heap'te saklanır
    let s1 = String::from("B1Z KODLAB");

    // s1'in ownership'i s2'ye taşındı (move)
    let s2 = s1;
    // println!("{}", s1); // HATA! s1 artık geçersiz

    // Clone ile kopyalama
    let s3 = s2.clone();
    println!("s2: {}, s3: {}", s2, s3); // OK

    // Fonksiyona ownership verme
    let s4 = String::from("Merhaba");
    ownership_ver(s4);
    // println!("{}", s4); // HATA! Ownership alındı
}

fn ownership_ver(s: String) {
    println!("{}", s);
    // s burada drop edilir
}
```

### 3. Borrowing ve References

```rust
fn main() {
    let s1 = String::from("B1Z KODLAB");

    // Immutable borrow
    let uzunluk = hesapla_uzunluk(&s1);
    println!("'{}' uzunluğu: {}", s1, uzunluk); // s1 hala kullanılabilir!

    // Mutable borrow
    let mut metin = String::from("Merhaba");
    degistir(&mut metin);
    println!("{}", metin); // "Merhaba, Dünya!"
}

fn hesapla_uzunluk(s: &String) -> usize {
    s.len() // Ownership almadı, sadece ödünç aldı
}

fn degistir(s: &mut String) {
    s.push_str(", Dünya!");
}
```

### 4. Struct ve Implementasyon

```rust
// Struct tanımlama
struct Ogrenci {
    isim: String,
    puan: u32,
    level: u8,
    aktif: bool,
}

// Implementation block
impl Ogrenci {
    // Associated function (constructor gibi)
    fn yeni(isim: String) -> Self {
        Self {
            isim,
            puan: 0,
            level: 1,
            aktif: true,
        }
    }

    // Method (self alır)
    fn puan_ekle(&mut self, miktar: u32) {
        self.puan += miktar;
        self.level_guncelle();
    }

    fn level_guncelle(&mut self) {
        self.level = (self.puan / 111) as u8 + 1;
    }

    fn bilgi_goster(&self) {
        println!(
            "{} - Puan: {}, Level: {}",
            self.isim, self.puan, self.level
        );
    }
}

fn main() {
    let mut ogrenci = Ogrenci::yeni(String::from("Şerif"));
    ogrenci.puan_ekle(222);
    ogrenci.bilgi_goster(); // Şerif - Puan: 222, Level: 3
}
```

## 🔍 Pattern Matching

```rust
fn main() {
    let puan = 111;

    // Match expression
    match puan {
        1111 => println!("Mükemmel! 🏆"),
        111..=999 => println!("Harika! 🎉"),
        1..=110 => println!("İyi gidiyorsun! 🚀"),
        _ => println!("Devam et! 💪"),
    }

    // Enum ile pattern matching
    enum KodDili {
        Python,
        JavaScript,
        Rust,
        Go,
    }

    let dil = KodDili::Rust;

    match dil {
        KodDili::Rust => println!("En iyisi! 🦀"),
        KodDili::Python => println!("Basit ve güçlü! 🐍"),
        KodDili::JavaScript => println!("Web'in kralı! 🟨"),
        KodDili::Go => println!("Hızlı ve efektif! 🐹"),
    }
}
```

## ⚠️ Error Handling: Result & Option

```rust
use std::fs::File;
use std::io::Read;

// Option<T> - Değer olabilir veya olmayabilir
fn ara(liste: &[i32], hedef: i32) -> Option<usize> {
    for (index, &item) in liste.iter().enumerate() {
        if item == hedef {
            return Some(index);
        }
    }
    None
}

// Result<T, E> - Başarı veya hata
fn dosya_oku(yol: &str) -> Result<String, std::io::Error> {
    let mut dosya = File::open(yol)?; // ? operator
    let mut icerik = String::new();
    dosya.read_to_string(&mut icerik)?;
    Ok(icerik)
}

fn main() {
    // Option kullanımı
    let sayilar = vec![1, 2, 3, 5, 8, 13];

    match ara(&sayilar, 5) {
        Some(index) => println!("Bulundu! Index: {}", index),
        None => println!("Bulunamadı!"),
    }

    // if let ile kısa yol
    if let Some(index) = ara(&sayilar, 8) {
        println!("8 bulundu: {}", index);
    }

    // Result kullanımı
    match dosya_oku("test.txt") {
        Ok(icerik) => println!("Dosya içeriği: {}", icerik),
        Err(hata) => println!("Hata: {}", hata),
    }
}
```

## 🏋️ Alıştırmalar

### Alıştırma 1: Ownership Challenge

```rust
// Bu kodu düzelt!
fn main() {
    let s = String::from("B1Z KODLAB");
    yazdir(s);
    yazdir(s); // HATA! Nasıl düzeltirsin?
}

fn yazdir(s: String) {
    println!("{}", s);
}
```

### Alıştırma 2: Struct ile B1Z Öğrenci Sistemi

```rust
struct B1zOgrenci {
    // Alanları ekle
}

impl B1zOgrenci {
    // Constructor
    fn yeni(isim: String) -> Self {
        // ???
    }

    // Ders tamamla
    fn ders_tamamla(&mut self, ders_no: u8) {
        // Her ders 111 puan
        // 11. ders 1111 puan
        // ???
    }

    // Seviye hesapla
    fn seviye(&self) -> u8 {
        // ???
    }
}

fn main() {
    let mut ogrenci = B1zOgrenci::yeni(String::from("Şerif"));
    ogrenci.ders_tamamla(1);
    ogrenci.ders_tamamla(2);
    println!("Puan: {}, Seviye: {}", ogrenci.puan, ogrenci.seviye());
}
```

### Alıştırma 3: Error Handling

```rust
// Fibonacci hesapla, hatalı girişleri Result ile handle et
fn fibonacci_guvenli(n: i32) -> Result<u64, String> {
    // n negatif ise Err dön
    // n > 93 ise overflow hatası ver
    // Normal durumda fibonacci hesapla
    // ???
}

fn main() {
    match fibonacci_guvenli(10) {
        Ok(sonuc) => println!("Fibonacci(10) = {}", sonuc),
        Err(hata) => println!("Hata: {}", hata),
    }

    match fibonacci_guvenli(-5) {
        Ok(sonuc) => println!("Sonuç: {}", sonuc),
        Err(hata) => println!("Hata: {}", hata), // "Negatif sayı!"
    }
}
```

## 🎯 Challenge: Mini Vektör Kütüphanesi

Generic bir MiniVektor struct'ı implement et:

```rust
struct MiniVektor<T> {
    elemanlar: Vec<T>,
}

impl<T> MiniVektor<T> {
    fn yeni() -> Self {
        // ???
    }

    fn ekle(&mut self, eleman: T) {
        // ???
    }

    fn uzunluk(&self) -> usize {
        // ???
    }

    fn al(&self, index: usize) -> Option<&T> {
        // ???
    }
}

// Bonus: Display trait implement et
use std::fmt;

impl<T: fmt::Display> fmt::Display for MiniVektor<T> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // ???
    }
}

fn main() {
    let mut v = MiniVektor::yeni();
    v.ekle(111);
    v.ekle(222);
    v.ekle(1111);

    println!("Uzunluk: {}", v.uzunluk());
    if let Some(eleman) = v.al(2) {
        println!("Index 2: {}", eleman);
    }
}
```

## 🦀 Rust'ın Avantajları

1. **Memory Safety:** Compile-time'da garanti
2. **Zero-Cost Abstractions:** Performans kaybı yok
3. **Fearless Concurrency:** Thread-safe kod yazma
4. **Modern Tooling:** Cargo, rustfmt, clippy
5. **Great Documentation:** Rust Book ve docs.rs

## 📖 Ekstra Kaynaklar

- **The Rust Book:** https://doc.rust-lang.org/book/
- **Rust by Example:** https://doc.rust-lang.org/rust-by-example/
- **Rustlings:** https://github.com/rust-lang/rustlings
- **B1Z KODLAB AI:** MiniMax-M2'ye Rust soruları sor!

## ✅ Dersi Tamamla

Tüm alıştırmaları çözdüğünde **111 puan** kazanırsın! 🦀

**Önceki Ders:** ← JavaScript/TypeScript Basics
**Sonraki Ders:** Go ile Backend →

---

**B1Z KODLAB** - Kodla, Kodlat, B1Z Ol 🚀
**Rust is not just a language, it's a mindset!** 🦀
