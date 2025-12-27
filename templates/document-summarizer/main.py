"""
MiniMax-M2 Belge Özetleme Şablonu
=================================
Uzun belgeleri akıllıca özetleyen sistem.

Özellikler:
- Uzun belge desteği (chunking)
- Hiyerarşik özetleme
- Farklı özet stilleri
- PDF/TXT/MD dosya desteği

Gereksinimler:
    pip install openai pypdf

Kullanım:
    python main.py document.pdf
    python main.py document.txt --style bullet
"""

import os
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from openai import OpenAI

try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# Özetleme ayarları
CHUNK_SIZE = 4000  # Karakter
CHUNK_OVERLAP = 200

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)


# ============================================================================
# Veri Yapıları
# ============================================================================

@dataclass
class SummaryConfig:
    """Özetleme yapılandırması."""
    style: str = "paragraph"  # paragraph, bullet, executive, academic
    length: str = "medium"    # short, medium, long
    language: str = "tr"      # tr, en
    focus: Optional[str] = None  # Odaklanılacak konu


@dataclass
class DocumentChunk:
    """Belge parçası."""
    index: int
    content: str
    summary: Optional[str] = None


@dataclass
class SummaryResult:
    """Özetleme sonucu."""
    original_length: int
    summary_length: int
    compression_ratio: float
    chunks_count: int
    summary: str
    chunk_summaries: list[str]


# ============================================================================
# Belge İşleme
# ============================================================================

def read_pdf(file_path: str) -> str:
    """PDF dosyasını oku."""
    if not PDF_AVAILABLE:
        raise ImportError("pypdf gerekli: pip install pypdf")

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def read_text(file_path: str) -> str:
    """Metin dosyasını oku."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_document(file_path: str) -> str:
    """Belgeyi oku (otomatik format algılama)."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")

    if path.suffix.lower() == ".pdf":
        return read_pdf(file_path)
    elif path.suffix.lower() in [".txt", ".md", ".rst"]:
        return read_text(file_path)
    else:
        # Varsayılan olarak metin olarak oku
        return read_text(file_path)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[DocumentChunk]:
    """Metni parçalara ayır."""
    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = start + chunk_size

        # Cümle sınırında kes
        if end < len(text):
            # Son nokta, soru işareti veya ünlem işaretini bul
            for sep in [". ", "? ", "! ", "\n\n"]:
                last_sep = text.rfind(sep, start, end)
                if last_sep > start + chunk_size // 2:
                    end = last_sep + len(sep)
                    break

        chunk_content = text[start:end].strip()

        if chunk_content:
            chunks.append(DocumentChunk(
                index=index,
                content=chunk_content
            ))
            index += 1

        start = end - overlap

    return chunks


# ============================================================================
# Özetleme Fonksiyonları
# ============================================================================

def get_style_prompt(config: SummaryConfig) -> str:
    """Stil promptu oluştur."""
    style_prompts = {
        "paragraph": "Akıcı paragraflar halinde yaz.",
        "bullet": "Madde işaretleri ile listele. Her nokta kısa ve öz olsun.",
        "executive": "Yönetici özeti formatında yaz. Anahtar bulguları ve önerileri vurgula.",
        "academic": "Akademik bir dilde yaz. Temel argümanları ve metodolojisini belirt.",
    }

    length_prompts = {
        "short": "Çok kısa tut (2-3 cümle veya 3-5 madde).",
        "medium": "Orta uzunlukta tut (1 paragraf veya 5-10 madde).",
        "long": "Detaylı yaz (2-3 paragraf veya 10-15 madde).",
    }

    language_prompts = {
        "tr": "Türkçe yaz.",
        "en": "İngilizce yaz.",
    }

    parts = [
        style_prompts.get(config.style, style_prompts["paragraph"]),
        length_prompts.get(config.length, length_prompts["medium"]),
        language_prompts.get(config.language, language_prompts["tr"]),
    ]

    if config.focus:
        parts.append(f"Özellikle şu konuya odaklan: {config.focus}")

    return " ".join(parts)


def summarize_chunk(chunk: DocumentChunk, config: SummaryConfig) -> str:
    """Tek bir parçayı özetle."""
    style_prompt = get_style_prompt(config)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"Sen profesyonel bir metin özetleyicisisin. {style_prompt}"
            },
            {
                "role": "user",
                "content": f"Bu metni özetle:\n\n{chunk.content}"
            }
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    return response.choices[0].message.content


