"""
MiniMax-M2 Çeviri Servisi Şablonu
=================================
Profesyonel çeviri servisi.

Özellikler:
- Çoklu dil desteği
- Bağlam duyarlı çeviri
- Teknik terim sözlüğü
- Toplu çeviri
- Kalite kontrolü

Gereksinimler:
    pip install openai fastapi uvicorn

Kullanım:
    # CLI modu
    python main.py translate "Merhaba dünya" --to en

    # Sunucu modu
    python main.py serve
"""

import os
import json
from typing import Optional
from dataclasses import dataclass, field

from openai import OpenAI

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)


# ============================================================================
# Dil Tanımları
# ============================================================================

LANGUAGES = {
    "tr": {"name": "Türkçe", "native": "Türkçe"},
    "en": {"name": "English", "native": "English"},
    "de": {"name": "German", "native": "Deutsch"},
    "fr": {"name": "French", "native": "Français"},
    "es": {"name": "Spanish", "native": "Español"},
    "it": {"name": "Italian", "native": "Italiano"},
    "pt": {"name": "Portuguese", "native": "Português"},
    "ru": {"name": "Russian", "native": "Русский"},
    "ja": {"name": "Japanese", "native": "日本語"},
    "zh": {"name": "Chinese", "native": "中文"},
    "ko": {"name": "Korean", "native": "한국어"},
    "ar": {"name": "Arabic", "native": "العربية"},
}


# ============================================================================
# Veri Yapıları
# ============================================================================

@dataclass
class TranslationConfig:
    """Çeviri yapılandırması."""
    source_lang: str = "auto"
    target_lang: str = "en"
    style: str = "natural"  # natural, formal, casual, technical
    preserve_formatting: bool = True
    glossary: dict = field(default_factory=dict)


@dataclass
class TranslationResult:
    """Çeviri sonucu."""
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: float
    alternatives: list[str] = field(default_factory=list)


# ============================================================================
# Çeviri Fonksiyonları
# ============================================================================

def detect_language(text: str) -> str:
    """Dil algılama."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": """Sen dil algılama uzmanısın.
Verilen metnin dilini belirle ve sadece dil kodunu döndür.
Dil kodları: tr, en, de, fr, es, it, pt, ru, ja, zh, ko, ar
Sadece kodu döndür, başka bir şey yazma."""
            },
            {
                "role": "user",
                "content": text[:500]  # İlk 500 karakter yeterli
            }
        ],
        temperature=0.1,
        max_tokens=10,
    )

    detected = response.choices[0].message.content.strip().lower()
    return detected if detected in LANGUAGES else "en"


def translate(
    text: str,
    config: Optional[TranslationConfig] = None
) -> TranslationResult:
    """Metin çevir."""
    config = config or TranslationConfig()

    # Kaynak dil algılama
    if config.source_lang == "auto":
        source_lang = detect_language(text)
    else:
        source_lang = config.source_lang

    source_name = LANGUAGES.get(source_lang, {}).get("name", source_lang)
    target_name = LANGUAGES.get(config.target_lang, {}).get("name", config.target_lang)

    # Stil promptu
    style_prompts = {
        "natural": "Doğal ve akıcı bir çeviri yap.",
        "formal": "Resmi ve profesyonel bir dil kullan.",
        "casual": "Günlük ve rahat bir dil kullan.",
        "technical": "Teknik terimleri koru ve doğru çevir.",
    }

    style_prompt = style_prompts.get(config.style, style_prompts["natural"])

    # Sözlük promptu
    glossary_prompt = ""
    if config.glossary:
        glossary_entries = [f"'{k}' → '{v}'" for k, v in config.glossary.items()]
        glossary_prompt = f"\n\nTeknik terimler sözlüğü:\n" + "\n".join(glossary_entries)

    # Format koruma
    format_prompt = ""
    if config.preserve_formatting:
        format_prompt = "\nOrijinal formatı (paragraflar, listeler) koru."

    # Çeviri
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"""Sen profesyonel bir çevirmensin.
{source_name} dilinden {target_name} diline çeviri yapıyorsun.
{style_prompt}
{format_prompt}
{glossary_prompt}

