"""
MiniMax-M2 Ses Asistanı Şablonu
===============================
Sesle etkileşimli AI asistanı.

Özellikler:
- Konuşma tanıma (Speech-to-Text)
- Metin sentezi (Text-to-Speech)
- Sürekli dinleme modu
- Wake word desteği
- Çoklu dil

Gereksinimler:
    pip install openai SpeechRecognition pyttsx3 pyaudio

Kullanım:
    python main.py
"""

import os
import sys
import time
import threading
from typing import Optional, Callable
from dataclasses import dataclass

from openai import OpenAI

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️ speech_recognition yüklü değil: pip install SpeechRecognition")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("⚠️ pyttsx3 yüklü değil: pip install pyttsx3")

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# Ses ayarları
WAKE_WORD = os.getenv("WAKE_WORD", "hey max")
LANGUAGE = os.getenv("LANGUAGE", "tr-TR")
VOICE_RATE = int(os.getenv("VOICE_RATE", "150"))

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)


# ============================================================================
# Veri Yapıları
# ============================================================================

@dataclass
class VoiceConfig:
    """Ses yapılandırması."""
    language: str = "tr-TR"
    voice_rate: int = 150
    wake_word: str = "hey max"
    timeout: float = 5.0
    phrase_time_limit: float = 10.0


# ============================================================================
# Speech-to-Text
# ============================================================================

class SpeechRecognizer:
    """Konuşma tanıyıcı."""

    def __init__(self, config: VoiceConfig = None):
        if not SPEECH_RECOGNITION_AVAILABLE:
            raise ImportError("speech_recognition gerekli")

        self.config = config or VoiceConfig()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Ortam gürültüsüne uyum
        with self.microphone as source:
            print("🎤 Mikrofon kalibre ediliyor...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def listen(self) -> Optional[str]:
        """Mikrofonu dinle ve metne çevir."""
        try:
            with self.microphone as source:
                print("🎤 Dinleniyor...")
                audio = self.recognizer.listen(
                    source,
                    timeout=self.config.timeout,
                    phrase_time_limit=self.config.phrase_time_limit
                )

            print("🔄 İşleniyor...")
            text = self.recognizer.recognize_google(
                audio,
                language=self.config.language
            )
            return text.lower()

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("❓ Anlaşılamadı")
            return None
        except sr.RequestError as e:
            print(f"❌ Tanıma hatası: {e}")
            return None

    def listen_for_wake_word(self) -> bool:
        """Wake word bekle."""
        text = self.listen()
        if text and self.config.wake_word in text:
            return True
        return False


# ============================================================================
# Text-to-Speech
# ============================================================================

class SpeechSynthesizer:
    """Konuşma sentezleyici."""

    def __init__(self, config: VoiceConfig = None):
        if not PYTTSX3_AVAILABLE:
            raise ImportError("pyttsx3 gerekli")

        self.config = config or VoiceConfig()
        self.engine = pyttsx3.init()

        # Ayarlar
        self.engine.setProperty("rate", self.config.voice_rate)

        # Türkçe ses varsa kullan
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if "turkish" in voice.name.lower() or "tr" in voice.id.lower():
                self.engine.setProperty("voice", voice.id)
                break

    def speak(self, text: str):
        """Metni seslendir."""
        print(f"🔊 {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def speak_async(self, text: str):
        """Asenkron seslendirme."""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.start()


# ============================================================================
# Voice Assistant
# ============================================================================

class VoiceAssistant:
    """Ses Asistanı."""

    def __init__(self, config: VoiceConfig = None):
        self.config = config or VoiceConfig()
        self.recognizer = SpeechRecognizer(self.config) if SPEECH_RECOGNITION_AVAILABLE else None
        self.synthesizer = SpeechSynthesizer(self.config) if PYTTSX3_AVAILABLE else None
        self.messages = []
        self.is_running = False

        self.system_prompt = """Sen sesli asistan MiniMax'sin.
Kısa ve anlaşılır yanıtlar ver.
Türkçe konuş.
Kullanıcıya yardımcı ol."""

    def process(self, text: str) -> str:
        """Kullanıcı girdisini işle."""
        # Özel komutlar
        if "kapat" in text or "dur" in text:
            return "STOP"

        if "temizle" in text:
            self.messages = []
            return "Sohbet geçmişi temizlendi."

        # AI yanıtı
        self.messages.append({"role": "user", "content": text})

        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.messages[-10:])  # Son 10 mesaj

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )

        ai_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": ai_response})

        return ai_response

    def respond(self, text: str):
        """Yanıt ver (ses ile)."""
        if self.synthesizer:
            self.synthesizer.speak(text)
        else:
            print(f"🤖 {text}")

    def run_continuous(self):
        """Sürekli dinleme modu."""
        if not self.recognizer or not self.synthesizer:
            print("❌ Ses bileşenleri yüklenemedi")
            return

        self.is_running = True
        print("\n" + "=" * 50)
        print("🎙️ Ses Asistanı Aktif")
        print(f"💡 Wake word: '{self.config.wake_word}'")
        print("   'kapat' diyerek çıkabilirsiniz")
        print("=" * 50 + "\n")

        self.respond("Merhaba! Size nasıl yardımcı olabilirim?")

        while self.is_running:
            text = self.recognizer.listen()

            if not text:
                continue

            print(f"👤 Sen: {text}")

            # Wake word kontrolü (opsiyonel)
            # if self.config.wake_word and self.config.wake_word not in text:
            #     continue

            response = self.process(text)

            if response == "STOP":
                self.respond("Görüşmek üzere!")
                self.is_running = False
                break

            self.respond(response)

    def run_once(self, text: str) -> str:
        """Tek seferlik işlem."""
        response = self.process(text)
        if self.synthesizer:
            self.synthesizer.speak(response)
        return response


