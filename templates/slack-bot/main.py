"""
MiniMax-M2 Slack Bot Şablonu
============================
MiniMax-M2 destekli Slack botu.

Özellikler:
- Slash komutları
- Mention yanıtları
- Thread desteği
- Kanal bazlı sohbet

Gereksinimler:
    pip install slack-bolt openai

Kullanım:
    1. Slack App oluşturun: https://api.slack.com/apps
    2. Bot Token ve Signing Secret alın
    3. .env dosyasını düzenleyin
    4. python main.py
"""

import os
import re
from collections import defaultdict

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI

# Yapılandırma
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "xoxb-your-token")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "xapp-your-token")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "your-signing-secret")

API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# Bot ayarları
MAX_HISTORY = 10

# Slack uygulaması
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)

# Sohbet geçmişleri (thread_ts bazlı)
conversations: dict[str, list[dict]] = defaultdict(list)


# ============================================================================
# Yardımcı Fonksiyonlar
# ============================================================================

def get_thread_key(channel: str, thread_ts: str = None) -> str:
    """Thread anahtarı oluştur."""
    return f"{channel}:{thread_ts or 'main'}"


def get_ai_response(thread_key: str, message: str, system_prompt: str = None) -> str:
    """AI yanıtı al."""
    history = conversations[thread_key][-MAX_HISTORY:]

    messages = [
        {"role": "system", "content": system_prompt or "Sen yardımcı bir Slack botusun. Kısa ve öz yanıtlar ver."}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )

        ai_response = response.choices[0].message.content

        # Geçmişe ekle
        conversations[thread_key].append({"role": "user", "content": message})
        conversations[thread_key].append({"role": "assistant", "content": ai_response})

        # Limit kontrolü
        if len(conversations[thread_key]) > MAX_HISTORY * 2:
            conversations[thread_key] = conversations[thread_key][-MAX_HISTORY * 2:]

        return ai_response

    except Exception as e:
        return f"❌ Hata: {str(e)}"


def clean_mention(text: str) -> str:
    """Mention'ları temizle."""
    return re.sub(r"<@[A-Z0-9]+>", "", text).strip()


# ============================================================================
# Event Handlers
# ============================================================================

@app.event("app_mention")
def handle_mention(event, say):
    """Bot mention edildiğinde."""
    channel = event["channel"]
    thread_ts = event.get("thread_ts", event["ts"])
    user = event["user"]
    text = clean_mention(event["text"])

    if not text:
        say(
            text="Merhaba! Bana bir şey sormak ister misin? 🤖",
            thread_ts=thread_ts
        )
        return

    thread_key = get_thread_key(channel, thread_ts)
    response = get_ai_response(thread_key, text)

    say(text=response, thread_ts=thread_ts)


@app.event("message")
def handle_message(event, say):
    """DM mesajları."""
    # Sadece DM'leri işle
    if event.get("channel_type") != "im":
        return

    # Bot mesajlarını yoksay
    if event.get("bot_id"):
        return

    channel = event["channel"]
    text = event.get("text", "")

    if not text:
        return

    thread_key = get_thread_key(channel)
    response = get_ai_response(thread_key, text)

    say(text=response)


# ============================================================================
# Slash Komutları
# ============================================================================

@app.command("/ask")
def handle_ask(ack, command, say):
    """Soru sorma komutu."""
    ack()

    text = command["text"]
    channel = command["channel_id"]
    user = command["user_id"]

    if not text:
        say(text="Kullanım: `/ask <soru>`", response_type="ephemeral")
        return

    thread_key = get_thread_key(channel)
    response = get_ai_response(thread_key, text)

    say(
        text=f"*Soru:* {text}\n\n*Yanıt:*\n{response}",
        response_type="in_channel"
    )


@app.command("/code")
def handle_code(ack, command, say):
    """Kod analizi komutu."""
    ack()

    code = command["text"]

    if not code:
        say(text="Kullanım: `/code <kod>`", response_type="ephemeral")
        return

    response = get_ai_response(
        "code_analysis",
        f"Bu kodu analiz et:\n```\n{code}\n```",
        system_prompt="Sen uzman bir kod analistisin. Kodu açıkla ve varsa sorunları belirt."
    )

    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*🔍 Kod Analizi*"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"```{code}```"}
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response}
            }
        ],
        response_type="in_channel"
    )


@app.command("/translate")
def handle_translate(ack, command, say):
    """Çeviri komutu."""
    ack()

    text = command["text"]

    if not text:
        say(text="Kullanım: `/translate <metin>`", response_type="ephemeral")
        return

    response = get_ai_response(
        "translation",
        f"Bu metni İngilizce'ye çevir: {text}",
        system_prompt="Sen profesyonel bir çevirmensin. Sadece çeviriyi döndür."
    )

    say(
        text=f"🌍 *Çeviri:*\n> {text}\n\n*English:*\n> {response}",
        response_type="in_channel"
    )


@app.command("/clear")
def handle_clear(ack, command, say):
    """Geçmiş temizleme komutu."""
    ack()

    channel = command["channel_id"]
    thread_key = get_thread_key(channel)
    conversations[thread_key] = []

    say(text="🧹 Sohbet geçmişi temizlendi!", response_type="ephemeral")


@app.command("/help")
def handle_help(ack, say):
    """Yardım komutu."""
    ack()

    say(
        blocks=[
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🤖 MiniMax-M2 Bot Yardım"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Komutlar:*\n"
                            "• `/ask <soru>` - Soru sor\n"
                            "• `/code <kod>` - Kod analizi\n"
                            "• `/translate <metin>` - Çeviri\n"
                            "• `/clear` - Geçmişi temizle\n"
                            "• `/help` - Bu yardım mesajı\n\n"
                            "*Mention:*\n"
                            "Botu mention ederek (@bot) sohbet edebilirsiniz.\n\n"
                            "*DM:*\n"
                            "Bota direkt mesaj atarak sohbet edebilirsiniz."
                }
            }
        ],
        response_type="ephemeral"
    )


# ============================================================================
# Shortcuts ve Actions
# ============================================================================

@app.shortcut("summarize_message")
def handle_summarize(ack, shortcut, client):
    """Mesaj özetleme shortcut'ı."""
    ack()

    # Mesajı al
    channel = shortcut["channel"]["id"]
    message_ts = shortcut["message"]["ts"]
    text = shortcut["message"].get("text", "")

    if not text:
        return

    # Özetle
    response = get_ai_response(
        "summarize",
        f"Bu mesajı özetle: {text}",
        system_prompt="Sen metin özetleme uzmanısın. Kısa ve öz özetle."
    )

    # Yanıt gönder
    client.chat_postMessage(
        channel=channel,
        thread_ts=message_ts,
        text=f"📝 *Özet:*\n{response}"
    )


# ============================================================================
# Ana Giriş
# ============================================================================

def main():
    """Botu başlat."""
    if SLACK_BOT_TOKEN == "xoxb-your-token":
        print("❌ Hata: SLACK_BOT_TOKEN ayarlanmamış!")
        print("Lütfen .env dosyasını düzenleyin.")
        return

    print("🚀 Slack botu başlatılıyor...")
    print("   Bot Token: ****" + SLACK_BOT_TOKEN[-4:])

    # Socket Mode ile başlat
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    print("✅ Bot hazır!")
    handler.start()


if __name__ == "__main__":
    main()
