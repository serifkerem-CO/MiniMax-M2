"""
MiniMax-M2 Discord Bot Şablonu
==============================
MiniMax-M2 destekli bir Discord botu.

Özellikler:
- Sohbet komutları
- Kod analizi
- Kod üretimi
- Çoklu kanal desteği
- Kullanıcı bazlı sohbet geçmişi

Gereksinimler:
    pip install discord.py openai python-dotenv

Kullanım:
    1. Discord Developer Portal'dan bot oluşturun
    2. .env dosyasına DISCORD_TOKEN ekleyin
    3. python main.py

Discord Bot Oluşturma:
    https://discord.com/developers/applications
"""

import os
import asyncio
from typing import Optional
from datetime import datetime
from collections import defaultdict

import discord
from discord.ext import commands
from discord import app_commands
from openai import OpenAI

# Yapılandırma
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "your-discord-token")
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# Bot ayarları
MAX_HISTORY = 10  # Kullanıcı başına maksimum mesaj geçmişi
MAX_RESPONSE_LENGTH = 2000  # Discord mesaj limiti
THINKING_EMOJI = "🤔"


# ============================================================================
# Bot Sınıfı
# ============================================================================

class MiniMaxBot(commands.Bot):
    """MiniMax-M2 destekli Discord botu."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            description="MiniMax-M2 destekli AI asistan"
        )

        # OpenAI client
        self.ai_client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)

        # Kullanıcı sohbet geçmişleri
        self.conversations: dict[int, list[dict]] = defaultdict(list)

        # Sistem promptu
        self.system_prompt = """Sen MiniMax-M2 destekli yardımcı bir Discord botusun.
Kullanıcılara nazik ve yardımsever bir şekilde yanıt ver.
Kod yazarken markdown formatı kullan.
Türkçe konuş."""

    async def setup_hook(self):
        """Bot başlatma hook'u."""
        # Slash komutlarını senkronize et
        await self.tree.sync()
        print(f"✅ Slash komutları senkronize edildi")

    async def on_ready(self):
        """Bot hazır olduğunda çağrılır."""
        print(f"🤖 {self.user} olarak giriş yapıldı!")
        print(f"📊 {len(self.guilds)} sunucuda aktif")

        # Durum mesajı
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/sohbet ile bana sor!"
            )
        )

    async def get_ai_response(
        self,
        user_id: int,
        message: str,
        system_override: Optional[str] = None
    ) -> str:
        """AI yanıtı al."""
        # Mesaj geçmişini hazırla
        history = self.conversations[user_id][-MAX_HISTORY:]

        messages = [
            {"role": "system", "content": system_override or self.system_prompt}
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        try:
            response = self.ai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
            )

            ai_response = response.choices[0].message.content

            # Geçmişe ekle
            self.conversations[user_id].append({"role": "user", "content": message})
            self.conversations[user_id].append({"role": "assistant", "content": ai_response})

            # Geçmiş limitini kontrol et
            if len(self.conversations[user_id]) > MAX_HISTORY * 2:
                self.conversations[user_id] = self.conversations[user_id][-MAX_HISTORY * 2:]

            return ai_response

        except Exception as e:
            return f"❌ Hata oluştu: {str(e)}"

    def clear_history(self, user_id: int):
        """Kullanıcı geçmişini temizle."""
        self.conversations[user_id] = []


# Bot instance
bot = MiniMaxBot()


# ============================================================================
# Slash Komutları
# ============================================================================

@bot.tree.command(name="sohbet", description="MiniMax-M2 ile sohbet et")
@app_commands.describe(mesaj="Sormak istediğin soru veya mesaj")
async def sohbet(interaction: discord.Interaction, mesaj: str):
    """Sohbet komutu."""
    await interaction.response.defer(thinking=True)

    response = await bot.get_ai_response(interaction.user.id, mesaj)

    # Uzun yanıtları böl
    if len(response) > MAX_RESPONSE_LENGTH:
        chunks = [response[i:i+MAX_RESPONSE_LENGTH] for i in range(0, len(response), MAX_RESPONSE_LENGTH)]
        await interaction.followup.send(chunks[0])
        for chunk in chunks[1:]:
            await interaction.channel.send(chunk)
    else:
        await interaction.followup.send(response)


