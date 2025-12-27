# MiniMax-M2 Telegram Bot Şablonu

MiniMax-M2 destekli bir Telegram botu.

## Özellikler

- **Sohbet**: Doğal dil sohbeti
- **Kod Analizi**: `/code` komutu
- **Çeviri**: `/translate` komutu
- **Inline Modu**: Herhangi bir sohbette @botadı ile kullanım
- **Sohbet Geçmişi**: Kullanıcı bazlı hafıza

## Kurulum

### 1. Telegram Bot Oluşturma

1. Telegram'da [@BotFather](https://t.me/botfather)'a gidin
2. `/newbot` komutu ile yeni bot oluşturun
3. Bot adı ve kullanıcı adı belirleyin
4. Token'ı alın

### 2. Kurulum

```bash
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını düzenleyin
python main.py
```

## Komutlar

| Komut | Açıklama |
|-------|----------|
| `/start` | Hoş geldin mesajı |
| `/help` | Yardım |
| `/clear` | Sohbet geçmişini temizle |
| `/code <kod>` | Kod analizi |
| `/translate <metin>` | İngilizce'ye çevir |

## Inline Modu

Herhangi bir sohbette:
```
@botadı Python nedir?
```

## Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## Özelleştirme

### Sistem Promptu Değiştirme

```python
async def get_ai_response(user_id, message, system_prompt=None):
    # Varsayılan sistem promptu
    default_prompt = "Sen yardımcı bir asistansın..."
```

### Yeni Komut Ekleme

```python
async def my_command(update, context):
    await update.message.reply_text("Yeni komut!")

application.add_handler(CommandHandler("mycommand", my_command))
```

## Güvenlik

1. Token'ı asla paylaşmayın
2. `.env` dosyasını `.gitignore`'a ekleyin
3. Rate limiting düşünün
