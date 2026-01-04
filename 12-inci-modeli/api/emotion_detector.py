"""
Emotion Detection Engine for 12. İnci Modeli
Uses hybrid approach: rule-based + ML model
"""

import re
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class Emotion(BaseModel):
    type: str
    confidence: float
    label: str
    emoji: str

class EmotionDetector:
    """
    12 İnci (Pearl) Emotion Detector
    Detects 12 core emotional categories in Turkish text
    """

    def __init__(self):
        self.emotion_keywords = self._load_emotion_keywords()
        self.ready = True
        logger.info("EmotionDetector initialized with 12 emotion categories")

    def _load_emotion_keywords(self) -> Dict[str, Dict]:
        """
        12 İnci Duygu Kategorileri ve keyword'leri
        """
        return {
            "joy": {
                "label": "Mutluluk",
                "emoji": "😊",
                "keywords": [
                    "mutlu", "sevinç", "harika", "mükemmel", "güzel", "süper",
                    "sevindim", "bayıldım", "iyi", "hoş", "keyifli", "neşe",
                    "gülmek", "gülümsemek", "şahane", "coşku", "zevk"
                ],
                "intensifiers": ["çok", "aşırı", "son derece", "gerçekten"]
            },
            "sadness": {
                "label": "Üzüntü",
                "emoji": "😢",
                "keywords": [
                    "üzgün", "hüzün", "keder", "ağlamak", "acı", "elem",
                    "mahzun", "melankoli", "kırık", "yalnız", "kayıp",
                    "üzücü", "mutsuz", "kötü", "berbat", "iç karartıcı"
                ],
                "intensifiers": ["derin", "ağır", "dayanılmaz"]
            },
            "anger": {
                "label": "Öfke",
                "emoji": "😠",
                "keywords": [
                    "sinir", "öfke", "kızgın", "hiddet", "bıktım", "yeter",
                    "dayanamam", "çileden", "delirmek", "kızmak", "tiksinmek",
                    "nefret", "gazap", "rahatsız", "sinirlendim", "canım sıkkın"
                ],
                "intensifiers": ["çok", "aşırı", "son derece"]
            },
            "fear": {
                "label": "Korku",
                "emoji": "😨",
                "keywords": [
                    "korku", "kaygı", "endişe", "panik", "telaş", "huzursuz",
                    "tedirgin", "gergin", "stres", "fobia", "dehşet",
                    "ürkütücü", "korkutucu", "ürkmek", "tekin değil"
                ],
                "intensifiers": ["dehşet verici", "korkunç"]
            },
            "disgust": {
                "label": "Tiksinme",
                "emoji": "🤢",
                "keywords": [
                    "iğrenç", "tiksinti", "mide bulandırıcı", "pis", "rahatsız edici",
                    "itici", "rezil", "berbat", "leş gibi", "terbiyesiz"
                ],
                "intensifiers": ["son derece", "aşırı"]
            },
            "surprise": {
                "label": "Şaşkınlık",
                "emoji": "😲",
                "keywords": [
                    "şaşırdım", "inanamıyorum", "vay", "hayret", "şok",
                    "beklemiyordum", "şaşırtıcı", "hayranlık", "olağanüstü",
                    "beklenmedik", "sürpriz", "olamaz", "ciddi mi"
                ],
                "intensifiers": []
            },
            "love": {
                "label": "Sevgi",
                "emoji": "❤️",
                "keywords": [
                    "sevgi", "aşk", "sevmek", "seviyorum", "aşık", "bağlılık",
                    "şefkat", "merhamet", "yumuşak", "nazik", "özen",
                    "değer vermek", "önemsemek", "bayılmak", "tapmak"
                ],
                "intensifiers": ["derin", "sonsuz", "büyük"]
            },
            "curiosity": {
                "label": "Merak",
                "emoji": "🤔",
                "keywords": [
                    "merak", "ilginç", "acaba", "neden", "nasıl", "niçin",
                    "öğrenmek", "keşfetmek", "araştırmak", "sormak",
                    "anlamak istiyorum", "bilmek istiyorum", "ilgi çekici"
                ],
                "intensifiers": []
            },
            "peace": {
                "label": "Huzur",
                "emoji": "😌",
                "keywords": [
                    "huzur", "sakin", "rahat", "dingin", "huzurlu", "sessiz",
                    "sükûnet", "rahatlık", "konfор", "barış", "huzur bulmak",
                    "rahatlamak", "gevşemek", "dinlenmek"
                ],
                "intensifiers": ["tam", "derin"]
            },
            "confidence": {
                "label": "Güven",
                "emoji": "💪",
                "keywords": [
                    "güven", "emin", "kararlı", "cesaret", "inanç", "ümit",
                    "umut", "başarabilirim", "yapabilirim", "güçlü",
                    "kararlılık", "sebat", "direnç", "kendime inanıyorum"
                ],
                "intensifiers": ["tam", "büyük", "sonsuz"]
            },
            "regret": {
                "label": "Pişmanlık",
                "emoji": "😔",
                "keywords": [
                    "pişman", "keşke", "vicdan azabı", "suçluluk", "özür",
                    "yanlış yaptım", "hata ettim", "pişmanlık duymak",
                    "nadamet", "af dilemek", "üzgünüm", "kusura bakma"
                ],
                "intensifiers": ["derin", "büyük"]
            },
            "excitement": {
                "label": "Heyecan",
                "emoji": "🎉",
                "keywords": [
                    "heyecan", "heyecanlı", "coşku", "enerji", "dinamik",
                    "motivasyon", "istekli", "tutkulu", "adrenalin",
                    "sabırsızlık", "beklenti", "ateşli", "hareketli"
                ],
                "intensifiers": ["büyük", "yoğun", "müthiş"]
            }
        }

    async def detect(self, text: str, language: str = "tr") -> List[Emotion]:
        """
        Detect emotions in text
        Returns list of emotions sorted by confidence
        """
        text_lower = text.lower()

        # Calculate emotion scores
        emotion_scores = {}

        for emotion_type, emotion_data in self.emotion_keywords.items():
            score = 0.0
            matches = []

            # Check keywords
            for keyword in emotion_data["keywords"]:
                if keyword in text_lower:
                    score += 1.0
                    matches.append(keyword)

            # Check intensifiers
            for intensifier in emotion_data.get("intensifiers", []):
                if intensifier in text_lower:
                    score *= 1.5  # Amplify emotion

            # Normalize score
            if score > 0:
                # Base confidence between 0.5 and 0.95
                confidence = min(0.5 + (score * 0.15), 0.95)
                emotion_scores[emotion_type] = {
                    "confidence": confidence,
                    "matches": matches
                }

        # If no emotions detected, use neutral default
        if not emotion_scores:
            return [Emotion(
                type="peace",
                confidence=0.3,
                label="Nötr/Huzur",
                emoji="😐"
            )]

        # Sort by confidence
        sorted_emotions = sorted(
            emotion_scores.items(),
            key=lambda x: x[1]["confidence"],
            reverse=True
        )

        # Build emotion list
        emotions = []
        for emotion_type, data in sorted_emotions[:3]:  # Top 3 emotions
            emotion_info = self.emotion_keywords[emotion_type]
            emotions.append(Emotion(
                type=emotion_type,
                confidence=round(data["confidence"], 2),
                label=emotion_info["label"],
                emoji=emotion_info["emoji"]
            ))

        logger.info(f"Detected emotions: {[(e.type, e.confidence) for e in emotions]}")

        return emotions

    def get_emotion_categories(self) -> List[Dict]:
        """
        Get all 12 emotion categories
        """
        return [
            {
                "id": i + 1,
                "type": emotion_type,
                "label": data["label"],
                "emoji": data["emoji"]
            }
            for i, (emotion_type, data) in enumerate(self.emotion_keywords.items())
        ]

    def is_ready(self) -> bool:
        """Check if detector is ready"""
        return self.ready
