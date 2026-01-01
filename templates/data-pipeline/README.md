# MiniMax-M2 Data Pipeline Şablonu

AI destekli veri işleme pipeline'ı.

## Özellikler

- **ETL İşlemleri**: Extract, Transform, Load
- **AI Dönüşümler**: Akıllı veri temizleme ve zenginleştirme
- **Çoklu Format**: CSV, JSON, Parquet, Excel, DuckDB
- **Checkpoint**: Kesintisiz işleme, kaldığı yerden devam
- **Paralel İşleme**: Yüksek performans

## Kurulum

```bash
pip install -r requirements.txt
```

## Hızlı Başlangıç

### CLI Kullanımı

```bash
# Basit dönüşüm
python main.py -i data.csv -o output.csv --drop-null --dedupe

# AI ile temizleme
python main.py -i data.csv -o clean.csv --clean ad sehir

# AI ile dönüşüm
python main.py -i data.csv -o result.json --transform "normalize et ve hataları düzelt"
```

### API Kullanımı

```python
from main import PipelineBuilder, get_source

# Pipeline oluştur
pipeline = (
    PipelineBuilder("my-pipeline")
    .drop_null()
    .deduplicate(["email"])
    .ai_clean("ad", "sehir")
    .ai_enrich("özet oluştur", "ozet", ["baslik", "icerik"])
    .sort("tarih")
    .build()
)

# Çalıştır
source = get_source("input.csv")
target = get_source("output.parquet")
result = pipeline.run(source, target)
```

## Dönüşüm Adımları

### Temel Dönüşümler

```python
pipeline = (
    PipelineBuilder("temel")
    .drop_null()                     # Null satırları kaldır
    .fill_null(value=0)              # Null değerleri doldur
    .rename(old_name="new_name")     # Sütun adı değiştir
    .select("col1", "col2", "col3")  # Sütun seç
    .filter(lambda df: df["yas"] > 18)  # Filtrele
    .cast(yas=int, fiyat=float)      # Tip dönüşümü
    .deduplicate(["id"])             # Tekrarları kaldır
    .sort("tarih", ascending=False)  # Sırala
    .build()
)
```

### AI Dönüşümleri

```python
pipeline = (
    PipelineBuilder("ai-pipeline")

    # AI ile toplu dönüşüm
    .ai_transform("adresleri normalize et ve il/ilçe ayır")

    # AI ile yeni sütun oluştur
    .ai_enrich(
        instruction="kısa özet oluştur",
        new_column="ozet",
        source_columns=["baslik", "icerik"]
    )

    # AI ile temizleme
    .ai_clean("ad", "soyad", "adres")

    .build()
)
```

### Özel Dönüşümler

```python
def custom_transform(df):
    df["tam_ad"] = df["ad"] + " " + df["soyad"]
    df["yil"] = pd.to_datetime(df["tarih"]).dt.year
    return df

pipeline = (
    PipelineBuilder("custom")
    .transform(custom_transform)
    .build()
)
```

## Veri Kaynakları

### Desteklenen Formatlar

| Format | Uzantı | Okuma | Yazma |
|--------|--------|-------|-------|
| CSV | .csv | ✅ | ✅ |
| JSON | .json | ✅ | ✅ |
| Parquet | .parquet | ✅ | ✅ |
| Excel | .xlsx, .xls | ✅ | ✅ |
| DuckDB | .duckdb, .db | ✅ | ✅ |

### Özel Kaynak

```python
from main import DataSource

class APISource(DataSource):
    def __init__(self, url):
        self.url = url

    def read(self):
        response = requests.get(self.url)
        return pd.DataFrame(response.json())

    def write(self, df):
        requests.post(self.url, json=df.to_dict(orient="records"))
```

## Checkpoint Sistemi

```python
# Checkpoint etkin (varsayılan)
pipeline = PipelineBuilder("long-running").config(
    checkpoint_enabled=True,
    checkpoint_dir=".checkpoints"
).build()

# Kaldığı yerden devam
result = pipeline.run(source, target, resume=True)

# Baştan başla
result = pipeline.run(source, target, resume=False)
```

## Yapılandırma

### Ortam Değişkenleri

```bash
# API
export MINIMAX_API_BASE="http://localhost:8000/v1"
export MINIMAX_API_KEY="your-api-key"
export MINIMAX_MODEL="MiniMax-M2"

# Pipeline
export PIPELINE_BATCH_SIZE="100"
export PIPELINE_MAX_WORKERS="4"
export PIPELINE_CHECKPOINT_DIR=".checkpoints"
```

### Programatik Yapılandırma

```python
pipeline = (
    PipelineBuilder("configured")
    .config(
        batch_size=50,
        max_workers=8,
        checkpoint_enabled=True,
        retry_count=5
    )
    .build()
)
```

## Örnek Senaryolar

### E-ticaret Veri Temizleme

```python
pipeline = (
    PipelineBuilder("ecommerce-clean")
    .drop_null(["urun_adi", "fiyat"])
    .deduplicate(["sku"])
    .ai_clean("urun_adi", "kategori")
    .ai_enrich("SEO açıklaması yaz", "seo_desc", ["urun_adi", "ozellikler"])
    .filter(lambda df: df["fiyat"] > 0)
    .sort("kategori", "urun_adi")
    .build()
)
```

### Log Analizi

```python
pipeline = (
    PipelineBuilder("log-analysis")
    .filter(lambda df: df["level"] == "ERROR")
    .ai_transform("hata mesajlarını kategorize et")
    .ai_enrich("çözüm önerisi", "suggestion", ["error_message", "stack_trace"])
    .sort("timestamp", ascending=False)
    .build()
)
```

### Müşteri Verisi Birleştirme

```python
def merge_sources(df):
    # Birden fazla kaynaktan gelen veriyi birleştir
    df = df.groupby("musteri_id").agg({
        "ad": "first",
        "email": "first",
        "toplam_harcama": "sum",
        "siparis_sayisi": "sum"
    }).reset_index()
    return df

pipeline = (
    PipelineBuilder("customer-merge")
    .drop_null(["musteri_id"])
    .transform(merge_sources)
    .ai_enrich("müşteri segmenti", "segment", ["toplam_harcama", "siparis_sayisi"])
    .build()
)
```

## CLI Referans

```bash
# Temel kullanım
python main.py -i input.csv -o output.csv

# Null temizleme
python main.py -i data.csv --drop-null

# Tekrar temizleme
python main.py -i data.csv --dedupe
python main.py -i data.csv --dedupe email ad

# AI temizleme
python main.py -i data.csv --clean ad sehir adres

# AI dönüşüm
python main.py -i data.csv --transform "normalize et"

# Demo
python main.py --demo
```
