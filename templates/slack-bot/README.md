# MiniMax-M2 Slack Bot Şablonu

MiniMax-M2 destekli Slack botu.

## Özellikler

- **Slash Komutları**: `/ask`, `/code`, `/translate`
- **Mention Yanıtları**: @bot ile sohbet
- **DM Desteği**: Direkt mesaj
- **Thread Desteği**: Thread içi sohbet geçmişi
- **Shortcuts**: Mesaj özetleme

## Kurulum

### 1. Slack App Oluşturma

1. https://api.slack.com/apps adresine gidin
2. "Create New App" → "From scratch"
3. App ismini ve workspace'i seçin

### 2. Bot Ayarları

**OAuth & Permissions:**
- Bot Token Scopes ekleyin:
  - `app_mentions:read`
  - `chat:write`
  - `commands`
  - `im:history`
  - `im:read`
  - `im:write`

**Event Subscriptions:**
- Enable Events
- Subscribe to bot events:
  - `app_mention`
  - `message.im`

**Slash Commands:**
- `/ask` - Soru sor
- `/code` - Kod analizi
- `/translate` - Çeviri
- `/clear` - Geçmiş temizle
- `/help` - Yardım

### 3. Socket Mode

- Settings → Socket Mode → Enable
- App-Level Token oluşturun (connections:write)

### 4. Kurulum

```bash
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını düzenleyin
python main.py
```

## Komutlar

| Komut | Açıklama |
|-------|----------|
| `/ask <soru>` | AI'ya soru sor |
| `/code <kod>` | Kod analizi |
| `/translate <metin>` | İngilizce'ye çevir |
| `/clear` | Sohbet geçmişini temizle |
| `/help` | Yardım göster |

## Kullanım

### Mention
```
@MiniMax Python'da liste nasıl oluşturulur?
```

### DM
Bot'a direkt mesaj gönderin.

### Thread
Thread'lerde sohbet geçmişi korunur.

## Shortcuts

Mesaj üzerinde sağ tık → "Summarize" shortcut'ı ile mesaj özetleyebilirsiniz.

## Manifest

```yaml
display_information:
  name: MiniMax-M2 Bot
features:
  bot_user:
    display_name: MiniMax
  slash_commands:
    - command: /ask
      description: AI'ya soru sor
    - command: /code
      description: Kod analizi
oauth_config:
  scopes:
    bot:
      - app_mentions:read
      - chat:write
      - commands
      - im:history
```
