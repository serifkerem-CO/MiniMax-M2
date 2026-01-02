# Ders 2: JavaScript/TypeScript Basics 🟨

**Zorluk:** ⭐⭐
**Puan:** 111
**Süre:** ~2.5 saat

## 📚 Öğrenme Hedefleri

Bu derste şunları öğreneceksin:
- Modern JavaScript (ES6+) özellikleri
- Arrow functions ve destructuring
- Async/await ve Promise'ler
- TypeScript temelleri ve type annotations

## 🎯 Giriş

JavaScript, web'in programlama dili! TypeScript ise JavaScript'e tip güvenliği kazandırır. Modern web geliştirme için her ikisi de kritik öneme sahip.

## 💡 Modern JavaScript (ES6+)

### 1. Değişkenler: let, const, var

```javascript
// const: Değiştirilemez
const PLATFORM = "B1Z KODLAB";

// let: Block-scoped değişken
let puan = 111;
puan = 222; // OK

// var: Eski yöntem (kullanma!)
var eski_yontem = "Kullanma!";
```

### 2. Arrow Functions

```javascript
// Geleneksel fonksiyon
function toplam(a, b) {
  return a + b;
}

// Arrow function
const toplamArrow = (a, b) => a + b;

// Tek parametreli
const kare = x => x * x;

// Çok satırlı
const fibonacci = (n) => {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
};

console.log(toplamArrow(111, 222)); // 333
```

### 3. Template Literals

```javascript
const isim = "Şerif";
const puan = 1111;

// Template literal ile
const mesaj = `Merhaba ${isim}! Puanın: ${puan}`;
console.log(mesaj);

// Çok satırlı string
const html = `
  <div>
    <h1>B1Z KODLAB</h1>
    <p>Puan: ${puan}</p>
  </div>
`;
```

### 4. Destructuring

```javascript
// Array destructuring
const dersler = ["Python", "JavaScript", "Rust"];
const [ilk, ikinci, ucuncu] = dersler;
console.log(ilk); // Python

// Object destructuring
const ogrenci = {
  isim: "Ali",
  puan: 111,
  level: 5
};

const { isim, puan } = ogrenci;
console.log(isim, puan); // Ali 111

// Spread operator
const yeniDersler = [...dersler, "Go", "TypeScript"];
const yeniOgrenci = { ...ogrenci, puan: 222 };
```

## 🔄 Async/Await ve Promises

### 1. Promise Temelleri

```javascript
// Promise oluşturma
const kodAnalizi = new Promise((resolve, reject) => {
  setTimeout(() => {
    const basarili = true;
    if (basarili) {
      resolve({ skor: 85, mesaj: "Harika kod!" });
    } else {
      reject("Analiz başarısız");
    }
  }, 1000);
});

// Promise kullanımı
kodAnalizi
  .then(sonuc => console.log(sonuc.mesaj))
  .catch(hata => console.error(hata));
```

### 2. Async/Await

```javascript
// Async fonksiyon
async function aiAnaliz(kod) {
  try {
    // API çağrısı (simülasyon)
    const response = await fetch('/api/ai/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: kod, language: 'javascript' })
    });

    const sonuc = await response.json();
    return sonuc;
  } catch (hata) {
    console.error('AI analiz hatası:', hata);
    throw hata;
  }
}

// Kullanım
const kod = "const x = 111;";
aiAnaliz(kod)
  .then(sonuc => console.log('Skor:', sonuc.score))
  .catch(hata => console.error(hata));
```

## 📘 TypeScript Temelleri

### 1. Type Annotations

```typescript
// Basit tipler
let isim: string = "B1Z KODLAB";
let puan: number = 111;
let aktif: boolean = true;

// Array tipleri
let dersler: string[] = ["Python", "JavaScript"];
let puanlar: number[] = [111, 222, 333];

// Fonksiyon tipleri
function topla(a: number, b: number): number {
  return a + b;
}

// Optional parametreler
function selamla(isim: string, soyisim?: string): string {
  return soyisim ? `${isim} ${soyisim}` : isim;
}
```

### 2. Interfaces ve Types

```typescript
// Interface tanımlama
interface Ogrenci {
  id: number;
  isim: string;
  puan: number;
  aktif?: boolean; // Optional
}

interface Ders {
  id: number;
  baslik: string;
  dil: "python" | "javascript" | "rust"; // Union type
  zorluk: number;
}

// Type kullanımı
type KodDili = "python" | "javascript" | "typescript" | "rust" | "go";

type AIGeribildirim = {
  skor: number;
  oneriler: string[];
  hatalar: string[];
};

// Kullanım
const ogrenci: Ogrenci = {
  id: 1,
  isim: "Şerif",
  puan: 1111
};

const ders: Ders = {
  id: 2,
  baslik: "JavaScript Basics",
  dil: "javascript",
  zorluk: 2
};
```

## 🏋️ Alıştırmalar

### Alıştırma 1: Arrow Function ile Array İşlemleri

```typescript
const sayilar: number[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];

// Map, filter, reduce kullan
const kareler = // sayıların kareleri
const tekler = // tek sayılar
const toplam = // toplam

console.log(kareler);
console.log(tekler);
console.log(toplam);
```

### Alıştırma 2: Promise Zinciri

```javascript
// Ardışık işlemler için Promise zinciri oluştur
function kodYaz() {
  return new Promise(resolve => {
    setTimeout(() => resolve("Kod yazıldı"), 1000);
  });
}

function kodTest() {
  return new Promise(resolve => {
    setTimeout(() => resolve("Test geçti"), 1000);
  });
}

function kodDeploy() {
  return new Promise(resolve => {
    setTimeout(() => resolve("Deploy başarılı"), 1000);
  });
}

// Promise chain oluştur
// ???
```

### Alıştırma 3: TypeScript Interface

```typescript
// B1Z KODLAB platformu için interface'ler oluştur
interface KullaniciProfili {
  // ???
}

interface DersTamamlama {
  // ???
}

// Kullanım örneği
const profil: KullaniciProfili = {
  // ???
};
```

## 🎯 Challenge: B1Z KODLAB Mini API

Basit bir API simülasyonu yap:

```typescript
interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

async function fetchLessons(): Promise<APIResponse<Ders[]>> {
  // Simüle edilmiş API çağrısı
  // ???
}

async function analyzeCode(kod: string, dil: KodDili): Promise<APIResponse<AIGeribildirim>> {
  // Simüle edilmiş AI analizi
  // ???
}

// Kullanım
(async () => {
  const lessons = await fetchLessons();
  console.log(lessons);

  const analysis = await analyzeCode("const x = 11;", "javascript");
  console.log(analysis);
})();
```

## 📖 Ekstra Kaynaklar

- **MDN JavaScript:** https://developer.mozilla.org/en-US/docs/Web/JavaScript
- **TypeScript Handbook:** https://www.typescriptlang.org/docs/
- **JavaScript.info:** https://javascript.info/
- **B1Z KODLAB AI:** Takıldığın yerlerde MiniMax-M2'ye sor!

## ✅ Dersi Tamamla

Tüm alıştırmaları çözdüğünde **111 puan** kazanırsın! 🎉

**Önceki Ders:** ← Python Temelleri
**Sonraki Ders:** Rust Fundamentals →

---

**B1Z KODLAB** - Kodla, Kodlat, B1Z Ol 🚀
