# MiniMax-M2 Çeviri Servisi Şablonu

Profesyonel çeviri servisi.

## Özellikler

- **12 Dil Desteği**: TR, EN, DE, FR, ES, IT, PT, RU, JA, ZH, KO, AR
- **Otomatik Dil Algılama**: Kaynak dili otomatik belirler
- **Çoklu Stil**: Doğal, resmi, günlük, teknik
- **Alternatif Çeviriler**: Birden fazla çeviri seçeneği
- **Kalite Kontrolü**: Çeviri değerlendirmesi

## Kullanım

### Çeviri
```bash
# Temel çeviri
python main.py translate "Merhaba dünya" --to en

# Stilli çeviri
python main.py translate "Hello world" --to tr --style formal

# Alternatiflerle
python main.py translate "Good morning" --to tr --alternatives 3
```

### Dil Algılama
```bash
python main.py detect "Bonjour le monde"
# 🔍 Algılanan dil: French (Français) [fr]
```

### Kalite Kontrolü
```bash
python main.py check \
  --original "Merhaba dünya" \
  --translation "Hello world" \
  --from tr --to en
```

### Dil Listesi
```bash
python main.py languages
```

## Desteklenen Diller

| Kod | Dil | Native |
|-----|-----|--------|
| tr | Turkish | Türkçe |
| en | English | English |
| de | German | Deutsch |
| fr | French | Français |
| es | Spanish | Español |
| it | Italian | Italiano |
| pt | Portuguese | Português |
| ru | Russian | Русский |
| ja | Japanese | 日本語 |
| zh | Chinese | 中文 |
| ko | Korean | 한국어 |
| ar | Arabic | العربية |

## API Kullanımı

```python
from main import translate, TranslationConfig

# Basit çeviri
result = translate("Merhaba")
print(result.translated_text)

# Yapılandırmalı çeviri
config = TranslationConfig(
    source_lang="tr",
    target_lang="en",
    style="technical",
    glossary={"API": "API", "veritabanı": "database"}
)
result = translate("API veritabanına bağlanır", config)
```

## Sözlük Kullanımı

Teknik terimleri korumak için:

```python
config = TranslationConfig(
    target_lang="en",
    glossary={
        "yapay zeka": "artificial intelligence",
        "makine öğrenmesi": "machine learning",
        "derin öğrenme": "deep learning"
    }
)
```

## Kalite Değerlendirmesi

```python
from main import quality_check

result = quality_check(
    original="Merhaba dünya",
    translation="Hello world",
    source_lang="tr",
    target_lang="en"
)

print(f"Puan: {result['score']}/10")
print(f"Doğruluk: {result['accuracy']}")
```
