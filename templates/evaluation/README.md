# MiniMax-M2 Değerlendirme ve Benchmark Şablonu

Model performansını değerlendirmek için araçlar.

## Özellikler

- **Test Setleri**: Özel test vakaları oluşturma
- **Metrikler**: Çeşitli doğruluk metrikleri
- **Performans**: Gecikme ve throughput ölçümü
- **Raporlama**: JSON ve görsel raporlar
- **Paralel Çalıştırma**: Hızlı değerlendirme

## Hızlı Başlangıç

1. Bağımlılıkları yükle:
```bash
pip install -r requirements.txt
```

2. Değerlendirmeyi çalıştır:
```bash
python main.py
```

## Metrikler

| Metrik | Açıklama |
|--------|----------|
| `exact` | Tam metin eşleşmesi |
| `contains` | Beklenen metin içeriyor mu |
| `keyword` | Anahtar kelimelerin varlığı |
| `code_exec` | Kod çalıştırma sonucu (dikkatli) |

## Test Vakası Oluşturma

```python
from main import TestCase, BenchmarkEngine

tests = [
    TestCase(
        id="test_1",
        prompt="2 + 2 kaçtır?",
        expected="4",
        category="math"
    ),
    TestCase(
        id="test_2",
        prompt="Python'da liste nasıl oluşturulur?",
        expected="list,[,]",
        category="code"
    ),
]

engine = BenchmarkEngine()
report = engine.run_benchmark(tests, metric="contains")
engine.print_report(report)
```

## Rapor Çıktıları

### Konsol Raporu
```
============================================================
📊 BENCHMARK RAPORU
============================================================
Model: MiniMax-M2
Tarih: 2024-01-15T10:30:00
------------------------------------------------------------
Toplam Test:      100
Başarılı:         98
Başarısız:        2
Başarı Oranı:     98.0%
------------------------------------------------------------
Ortalama Gecikme: 450ms
P50 Gecikme:      420ms
P90 Gecikme:      680ms
P99 Gecikme:      1200ms
------------------------------------------------------------
Toplam Token:     50000
Token/Saniye:     111.1
------------------------------------------------------------
Doğruluk:         92.5%
============================================================
```

### JSON Raporu
```json
{
  "model_name": "MiniMax-M2",
  "timestamp": "2024-01-15T10:30:00",
  "total_tests": 100,
  "successful_tests": 98,
  "avg_latency_ms": 450.5,
  "accuracy": 0.925,
  "results": [...]
}
```

## Özel Değerlendirme

### Paralel Çalıştırma
```python
report = engine.run_benchmark(
    tests,
    concurrent=5,  # 5 paralel istek
    temperature=0.1
)
```

### Özel Metrik
```python
def my_metric(response: str, expected: str) -> float:
    # Özel skor hesaplama
    return score

METRICS["custom"] = my_metric
report = engine.run_benchmark(tests, metric="custom")
```

### Dosyadan Test Yükleme
```python
import json

with open("tests.json") as f:
    data = json.load(f)

tests = [TestCase(**item) for item in data]
```

## Görselleştirme

```python
# Gecikme grafiği
engine.plot_latencies(report, "latency.png")
```

## Kategori Bazlı Analiz

```python
results_by_category = {}
for r in report.results:
    cat = tests_dict[r["test_id"]].category
    results_by_category.setdefault(cat, []).append(r["score"])

for cat, scores in results_by_category.items():
    print(f"{cat}: {sum(scores)/len(scores)*100:.1f}%")
```
