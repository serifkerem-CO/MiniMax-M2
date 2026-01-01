# MiniMax-M2 Web Scraper Şablonu

AI destekli akıllı web kazıma.

## Özellikler

- **Akıllı Çıkarma**: Doğal dil ile veri çıkarma
- **Sayfa Analizi**: Otomatik yapı analizi
- **Crawling**: Çoklu sayfa tarama
- **Rate Limiting**: Güvenli kazıma
- **JSON Çıktı**: Yapılandırılmış veri

## Kullanım

### Tek Sayfa Kazıma
```bash
python main.py "https://example.com"
```

### Veri Çıkarma
```bash
python main.py "https://example.com/products" --extract "ürün adı ve fiyatı"
```

### Crawling
```bash
python main.py "https://example.com" --crawl 10
```

### JSON Çıktı
```bash
python main.py "https://example.com" --output data.json
```

## API Kullanımı

### Basit Kazıma
```python
from main import WebScraper

scraper = WebScraper()
page = scraper.scrape("https://example.com")

print(page.title)
print(page.content)
print(page.links)
```

### AI ile Veri Çıkarma
```python
result = scraper.extract(
    "https://example.com/products",
    "ürün adı, fiyat ve açıklama"
)
print(result.data)
```

### Çoklu Sayfa
```python
pages = scraper.crawl(
    "https://example.com",
    max_pages=10,
    same_domain=True
)
for page in pages:
    print(page.title)
```

## Çıkarma Örnekleri

### E-ticaret
```bash
python main.py "https://shop.com/product" \
  --extract "ürün adı, fiyat, stok durumu, özellikler"
```

### Haber Sitesi
```bash
python main.py "https://news.com/article" \
  --extract "başlık, yazar, tarih, içerik özeti"
```

### İş İlanı
```bash
python main.py "https://jobs.com/listing" \
  --extract "pozisyon, şirket, maaş, gereksinimler"
```

## Rate Limiting

```python
from main import WebFetcher

fetcher = WebFetcher(
    timeout=30,
    delay=2.0  # İstekler arası bekleme
)
```

## Dikkat Edilmesi Gerekenler

1. **robots.txt**: Sitenin robots.txt dosyasına saygı gösterin
2. **Rate Limiting**: Sunucuyu yormayın
3. **Yasal**: Kullanım şartlarını kontrol edin
4. **Etik**: Kişisel verilere dikkat edin