@bot.tree.command(name="kod", description="Kod üret veya analiz et")
@app_commands.describe(
    islem="İşlem türü",
    aciklama="Kod açıklaması veya analiz edilecek kod"
)
@app_commands.choices(islem=[
    app_commands.Choice(name="Üret", value="generate"),
    app_commands.Choice(name="Analiz", value="analyze"),
    app_commands.Choice(name="Düzelt", value="fix"),
])
async def kod(interaction: discord.Interaction, islem: str, aciklama: str):
    """Kod işlemleri komutu."""
    await interaction.response.defer(thinking=True)

    if islem == "generate":
        system = """Sen uzman bir yazılım geliştiricisisin.
Verilen açıklamaya göre temiz, okunabilir kod yaz.
Kodu markdown code block içinde döndür."""
        prompt = f"Şu kodu yaz: {aciklama}"

    elif islem == "analyze":
        system = """Sen uzman bir kod analistisin.
Verilen kodu analiz et ve şunları belirt:
1. Kodun ne yaptığı
2. Olası sorunlar
3. İyileştirme önerileri"""
        prompt = f"Bu kodu analiz et:\n```\n{aciklama}\n```"

    else:  # fix
        system = """Sen uzman bir hata ayıklayıcısın.
Verilen koddaki hataları bul ve düzelt.
Düzeltilmiş kodu ve açıklamayı döndür."""
        prompt = f"Bu kodu düzelt:\n```\n{aciklama}\n```"

    response = await bot.get_ai_response(
        interaction.user.id,
        prompt,
        system_override=system
    )

    if len(response) > MAX_RESPONSE_LENGTH:
        chunks = [response[i:i+MAX_RESPONSE_LENGTH] for i in range(0, len(response), MAX_RESPONSE_LENGTH)]
        await interaction.followup.send(chunks[0])
        for chunk in chunks[1:]:
            await interaction.channel.send(chunk)
    else:
        await interaction.followup.send(response)


@bot.tree.command(name="temizle", description="Sohbet geçmişini temizle")
async def temizle(interaction: discord.Interaction):
    """Geçmiş temizleme komutu."""
    bot.clear_history(interaction.user.id)
    await interaction.response.send_message(
        "🧹 Sohbet geçmişin temizlendi!",
        ephemeral=True
    )


@bot.tree.command(name="yardim", description="Bot komutları hakkında bilgi")
async def yardim(interaction: discord.Interaction):
    """Yardım komutu."""
    embed = discord.Embed(
        title="🤖 MiniMax-M2 Bot Yardım",
        description="MiniMax-M2 destekli AI asistan",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="/sohbet <mesaj>",
        value="AI ile sohbet et",
        inline=False
    )
    embed.add_field(
        name="/kod <işlem> <açıklama>",
        value="Kod üret, analiz et veya düzelt",
        inline=False
    )
    embed.add_field(
        name="/temizle",
        value="Sohbet geçmişini temizle",
        inline=False
    )
    embed.add_field(
        name="/yardim",
        value="Bu yardım mesajını göster",
        inline=False
    )

    embed.set_footer(text="MiniMax-M2 ile güçlendirilmiştir")
    embed.timestamp = datetime.now()

    await interaction.response.send_message(embed=embed)


# ============================================================================
# Prefix Komutları (Opsiyonel)
# ============================================================================

@bot.command(name="sor")
async def sor(ctx: commands.Context, *, soru: str):
    """Prefix ile soru sor (!sor <soru>)."""
    async with ctx.typing():
        response = await bot.get_ai_response(ctx.author.id, soru)

    if len(response) > MAX_RESPONSE_LENGTH:
        chunks = [response[i:i+MAX_RESPONSE_LENGTH] for i in range(0, len(response), MAX_RESPONSE_LENGTH)]
        for chunk in chunks:
            await ctx.send(chunk)
    else:
        await ctx.send(response)


@bot.command(name="ping")
async def ping(ctx: commands.Context):
    """Bot gecikmesini göster."""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Gecikme: {latency}ms")


# ============================================================================
# Event Handlers
# ============================================================================

@bot.event
async def on_message(message: discord.Message):
    """Mesaj event handler."""
    # Kendi mesajlarını yoksay
    if message.author == bot.user:
        return

    # Bot mention edilirse yanıt ver
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        # Mention'ı temizle
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()

        if content:
            async with message.channel.typing():
                response = await bot.get_ai_response(message.author.id, content)

            if len(response) > MAX_RESPONSE_LENGTH:
                chunks = [response[i:i+MAX_RESPONSE_LENGTH] for i in range(0, len(response), MAX_RESPONSE_LENGTH)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.reply(response)
        else:
            await message.reply("Merhaba! Bana bir şey sormak ister misin? 🤖")

    # Prefix komutlarını işle
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Komut hata handler."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Eksik argüman: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Bilinmeyen komutları yoksay
    else:
        await ctx.send(f"❌ Hata: {str(error)}")


# ============================================================================
# Ana Giriş
# ============================================================================

def main():
    """Botu başlat."""
    if DISCORD_TOKEN == "your-discord-token":
        print("❌ Hata: DISCORD_TOKEN ayarlanmamış!")
        print("Lütfen .env dosyasına DISCORD_TOKEN ekleyin.")
        return

    print("🚀 Bot başlatılıyor...")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