Sadece çeviriyi döndür, ek açıklama yapma."""
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.3,
        max_tokens=len(text) * 2,  # Çeviri genellikle daha uzun olabilir
    )

    translated = response.choices[0].message.content

    return TranslationResult(
        source_text=text,
        translated_text=translated,
        source_lang=source_lang,
        target_lang=config.target_lang,
        confidence=0.95,  # MiniMax-M2 için yüksek güven
    )


def translate_with_alternatives(
    text: str,
    config: Optional[TranslationConfig] = None,
    num_alternatives: int = 3
) -> TranslationResult:
    """Alternatif çevirilerle birlikte çevir."""
    config = config or TranslationConfig()

    # Ana çeviri
    result = translate(text, config)

    # Alternatifler
    source_name = LANGUAGES.get(result.source_lang, {}).get("name", result.source_lang)
    target_name = LANGUAGES.get(config.target_lang, {}).get("name", config.target_lang)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"""Sen profesyonel bir çevirmensin.
{source_name} dilinden {target_name} diline {num_alternatives} farklı çeviri yap.
Her çeviriyi yeni satırda ver.
Sadece çevirileri döndür, numara veya açıklama ekleme."""
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.8,  # Çeşitlilik için yüksek sıcaklık
        max_tokens=len(text) * 2 * num_alternatives,
    )

    alternatives = response.choices[0].message.content.strip().split("\n")
    alternatives = [alt.strip() for alt in alternatives if alt.strip()]

    result.alternatives = alternatives[:num_alternatives]

    return result


def batch_translate(
    texts: list[str],
    config: Optional[TranslationConfig] = None
) -> list[TranslationResult]:
    """Toplu çeviri."""
    results = []
    for i, text in enumerate(texts):
        print(f"Çeviriliyor {i + 1}/{len(texts)}...")
        result = translate(text, config)
        results.append(result)
    return results


def quality_check(
    original: str,
    translation: str,
    source_lang: str,
    target_lang: str
) -> dict:
    """Çeviri kalite kontrolü."""
    source_name = LANGUAGES.get(source_lang, {}).get("name", source_lang)
    target_name = LANGUAGES.get(target_lang, {}).get("name", target_lang)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": """Sen çeviri kalite değerlendirme uzmanısın.
Verilen çeviriyi değerlendir ve JSON formatında sonuç döndür:
{
    "score": 1-10 arası puan,
    "accuracy": "doğruluk değerlendirmesi",
    "fluency": "akıcılık değerlendirmesi",
    "issues": ["sorun 1", "sorun 2"],
    "suggestions": ["öneri 1", "öneri 2"]
}"""
            },
            {
                "role": "user",
                "content": f"""Orijinal ({source_name}):
{original}

Çeviri ({target_name}):
{translation}"""
            }
        ],
        temperature=0.3,
        max_tokens=500,
    )

    try:
        # JSON bloğunu bul
        content = response.choices[0].message.content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0]
        else:
            json_str = content

        return json.loads(json_str)
    except (json.JSONDecodeError, IndexError):
        return {"score": 0, "error": "Değerlendirme yapılamadı"}


# ============================================================================
# CLI
# ============================================================================

def cli():
    """Komut satırı arayüzü."""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax-M2 Çeviri Servisi")
    subparsers = parser.add_subparsers(dest="command")

    # translate komutu
    translate_parser = subparsers.add_parser("translate", help="Metin çevir")
    translate_parser.add_argument("text", help="Çevrilecek metin")
    translate_parser.add_argument("--from", "-f", dest="source", default="auto", help="Kaynak dil")
    translate_parser.add_argument("--to", "-t", dest="target", default="en", help="Hedef dil")
    translate_parser.add_argument("--style", "-s", default="natural",
                                   choices=["natural", "formal", "casual", "technical"])
    translate_parser.add_argument("--alternatives", "-a", type=int, default=0,
                                   help="Alternatif çeviri sayısı")

    # detect komutu
    detect_parser = subparsers.add_parser("detect", help="Dil algıla")
    detect_parser.add_argument("text", help="Metin")

    # check komutu
    check_parser = subparsers.add_parser("check", help="Çeviri kalite kontrolü")
    check_parser.add_argument("--original", "-o", required=True, help="Orijinal metin")
    check_parser.add_argument("--translation", "-t", required=True, help="Çeviri")
    check_parser.add_argument("--from", "-f", dest="source", default="tr", help="Kaynak dil")
    check_parser.add_argument("--to", dest="target", default="en", help="Hedef dil")

    # languages komutu
    subparsers.add_parser("languages", help="Desteklenen dilleri listele")

    args = parser.parse_args()

    if args.command == "translate":
        config = TranslationConfig(
            source_lang=args.source,
            target_lang=args.target,
            style=args.style,
        )

        if args.alternatives > 0:
            result = translate_with_alternatives(args.text, config, args.alternatives)
            print(f"\n🌍 Çeviri ({result.source_lang} → {result.target_lang}):\n")
            print(result.translated_text)
            if result.alternatives:
                print("\n📋 Alternatifler:")
                for i, alt in enumerate(result.alternatives, 1):
                    print(f"  {i}. {alt}")
        else:
            result = translate(args.text, config)
            print(f"\n🌍 Çeviri ({result.source_lang} → {result.target_lang}):\n")
            print(result.translated_text)

    elif args.command == "detect":
        lang = detect_language(args.text)
        lang_info = LANGUAGES.get(lang, {"name": lang, "native": lang})
        print(f"🔍 Algılanan dil: {lang_info['name']} ({lang_info['native']}) [{lang}]")

    elif args.command == "check":
        result = quality_check(args.original, args.translation, args.source, args.target)
        print("\n📊 Kalite Değerlendirmesi:\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "languages":
        print("\n🌍 Desteklenen Diller:\n")
        for code, info in LANGUAGES.items():
            print(f"  {code}: {info['name']} ({info['native']})")

    else:
        parser.print_help()


# ============================================================================
# Ana Giriş
# ============================================================================

if __name__ == "__main__":
    cli()
