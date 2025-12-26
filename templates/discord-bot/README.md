# MiniMax-M2 Discord Bot Şablonu

MiniMax-M2 destekli bir Discord botu.

## Özellikler

- **Sohbet**: AI ile doğal dil sohbeti
- **Kod İşlemleri**: Kod üretimi, analizi ve düzeltmesi
- **Hafıza**: Kullanıcı bazlı sohbet geçmişi
- **Slash Komutları**: Modern Discord komut arayüzü
- **Mention Yanıtı**: Bot mention edildiğinde yanıt verir

## Kurulum

### 1. Discord Bot Oluşturma

1. [Discord Developer Portal](https://discord.com/developers/applications)'a gidin
2. "New Application" tıklayın ve isim verin
3. "Bot" sekmesine gidin
4. "Add Bot" tıklayın
5. "Reset Token" ile token alın
6. "MESSAGE CONTENT INTENT" seçeneğini aktifleştirin

### 2. Bot'u Sunucuya Ekleme

1. "OAuth2" > "URL Generator" sekmesine gidin
2. Scopes: `bot`, `applications.commands`
3. Bot Permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`
4. Oluşturulan URL ile botu sunucuya ekleyin

### 3. Kurulum

```bash
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını düzenleyin
python main.py
```

## Komutlar

### Slash Komutları

| Komut | Açıklama |
|-------|----------|
| `/sohbet <mesaj>` | AI ile sohbet et |
| `/kod <işlem> <açıklama>` | Kod üret/analiz et/düzelt |
| `/temizle` | Sohbet geçmişini temizle |
| `/yardim` | Yardım mesajını göster |

### Prefix Komutları

| Komut | Açıklama |
|-------|----------|
| `!sor <soru>` | AI'ya soru sor |
| `!ping` | Bot gecikmesini göster |

### Mention

Botu mention ederek (@BotAdı) doğrudan sohbet edebilirsiniz.

## Kullanım Örnekleri

```
/sohbet Python'da liste nasıl oluşturulur?

/kod Üret Fibonacci dizisini hesaplayan fonksiyon

/kod Analiz def hello(): print("world")

@BotAdı Merhaba, nasılsın?
```

## Yapılandırma

### Ortam Değişkenleri

| Değişken | Açıklama |
|----------|----------|
| `DISCORD_TOKEN` | Discord bot token |
| `MINIMAX_API_BASE` | MiniMax API endpoint |
| `MINIMAX_API_KEY` | MiniMax API anahtarı |
| `MINIMAX_MODEL` | Model adı |

### Bot Ayarları (main.py)

```python
MAX_HISTORY = 10        # Kullanıcı başına mesaj geçmişi
MAX_RESPONSE_LENGTH = 2000  # Maksimum mesaj uzunluğu
```

## Docker ile Çalıştırma

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

```bash
docker build -t minimax-discord .
docker run -d --env-file .env minimax-discord
```

## Güvenlik Notları

1. Token'ı asla paylaşmayın
2. `.env` dosyasını `.gitignore`'a ekleyin
3. Production'da rate limiting ekleyin
4. Hassas komutları yetkilendirme ile koruyun
