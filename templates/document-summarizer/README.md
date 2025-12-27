# MiniMax-M2 Belge Özetleme Şablonu

Uzun belgeleri akıllıca özetleyen sistem.

## Özellikler

- **Uzun Belge Desteği**: Hiyerarşik özetleme
- **Çoklu Format**: PDF, TXT, MD
- **Farklı Stiller**: Paragraf, madde, yönetici, akademik
- **Dil Desteği**: Türkçe, İngilizce
- **Odak Modu**: Belirli konulara odaklanma

## Kullanım

### Temel Kullanım
```bash
python main.py document.pdf
python main.py article.txt
```

### Seçenekler
```bash
# Madde işaretli kısa özet
python main.py doc.pdf --style bullet --length short

# İngilizce yönetici özeti
python main.py report.pdf --style executive --language en

# Belirli konuya odaklanma
python main.py research.pdf --focus "sonuçlar ve öneriler"

# Dosyaya kaydet
python main.py doc.pdf --output summary.md
```

### Stdin'den Okuma
```bash
cat article.txt | python main.py
```

## Özet Stilleri

| Stil | Açıklama |
|------|----------|
| paragraph | Akıcı paragraflar |
| bullet | Madde işaretli liste |
| executive | Yönetici özeti |
| academic | Akademik format |

## Uzunluk Seçenekleri

| Uzunluk | Açıklama |
|---------|----------|
| short | 2-3 cümle / 3-5 madde |
| medium | 1 paragraf / 5-10 madde |
| long | 2-3 paragraf / 10-15 madde |

## Hiyerarşik Özetleme

Uzun belgeler için:

```
┌─────────────────────────────────────┐
│           Uzun Belge                │
└──────────────┬──────────────────────┘
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
   ┌───────┐ ┌───────┐ ┌───────┐
   │Parça 1│ │Parça 2│ │Parça 3│
   └───┬───┘ └───┬───┘ └───┬───┘
       │         │         │
       ▼         ▼         ▼
   ┌───────┐ ┌───────┐ ┌───────┐
   │Özet 1 │ │Özet 2 │ │Özet 3 │
   └───┬───┘ └───┬───┘ └───┬───┘
       │         │         │
       └────────┬┴─────────┘
                │
                ▼
         ┌─────────────┐
         │ Final Özet  │
         └─────────────┘
```

## API Kullanımı

```python
from main import summarize_document, SummaryConfig

text = open("document.txt").read()

config = SummaryConfig(
    style="bullet",
    length="medium",
    language="tr",
    focus="ana bulgular"
)

result = summarize_document(text, config)
print(result.summary)
print(f"Sıkıştırma: {result.compression_ratio:.1%}")
```
