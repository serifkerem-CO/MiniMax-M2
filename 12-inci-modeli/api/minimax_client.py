"""
MiniMax-M2 API Client for Emotion-Aware Response Generation
modulLLM.com integration
"""

import os
import httpx
import asyncio
from typing import List, Optional, Dict
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class MiniMaxClient:
    """
    Client for MiniMax-M2 API
    Generates emotion-aware responses using MiniMax-M2 model
    """

    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY", "")
        self.api_base = os.getenv(
            "MINIMAX_API_BASE",
            "https://api.minimax.chat/v1/text/chatcompletion_v2"
        )
        self.group_id = os.getenv("MINIMAX_GROUP_ID", "")
        self.model = "MiniMax-Text-01"

        # Model parameters (as recommended in README)
        self.temperature = float(os.getenv("TEMPERATURE", "1.0"))
        self.top_p = float(os.getenv("TOP_P", "0.95"))
        self.top_k = int(os.getenv("TOP_K", "40"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1024"))

        self.client = httpx.AsyncClient(timeout=60.0)

        if not self.api_key:
            logger.warning("MINIMAX_API_KEY not set! Set it in .env file")

        logger.info(f"MiniMaxClient initialized - Model: {self.model}")

    def is_ready(self) -> bool:
        """Check if client is configured"""
        return bool(self.api_key)

    async def generate_emotion_response(
        self,
        text: str,
        emotions: List,
        context: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """
        Generate emotion-aware response using MiniMax-M2

        Args:
            text: User's input text
            emotions: List of detected emotions
            context: Optional conversation context
            stream: Enable streaming (not implemented yet)

        Returns:
            AI-generated emotion-aware response
        """
        try:
            # Build emotion context
            emotion_context = self._build_emotion_context(emotions)

            # Create system prompt
            system_prompt = self._create_emotion_system_prompt(emotion_context)

            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]

            if context:
                messages.append({
                    "role": "system",
                    "content": f"Önceki konuşma bağlamı: {context}"
                })

            messages.append({
                "role": "user",
                "content": text
            })

            # Make API call
            response = await self._call_minimax_api(messages)

            return response

        except Exception as e:
            logger.error(f"MiniMax API error: {str(e)}")
            # Fallback response
            return self._generate_fallback_response(emotions)

    def _build_emotion_context(self, emotions: List) -> str:
        """Build emotion context string for prompt"""
        if not emotions:
            return "nötr"

        primary = emotions[0]
        emotion_str = f"{primary.label} ({primary.emoji})"

        if len(emotions) > 1:
            secondary = emotions[1]
            emotion_str += f" ve {secondary.label} ({secondary.emoji})"

        return emotion_str

    def _create_emotion_system_prompt(self, emotion_context: str) -> str:
        """
        Create emotion-aware system prompt for MiniMax-M2
        """
        return f"""Sen 12. İnci (Pearl) Modeli adlı duygusal zeka asistanısın. modulLLM.com platformu üzerinde çalışıyorsun.

**Görevin:**
Kullanıcının duygusal durumunu anlamak ve empatik, uygun yanıtlar vermek.

**Tespit Edilen Duygular:** {emotion_context}

**Yanıt Kuralları:**
1. Kullanıcının duygusal durumuna uygun ton kullan
2. Empati göster ve duygularını doğrula
3. Yapıcı ve destekleyici ol
4. Doğal ve samimi bir dil kullan
5. Emoji kullanımı sınırlı tut (sadece uygun yerlerde)
6. Türkçe yanıt ver

**12 İnci Duygu Kategorileri:**
😊 Mutluluk | 😢 Üzüntü | 😠 Öfke | 😨 Korku | 🤢 Tiksinme | 😲 Şaşkınlık
❤️ Sevgi | 🤔 Merak | 😌 Huzur | 💪 Güven | 😔 Pişmanlık | 🎉 Heyecan

Kullanıcının duygularına uygun, yardımcı ve anlayışlı bir yanıt ver."""

    async def _call_minimax_api(self, messages: List[Dict]) -> str:
        """
        Make actual API call to MiniMax
        """
        if not self.api_key:
            logger.warning("No API key, using fallback")
            return "MiniMax API anahtarı ayarlanmamış. Lütfen .env dosyasına MINIMAX_API_KEY ekleyin."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "stream": False,
            # MiniMax-M2 specific parameters
            "mask_sensitive_info": True,
            "reply_constraints": {
                "sender_type": "BOT",
                "sender_name": "12. İnci Modeli"
            }
        }

        # Add group_id if available
        if self.group_id:
            headers["GroupId"] = self.group_id

        try:
            response = await self.client.post(
                self.api_base,
                json=payload,
                headers=headers
            )

            if response.status_code != 200:
                logger.error(f"MiniMax API error: {response.status_code} - {response.text}")
                raise Exception(f"API error: {response.status_code}")

            data = response.json()

            # Extract response from MiniMax API response format
            if "choices" in data and len(data["choices"]) > 0:
                message = data["choices"][0].get("message", {})
                content = message.get("content", "")

                # Remove <think>...</think> tags if present (MiniMax-M2 thinking)
                import re
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                content = content.strip()

                return content
            elif "reply" in data:
                # Alternative response format
                return data["reply"]
            else:
                logger.error(f"Unexpected API response format: {data}")
                raise Exception("Unexpected response format")

        except httpx.TimeoutException:
            logger.error("MiniMax API timeout")
            raise Exception("API isteği zaman aşımına uğradı")
        except Exception as e:
            logger.error(f"MiniMax API call failed: {str(e)}")
            raise

    def _generate_fallback_response(self, emotions: List) -> str:
        """
        Generate fallback response when API is unavailable
        """
        if not emotions:
            return "Mesajınızı aldım. Size nasıl yardımcı olabilirim?"

        primary = emotions[0]

        fallback_responses = {
            "joy": "Mutluluğunuzu paylaştığınız için teşekkürler! Bu pozitif enerjinizi hissetmek güzel.",
            "sadness": "Üzgün hissettiğinizi anlıyorum. Yanınızdayım, konuşmak isterseniz buradayım.",
            "anger": "Sinirlenmiş görünüyorsunuz. Neler olduğunu paylaşmak isterseniz dinliyorum.",
            "fear": "Endişelerinizi anlıyorum. Adım adım ilerleyebiliriz, yalnız değilsiniz.",
            "disgust": "Rahatsızlığınızı anlıyorum. Durumu daha iyi hale getirmek için ne yapabiliriz?",
            "surprise": "Şaşkınlık yaratan bir durum var gibi. Daha fazla bilgi verir misiniz?",
            "love": "Sevginizi ve pozitif duygularınızı hissetmek çok güzel.",
            "curiosity": "Merakınız çok güzel! Size yardımcı olmaya çalışayım.",
            "peace": "Huzurlu bir enerji yayıyorsunuz. Bu güzel.",
            "confidence": "Güveninizi hissediyorum! Bu harika bir tutum.",
            "regret": "Pişmanlık duymak insani bir duygu. Geçmişten ders alıp ileriye bakmak önemli.",
            "excitement": "Heyecanınız bulaşıcı! Bu enerji harika."
        }

        response = fallback_responses.get(
            primary.type,
            "Mesajınızı aldım ve duygularınızı anlıyorum."
        )

        return f"{response} (Not: MiniMax API bağlantısı kurulamadı, varsayılan yanıt)"

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    def __del__(self):
        """Cleanup on deletion"""
        try:
            asyncio.create_task(self.close())
        except:
            pass
