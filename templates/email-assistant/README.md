# MiniMax-M2 Email Asistanı Şablonu

AI destekli email işleme ve yanıtlama.

## Özellikler

- **Email Analizi**: Kategori, duygu, öncelik
- **Otomatik Yanıt**: Farklı tonlarda yanıt önerileri
- **Özetleme**: Gelen kutusu özeti
- **Email Oluşturma**: Açıklamadan email taslağı
- **Spam Tespiti**: Spam sınıflandırma

## Kullanım

### Demo Modu
```bash
python main.py --demo
```

### Gerçek Email İşlemleri
```bash
# .env dosyasını yapılandırın
cp .env.example .env

# Email'leri al ve analiz et
python main.py
```

## Email Analizi

```python
from main import EmailAssistant, Email

assistant = EmailAssistant()

email = Email(
    id="1",
    sender="boss@company.com",
    recipient="me@company.com",
    subject="Acil: Rapor Gerekli",
    body="Yarına kadar raporu tamamlamanız gerekiyor...",
    date="2024-01-15"
)

analysis = assistant.analyze_email(email)
print(f"Kategori: {analysis.category}")  # urgent
print(f"Öncelik: {analysis.priority}")    # high
print(f"Yanıt gerekli: {analysis.requires_response}")  # True
```

## Yanıt Oluşturma

```python
# Profesyonel yanıt
reply = assistant.generate_reply(email, tone="professional")

# Samimi yanıt
reply = assistant.generate_reply(email, tone="friendly")

# Kısa yanıt
reply = assistant.generate_reply(email, tone="brief")
```

## Email Oluşturma

```python
new_email = assistant.compose_email(
    description="Müşteriye teslimat gecikmesi hakkında özür emaili",
    recipient="customer@example.com"
)

print(new_email["subject"])
print(new_email["body"])
```

## Kategoriler

| Kategori | Açıklama |
|----------|----------|
| work | İş emaili |
| personal | Kişisel |
| marketing | Pazarlama/reklam |
| spam | Spam |
| urgent | Acil |

## Gmail Yapılandırması

1. Google hesabında 2FA aktifleştirin
2. App Password oluşturun:
   - Google Account → Security → App passwords
3. .env dosyasına ekleyin:
   ```
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   ```
