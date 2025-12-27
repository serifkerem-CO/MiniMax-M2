"""
MiniMax-M2 Telegram Bot Şablonu
===============================
MiniMax-M2 destekli bir Telegram botu.

Özellikler:
- Sohbet komutları
- Inline modu
- Kod analizi
- Sesli mesaj desteği (opsiyonel)

Gereksinimler:
    pip install python-telegram-bot openai

Kullanım:
    1. @BotFather ile bot oluşturun
    2. .env dosyasına TELEGRAM_TOKEN ekleyin
    3. python main.py
"""

import os
import logging
from typing import Optional
from collections import defaultdict

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Yapılandırma
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your-telegram-token")
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# Bot ayarları
MAX_HISTORY = 10
MAX_MESSAGE_LENGTH = 4096

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)

# Kullanıcı sohbet geçmişleri
conversations: dict[int, list[dict]] = defaultdict(list)


# ============================================================================
# Yardımcı Fonksiyonlar
# ============================================================================

async def get_ai_response(user_id: int, message: str, system_prompt: Optional[str] = None) -> str:
    """AI yanıtı al."""
    history = conversations[user_id][-MAX_HISTORY:]

    messages = [
        {"role": "system", "content": system_prompt or "Sen yardımcı bir Telegram botusun."}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
        )

        ai_response = response.choices[0].message.content

        # Geçmişe ekle
        conversations[user_id].append({"role": "user", "content": message})
        conversations[user_id].append({"role": "assistant", "content": ai_response})

        # Limit kontrolü
        if len(conversations[user_id]) > MAX_HISTORY * 2:
            conversations[user_id] = conversations[user_id][-MAX_HISTORY * 2:]

        return ai_response

    except Exception as e:
        logger.error(f"AI hatası: {e}")
        return f"❌ Hata oluştu: {str(e)}"


def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """Uzun mesajları böl."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break

        # Kelime sınırında kes
        split_pos = text.rfind(' ', 0, max_length)
        if split_pos == -1:
            split_pos = max_length

        chunks.append(text[:split_pos])
        text = text[split_pos:].lstrip()

    return chunks


# ============================================================================
# Komut İşleyicileri
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlangıç komutu."""
    welcome_message = """
🤖 *MiniMax-M2 Bot'a Hoş Geldiniz!*

Ben MiniMax-M2 ile güçlendirilmiş bir AI asistanıyım.

*Komutlar:*
/start - Bu mesajı göster
/help - Yardım
/clear - Sohbet geçmişini temizle
/code - Kod analizi
/translate - Çeviri

Veya doğrudan mesaj yazarak sohbet edebilirsiniz!
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yardım komutu."""
    help_text = """
📚 *Yardım*

*Sohbet:*
Doğrudan mesaj yazarak AI ile sohbet edebilirsiniz.

*Komutlar:*
• `/code <kod>` - Kodu analiz et
• `/translate <metin>` - İngilizce'ye çevir
• `/clear` - Sohbet geçmişini temizle

*İpuçları:*
• Bot geçmiş mesajları hatırlar
• Uzun yanıtlar otomatik bölünür
• Inline modda @botadı yazarak kullanabilirsiniz
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Geçmiş temizleme komutu."""
    user_id = update.effective_user.id
    conversations[user_id] = []
    await update.message.reply_text("🧹 Sohbet geçmişi temizlendi!")


async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kod analizi komutu."""
    if not context.args:
        await update.message.reply_text(
            "Kullanım: `/code <kod>`\nÖrnek: `/code print('hello')`",
            parse_mode="Markdown"
        )
        return

    code = " ".join(context.args)

    await update.message.reply_text("🔍 Kod analiz ediliyor...")

    response = await get_ai_response(
        update.effective_user.id,
        f"Bu kodu analiz et ve açıkla:\n```\n{code}\n```",
        system_prompt="Sen uzman bir kod analistisin. Kodu açıkla ve varsa sorunları belirt."
    )

    for chunk in split_message(response):
        await update.message.reply_text(chunk)


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Çeviri komutu."""
    if not context.args:
        await update.message.reply_text(
            "Kullanım: `/translate <metin>`",
            parse_mode="Markdown"
        )
        return

    text = " ".join(context.args)

    response = await get_ai_response(
        update.effective_user.id,
        f"Bu metni İngilizce'ye çevir:\n{text}",
        system_prompt="Sen profesyonel bir çevirmensin. Sadece çeviriyi döndür."
    )

    await update.message.reply_text(f"🌍 *Çeviri:*\n{response}", parse_mode="Markdown")


# ============================================================================
# Mesaj İşleyicileri
# ============================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Normal mesaj işleyici."""
    user_id = update.effective_user.id
    message_text = update.message.text

    # Yazıyor göstergesi
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    response = await get_ai_response(user_id, message_text)

    for chunk in split_message(response):
        await update.message.reply_text(chunk)


async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline sorgu işleyici."""
    query = update.inline_query.query

    if not query:
        return

    try:
        response = await get_ai_response(
            update.inline_query.from_user.id,
            query,
            system_prompt="Kısa ve öz cevap ver."
        )

        # Yanıtı kısalt
        if len(response) > 200:
            short_response = response[:200] + "..."
        else:
            short_response = response

        results = [
            InlineQueryResultArticle(
                id="1",
                title="MiniMax-M2 Yanıtı",
                description=short_response,
                input_message_content=InputTextMessageContent(response),
            )
        ]

        await update.inline_query.answer(results, cache_time=10)

    except Exception as e:
        logger.error(f"Inline sorgu hatası: {e}")


# ============================================================================
# Hata İşleyici
# ============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hata işleyici."""
    logger.error(f"Hata: {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Bir hata oluştu. Lütfen tekrar deneyin."
        )


# ============================================================================
# Ana Giriş
# ============================================================================

def main():
    """Botu başlat."""
    if TELEGRAM_TOKEN == "your-telegram-token":
        print("❌ Hata: TELEGRAM_TOKEN ayarlanmamış!")
        print("Lütfen .env dosyasına TELEGRAM_TOKEN ekleyin.")
        return

    print("🚀 Telegram botu başlatılıyor...")

    # Uygulama oluştur
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Komut işleyicileri
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("code", code_command))
    application.add_handler(CommandHandler("translate", translate_command))

    # Mesaj işleyicileri
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Inline işleyici
    application.add_handler(InlineQueryHandler(handle_inline_query))

    # Hata işleyici
    application.add_error_handler(error_handler)

    # Başlat
    print("✅ Bot hazır!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
