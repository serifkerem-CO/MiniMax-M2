#!/usr/bin/env python3
"""
12. İnci Modeli - WebSocket Demo
Real-time emotion chat demo using WebSocket
"""

import asyncio
import websockets
import json
import sys

WS_URL = "ws://localhost:8000/ws/emotion/realtime"

async def emotion_chat():
    """Interactive WebSocket emotion chat"""

    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║      💎 12. İnci Modeli - Real-time WebSocket Chat 💎     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    try:
        async with websockets.connect(WS_URL) as websocket:
            # Receive welcome message
            welcome = await websocket.recv()
            data = json.loads(welcome)

            if data.get("type") == "connected":
                print(f"✅ {data.get('message', 'Bağlı!')}\n")

            print("Mesajınızı yazın (çıkmak için 'q'):\n")

            # Create task for receiving messages
            async def receive_messages():
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)

                        if data.get("type") == "emotion_response":
                            print_emotion_response(data)
                        elif data.get("type") == "error":
                            print(f"\n❌ Hata: {data.get('message')}\n")

                    except Exception as e:
                        print(f"\n❌ Mesaj alma hatası: {str(e)}")
                        break

            # Start receiving task
            receive_task = asyncio.create_task(receive_messages())

            # Send messages
            while True:
                try:
                    text = await asyncio.get_event_loop().run_in_executor(
                        None, input, "➤ Siz: "
                    )
                    text = text.strip()

                    if text.lower() in ['q', 'quit', 'exit', 'çık']:
                        print("\n👋 Görüşürüz!")
                        receive_task.cancel()
                        break

                    if not text:
                        continue

                    # Send message
                    message = {
                        "type": "message",
                        "text": text
                    }

                    await websocket.send(json.dumps(message))

                except Exception as e:
                    print(f"\n❌ Mesaj gönderme hatası: {str(e)}")
                    break

    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket bağlantı hatası: {str(e)}")
        print("API sunucusunun çalıştığından emin olun!")
    except Exception as e:
        print(f"❌ Hata: {str(e)}")


def print_emotion_response(data: dict):
    """Pretty print emotion response"""
    emotions = data.get("emotions", [])
    ai_response = data.get("ai_response", "")

    # Print detected emotions
    if emotions:
        emotion_str = " ".join([
            f"{e.get('emoji', '')} {e.get('label', '')}"
            for e in emotions[:2]  # Show top 2
        ])
        print(f"\n[{emotion_str}]")

    # Print AI response
    if ai_response:
        print(f"🤖 AI: {ai_response}\n")


if __name__ == "__main__":
    try:
        asyncio.run(emotion_chat())
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandırıldı.")
        sys.exit(0)