# ============================================================================
# Text-Only Mode (Ses donanımı olmadan)
# ============================================================================

class TextVoiceAssistant:
    """Metin tabanlı ses asistanı simülasyonu."""

    def __init__(self):
        self.messages = []
        self.system_prompt = """Sen sesli asistan MiniMax'sin.
Kısa ve anlaşılır yanıtlar ver.
Türkçe konuş."""

    def chat(self, text: str) -> str:
        """Sohbet et."""
        self.messages.append({"role": "user", "content": text})

        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.messages[-10:])

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )

        ai_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": ai_response})

        return ai_response

    def run(self):
        """İnteraktif mod."""
        print("\n" + "=" * 50)
        print("🎙️ Ses Asistanı (Metin Modu)")
        print("   'çık' yazarak çıkabilirsiniz")
        print("=" * 50 + "\n")

        print("🤖 Merhaba! Size nasıl yardımcı olabilirim?\n")

        while True:
            try:
                user_input = input("👤 Sen: ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if user_input.lower() in ["çık", "kapat", "quit", "exit"]:
                print("🤖 Görüşmek üzere!")
                break

            if not user_input:
                continue

            response = self.chat(user_input)
            print(f"🤖 MiniMax: {response}\n")


# ============================================================================
# Ana Giriş
# ============================================================================

def main():
    """Ana fonksiyon."""
    print("=" * 60)
    print("🎙️ MiniMax-M2 Ses Asistanı")
    print("=" * 60)

    # Donanım kontrolü
    has_voice = SPEECH_RECOGNITION_AVAILABLE and PYTTSX3_AVAILABLE

    if has_voice:
        print("\n✅ Ses donanımı algılandı")
        print("1. Sesli mod")
        print("2. Metin modu")
        choice = input("\nSeçiminiz (1-2): ").strip()

        if choice == "1":
            try:
                config = VoiceConfig(
                    language=LANGUAGE,
                    voice_rate=VOICE_RATE,
                    wake_word=WAKE_WORD,
                )
                assistant = VoiceAssistant(config)
                assistant.run_continuous()
            except Exception as e:
                print(f"❌ Ses hatası: {e}")
                print("Metin moduna geçiliyor...")
                TextVoiceAssistant().run()
        else:
            TextVoiceAssistant().run()
    else:
        print("\n⚠️ Ses donanımı bulunamadı, metin modu kullanılıyor")
        print("Ses için yükleyin: pip install SpeechRecognition pyttsx3 pyaudio")
        TextVoiceAssistant().run()


if __name__ == "__main__":
    main()
