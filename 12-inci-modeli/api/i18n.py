"""
Multi-language Support for 12. İnci Modeli
English and Turkish language support
"""

from typing import Dict
from enum import Enum

class Language(str, Enum):
    TURKISH = "tr"
    ENGLISH = "en"

# ============================================
# Emotion Labels
# ============================================

EMOTION_LABELS = {
    Language.TURKISH: {
        "joy": "Mutluluk",
        "sadness": "Üzüntü",
        "anger": "Öfke",
        "fear": "Korku",
        "disgust": "Tiksinme",
        "surprise": "Şaşkınlık",
        "love": "Sevgi",
        "curiosity": "Merak",
        "peace": "Huzur",
        "confidence": "Güven",
        "regret": "Pişmanlık",
        "excitement": "Heyecan"
    },
    Language.ENGLISH: {
        "joy": "Joy",
        "sadness": "Sadness",
        "anger": "Anger",
        "fear": "Fear",
        "disgust": "Disgust",
        "surprise": "Surprise",
        "love": "Love",
        "curiosity": "Curiosity",
        "peace": "Peace",
        "confidence": "Confidence",
        "regret": "Regret",
        "excitement": "Excitement"
    }
}

# ============================================
# English Emotion Keywords
# ============================================

ENGLISH_KEYWORDS = {
    "joy": [
        "happy", "joy", "great", "wonderful", "awesome", "fantastic",
        "delighted", "pleased", "glad", "cheerful", "joyful",
        "smile", "laugh", "amazing", "excited", "love it"
    ],
    "sadness": [
        "sad", "unhappy", "depressed", "down", "miserable",
        "cry", "tears", "sorrow", "grief", "heartbroken",
        "lonely", "blue", "gloomy", "melancholy"
    ],
    "anger": [
        "angry", "mad", "furious", "annoyed", "irritated",
        "frustrated", "hate", "rage", "pissed", "upset",
        "disgusted", "fed up", "enough", "can't stand"
    ],
    "fear": [
        "afraid", "scared", "fear", "worried", "anxious",
        "nervous", "panic", "terrified", "frightened",
        "concerned", "uneasy", "stressed", "tense"
    ],
    "disgust": [
        "disgusting", "gross", "sick", "revolting", "awful",
        "terrible", "horrible", "nasty", "yuck", "ew"
    ],
    "surprise": [
        "surprised", "shocked", "wow", "amazing", "unbelievable",
        "unexpected", "astonished", "stunned", "incredible",
        "can't believe", "no way", "really", "omg"
    ],
    "love": [
        "love", "adore", "cherish", "care", "affection",
        "dear", "sweet", "tender", "fond", "devoted",
        "attached", "appreciate", "value"
    ],
    "curiosity": [
        "curious", "wonder", "interesting", "how", "why",
        "what", "when", "where", "learn", "discover",
        "explore", "question", "ask", "know"
    ],
    "peace": [
        "peace", "calm", "relaxed", "tranquil", "serene",
        "quiet", "peaceful", "still", "rest", "comfortable",
        "at ease", "settled", "content"
    ],
    "confidence": [
        "confident", "sure", "certain", "believe", "faith",
        "hope", "trust", "can do", "strong", "determined",
        "capable", "bold", "courageous"
    ],
    "regret": [
        "regret", "sorry", "wish", "guilt", "remorse",
        "apologize", "my bad", "mistake", "shouldn't have",
        "if only", "wrong", "fault"
    ],
    "excitement": [
        "excited", "thrilled", "pumped", "energetic",
        "enthusiastic", "eager", "looking forward",
        "can't wait", "anticipate", "dynamic"
    ]
}

# ============================================
# System Messages
# ============================================

SYSTEM_MESSAGES = {
    Language.TURKISH: {
        "welcome": "12. İnci Modeli'ne hoş geldiniz! 💎",
        "connected": "Bağlantı başarılı!",
        "error_no_text": "Lütfen bir metin girin.",
        "error_detection": "Duygu tespiti yapılamadı.",
        "error_api": "API hatası oluştu.",
        "thank_you": "Teşekkürler!",
        "analyzing": "Analiz ediliyor...",
        "response_generated": "Yanıt oluşturuldu"
    },
    Language.ENGLISH: {
        "welcome": "Welcome to 12. İnci Model! 💎",
        "connected": "Connected successfully!",
        "error_no_text": "Please enter some text.",
        "error_detection": "Emotion detection failed.",
        "error_api": "API error occurred.",
        "thank_you": "Thank you!",
        "analyzing": "Analyzing...",
        "response_generated": "Response generated"
    }
}

# ============================================
# AI System Prompts (Multi-language)
# ============================================

AI_SYSTEM_PROMPTS = {
    Language.TURKISH: """Sen 12. İnci (Pearl) Modeli adlı duygusal zeka asistanısın. modulLLM.com platformu üzerinde çalışıyorsun.

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

Kullanıcının duygularına uygun, yardımcı ve anlayışlı bir yanıt ver.""",

    Language.ENGLISH: """You are 12. İnci (Pearl) Model, an emotional intelligence assistant. You operate on the modulLLM.com platform.

**Your Task:**
Understand the user's emotional state and provide empathetic, appropriate responses.

**Detected Emotions:** {emotion_context}

**Response Guidelines:**
1. Use a tone appropriate to the user's emotional state
2. Show empathy and validate their feelings
3. Be constructive and supportive
4. Use natural and genuine language
5. Use emojis sparingly (only when appropriate)
6. Respond in English

Provide a helpful and understanding response appropriate to the user's emotions."""
}

# ============================================
# Helper Functions
# ============================================

def get_emotion_label(emotion_type: str, language: Language = Language.TURKISH) -> str:
    """Get emotion label in specified language"""
    return EMOTION_LABELS.get(language, {}).get(emotion_type, emotion_type)

def get_message(key: str, language: Language = Language.TURKISH) -> str:
    """Get system message in specified language"""
    return SYSTEM_MESSAGES.get(language, {}).get(key, key)

def get_ai_prompt(emotion_context: str, language: Language = Language.TURKISH) -> str:
    """Get AI system prompt in specified language"""
    template = AI_SYSTEM_PROMPTS.get(language, AI_SYSTEM_PROMPTS[Language.TURKISH])
    return template.format(emotion_context=emotion_context)

def get_keywords_for_language(language: Language) -> Dict:
    """Get emotion keywords for specified language"""
    if language == Language.ENGLISH:
        return ENGLISH_KEYWORDS
    else:
        # Return Turkish keywords from emotion_detector.py
        from emotion_detector import EmotionDetector
        detector = EmotionDetector()
        keywords = {}
        for emotion_type, data in detector.emotion_keywords.items():
            keywords[emotion_type] = data.get("keywords", [])
        return keywords
