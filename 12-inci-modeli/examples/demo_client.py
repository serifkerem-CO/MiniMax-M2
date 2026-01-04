#!/usr/bin/env python3
"""
12. İnci Modeli - Demo Client
Interactive demo for testing the Emotion AI system
"""

import asyncio
import aiohttp
import json
from typing import List, Dict
import sys

# API Configuration
API_BASE = "http://localhost:8000"

class InciDemoClient:
    """Demo client for 12. İnci Modeli"""

    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def analyze_emotion(self, text: str, language: str = "tr") -> Dict:
        """Analyze emotion in text"""
        url = f"{self.base_url}/api/v1/emotion/analyze"
        payload = {"text": text, "language": language}

        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"API Error: {response.status}")

    async def get_emotions_list(self) -> List[Dict]:
        """Get list of 12 emotion categories"""
        url = f"{self.base_url}/api/v1/emotions/list"

        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("emotions", [])
            else:
                raise Exception(f"API Error: {response.status}")

    def print_result(self, text: str, result: Dict):
        """Pretty print analysis result"""
        print(f"\n{'='*60}")
        print(f"📝 Metin: {text}")
        print(f"{'='*60}")

        emotions = result.get("emotions", [])
        if emotions:
            print(f"\n🎯 Tespit Edilen Duygular:")
            for i, emotion in enumerate(emotions, 1):
                emoji = emotion.get("emoji", "")
                label = emotion.get("label", "")
                confidence = emotion.get("confidence", 0)
                print(f"  {i}. {emoji} {label} - {confidence*100:.0f}% güven")

        print(f"\n💎 Birincil Duygu: {result.get('primary_emotion', 'N/A')}")

        response = result.get("response_suggestion", "")
        if response:
            print(f"\n🤖 AI Yanıtı:")
            print(f"  {response}")

        print(f"\n{'='*60}\n")


async def demo_basic_analysis():
    """Demo: Basic emotion analysis"""
    print("\n🎯 DEMO 1: Temel Duygu Analizi\n")

    test_texts = [
        "Bugün harika bir gün geçirdim, çok mutluyum!",
        "Çok üzgünüm ve kaygılıyım, ne yapacağımı bilmiyorum",
        "Bu duruma çok sinirlendim, yeter artık!",
        "Vay canına, bunu hiç beklemiyordum! İnanılmaz!",
        "Seni çok seviyorum, her şey için teşekkürler",
    ]

    async with InciDemoClient() as client:
        for text in test_texts:
            try:
                result = await client.analyze_emotion(text)
                client.print_result(text, result)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"❌ Hata: {str(e)}")


async def demo_emotion_categories():
    """Demo: List all 12 emotion categories"""
    print("\n🎨 DEMO 2: 12 İnci Duygu Kategorileri\n")

    async with InciDemoClient() as client:
        try:
            emotions = await client.get_emotions_list()

            print(f"{'='*60}")
            print(f"💎 12 İnci Modeli - Duygu Kategorileri")
            print(f"{'='*60}\n")

            for emotion in emotions:
                id_num = emotion.get("id", "")
                emoji = emotion.get("emoji", "")
                label = emotion.get("label", "")
                type_name = emotion.get("type", "")

                print(f"  {id_num:2d}. {emoji}  {label:15s} ({type_name})")

            print(f"\n{'='*60}\n")

        except Exception as e:
            print(f"❌ Hata: {str(e)}")


async def demo_interactive():
    """Demo: Interactive mode"""
    print("\n💬 DEMO 3: İnteraktif Mod\n")
    print("Mesajınızı yazın (çıkmak için 'q'):\n")

    async with InciDemoClient() as client:
        while True:
            try:
                text = input("➤ Siz: ").strip()

                if text.lower() in ['q', 'quit', 'exit', 'çık']:
                    print("\n👋 Görüşürüz!")
                    break

                if not text:
                    continue

                result = await client.analyze_emotion(text)

                # Show emotions
                emotions = result.get("emotions", [])
                if emotions:
                    primary = emotions[0]
                    emoji = primary.get("emoji", "")
                    label = primary.get("label", "")
                    print(f"\n{emoji} {label}")

                # Show AI response
                response = result.get("response_suggestion", "")
                if response:
                    print(f"🤖 AI: {response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Görüşürüz!")
                break
            except Exception as e:
                print(f"\n❌ Hata: {str(e)}\n")


async def demo_all():
    """Run all demos"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           💎 12. İnci Modeli - Demo Client 💎             ║
║                                                           ║
║               modulLLM.com - Emotion AI                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    demos = [
        ("1", "Temel Duygu Analizi", demo_basic_analysis),
        ("2", "12 Duygu Kategorileri", demo_emotion_categories),
        ("3", "İnteraktif Mod", demo_interactive),
    ]

    while True:
        print("\n📋 Demo Seçenekleri:\n")
        for num, name, _ in demos:
            print(f"  {num}. {name}")
        print("  q. Çıkış\n")

        choice = input("Seçiminiz: ").strip()

        if choice.lower() in ['q', 'quit', 'exit']:
            print("\n👋 Görüşürüz!")
            break

        demo_func = next((func for num, _, func in demos if num == choice), None)

        if demo_func:
            await demo_func()
        else:
            print("\n❌ Geçersiz seçim!\n")


if __name__ == "__main__":
    try:
        asyncio.run(demo_all())
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandırıldı.")
        sys.exit(0)