def combine_summaries(summaries: list[str], config: SummaryConfig) -> str:
    """Parça özetlerini birleştir."""
    combined = "\n\n---\n\n".join(summaries)

    style_prompt = get_style_prompt(config)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"""Sen profesyonel bir metin özetleyicisisin.
Verilen parça özetlerini tutarlı bir bütün haline getir.
Tekrarları kaldır ve akış sağla.
{style_prompt}"""
            },
            {
                "role": "user",
                "content": f"Bu parça özetlerini birleştirerek tek bir özet oluştur:\n\n{combined}"
            }
        ],
        temperature=0.3,
        max_tokens=2048,
    )

    return response.choices[0].message.content


def summarize_document(
    text: str,
    config: Optional[SummaryConfig] = None
) -> SummaryResult:
    """
    Belgeyi özetle.

    Uzun belgeler için hiyerarşik özetleme kullanır:
    1. Belgeyi parçalara ayır
    2. Her parçayı özetle
    3. Parça özetlerini birleştir
    """
    config = config or SummaryConfig()

    # Metni parçala
    chunks = chunk_text(text)
    print(f"📄 Belge {len(chunks)} parçaya ayrıldı.")

    # Her parçayı özetle
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"  Parça {i + 1}/{len(chunks)} özetleniyor...")
        summary = summarize_chunk(chunk, config)
        chunk.summary = summary
        chunk_summaries.append(summary)

    # Parça özetlerini birleştir
    if len(chunk_summaries) > 1:
        print("📝 Özetler birleştiriliyor...")
        final_summary = combine_summaries(chunk_summaries, config)
    else:
        final_summary = chunk_summaries[0] if chunk_summaries else ""

    # Sonuç
    return SummaryResult(
        original_length=len(text),
        summary_length=len(final_summary),
        compression_ratio=len(final_summary) / len(text) if len(text) > 0 else 0,
        chunks_count=len(chunks),
        summary=final_summary,
        chunk_summaries=chunk_summaries,
    )


# ============================================================================
# CLI
# ============================================================================

def main():
    """Ana fonksiyon."""
    import argparse

    parser = argparse.ArgumentParser(
        description="MiniMax-M2 Belge Özetleme Aracı"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Özetlenecek dosya (PDF, TXT, MD)"
    )
    parser.add_argument(
        "--style", "-s",
        choices=["paragraph", "bullet", "executive", "academic"],
        default="paragraph",
        help="Özet stili"
    )
    parser.add_argument(
        "--length", "-l",
        choices=["short", "medium", "long"],
        default="medium",
        help="Özet uzunluğu"
    )
    parser.add_argument(
        "--language", "-L",
        choices=["tr", "en"],
        default="tr",
        help="Özet dili"
    )
    parser.add_argument(
        "--focus", "-f",
        help="Odaklanılacak konu"
    )
    parser.add_argument(
        "--output", "-o",
        help="Çıktı dosyası"
    )

    args = parser.parse_args()

    # Dosya veya stdin'den oku
    if args.file:
        print(f"📖 Dosya okunuyor: {args.file}")
        text = read_document(args.file)
    elif not sys.stdin.isatty():
        print("📖 Stdin'den okunuyor...")
        text = sys.stdin.read()
    else:
        parser.print_help()
        return

    # Yapılandırma
    config = SummaryConfig(
        style=args.style,
        length=args.length,
        language=args.language,
        focus=args.focus,
    )

    print(f"📊 Belge uzunluğu: {len(text)} karakter")
    print(f"⚙️  Stil: {config.style}, Uzunluk: {config.length}")

    # Özetle
    result = summarize_document(text, config)

    # Sonucu göster
    print("\n" + "="*60)
    print("📋 ÖZET")
    print("="*60 + "\n")
    print(result.summary)

    print("\n" + "-"*60)
    print(f"📊 İstatistikler:")
    print(f"   Orijinal: {result.original_length} karakter")
    print(f"   Özet: {result.summary_length} karakter")
    print(f"   Sıkıştırma: {result.compression_ratio:.1%}")
    print(f"   Parça sayısı: {result.chunks_count}")

    # Çıktı dosyasına yaz
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.summary)
        print(f"\n✅ Özet kaydedildi: {args.output}")


if __name__ == "__main__":
    main()
