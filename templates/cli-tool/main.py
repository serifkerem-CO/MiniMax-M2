#!/usr/bin/env python3
"""
MiniMax-M2 CLI Aracı Şablonu
============================
Komut satırından MiniMax-M2 ile etkileşim.

Özellikler:
- İnteraktif sohbet modu
- Tek seferlik sorgular
- Pipe desteği (stdin/stdout)
- Dosya işleme
- Özelleştirilebilir çıktı

Gereksinimler:
    pip install openai click rich

Kullanım:
    # İnteraktif mod
    python main.py chat

    # Tek seferlik sorgu
    python main.py ask "Python nedir?"

    # Pipe ile kullanım
    cat code.py | python main.py analyze

    # Dosya analizi
    python main.py analyze --file code.py
"""

import os
import sys
from typing import Optional

import click
from openai import OpenAI

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)

# Rich konsol
console = Console() if RICH_AVAILABLE else None


def output(text: str, markdown: bool = True):
    """Çıktı fonksiyonu."""
    if console and markdown:
        console.print(Markdown(text))
    else:
        print(text)


def get_response(
    prompt: str,
    system_prompt: str = "Sen yardımcı bir asistansın.",
    temperature: float = 0.7,
    max_tokens: int = 2048,
    stream: bool = False
) -> str:
    """AI yanıtı al."""
    try:
        if stream:
            response_text = ""
            stream_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    response_text += content
                    print(content, end="", flush=True)

            print()  # Yeni satır
            return response_text
        else:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

    except Exception as e:
        return f"Hata: {str(e)}"


# ============================================================================
# CLI Komutları
# ============================================================================

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """MiniMax-M2 CLI Aracı - AI destekli komut satırı asistanı."""
    pass


@cli.command()
@click.option("--system", "-s", default="Sen yardımcı bir asistansın.", help="Sistem promptu")
@click.option("--temperature", "-t", default=0.7, type=float, help="Sıcaklık (0-2)")
@click.option("--max-tokens", "-m", default=2048, type=int, help="Maksimum token")
def chat(system: str, temperature: float, max_tokens: int):
    """İnteraktif sohbet modu."""
    if console:
        console.print(Panel.fit(
            "[bold blue]MiniMax-M2 Sohbet[/bold blue]\n"
            "Çıkmak için 'exit' veya Ctrl+C yazın.",
            title="🤖"
        ))
    else:
        print("=== MiniMax-M2 Sohbet ===")
        print("Çıkmak için 'exit' yazın.\n")

    history = []

    while True:
        try:
            user_input = input("\n👤 Sen: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGüle güle!")
            break

        if user_input.lower() in ["exit", "quit", "q", "çık"]:
            print("Güle güle!")
            break

        if not user_input:
            continue

        if user_input == "/clear":
            history = []
            print("Geçmiş temizlendi.")
            continue

        # Mesajları hazırla
        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        print("\n🤖 MiniMax: ", end="")

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    print(content, end="", flush=True)

            print()

            # Geçmişe ekle
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": full_response})

            # Geçmiş limitini kontrol et
            if len(history) > 20:
                history = history[-20:]

        except Exception as e:
            print(f"\nHata: {e}")


@cli.command()
@click.argument("question")
@click.option("--system", "-s", default="Sen yardımcı bir asistansın.", help="Sistem promptu")
@click.option("--temperature", "-t", default=0.7, type=float, help="Sıcaklık")
@click.option("--stream/--no-stream", default=True, help="Streaming mod")
@click.option("--raw", is_flag=True, help="Markdown formatı olmadan çıktı")
def ask(question: str, system: str, temperature: float, stream: bool, raw: bool):
    """Tek seferlik soru sor."""
    response = get_response(question, system, temperature, stream=stream)

    if not stream:
        if raw:
            print(response)
        else:
            output(response)


@cli.command()
@click.option("--file", "-f", type=click.Path(exists=True), help="Analiz edilecek dosya")
@click.option("--language", "-l", default="auto", help="Programlama dili")
@click.option("--type", "analysis_type", type=click.Choice(["explain", "review", "fix", "optimize"]),
              default="explain", help="Analiz türü")
def analyze(file: Optional[str], language: str, analysis_type: str):
    """Kod analizi yap."""
    # Kodu al (dosyadan veya stdin'den)
    if file:
        with open(file, "r") as f:
            code = f.read()
        if language == "auto":
            ext = os.path.splitext(file)[1]
            lang_map = {".py": "python", ".js": "javascript", ".ts": "typescript",
                        ".go": "go", ".rs": "rust", ".java": "java", ".cpp": "c++"}
            language = lang_map.get(ext, "code")
    elif not sys.stdin.isatty():
        code = sys.stdin.read()
        if language == "auto":
            language = "code"
    else:
        print("Hata: Dosya belirtin veya stdin'den kod gönderin.")
        return

    type_prompts = {
        "explain": "Bu kodu açıkla:",
        "review": "Bu kodu incele ve iyileştirme önerileri sun:",
        "fix": "Bu koddaki hataları bul ve düzelt:",
        "optimize": "Bu kodu optimize et:",
    }

    prompt = f"{type_prompts[analysis_type]}\n\n```{language}\n{code}\n```"

    if console:
        console.print(f"\n[bold]🔍 Kod Analizi ({analysis_type})[/bold]\n")

    response = get_response(
        prompt,
        system_prompt="Sen uzman bir kod analistisin.",
        temperature=0.3,
        stream=True
    )


@cli.command()
@click.argument("description")
@click.option("--language", "-l", default="python", help="Programlama dili")
@click.option("--output", "-o", type=click.Path(), help="Çıktı dosyası")
def generate(description: str, language: str, output: Optional[str]):
    """Açıklamadan kod üret."""
    prompt = f"{language} ile şunu yaz:\n\n{description}"

    response = get_response(
        prompt,
        system_prompt=f"Sen uzman bir {language} geliştiricisisin. Sadece kod döndür, açıklama ekleme.",
        temperature=0.3,
        stream=not output
    )

    if output:
        # Markdown kod bloğunu çıkar
        code = response
        if f"```{language}" in response:
            code = response.split(f"```{language}")[1].split("```")[0]
        elif "```" in response:
            code = response.split("```")[1].split("```")[0]

        with open(output, "w") as f:
            f.write(code.strip())
        print(f"Kod yazıldı: {output}")


@cli.command()
@click.argument("text")
@click.option("--to", "-t", default="İngilizce", help="Hedef dil")
@click.option("--from", "from_lang", default="auto", help="Kaynak dil")
def translate(text: str, to: str, from_lang: str):
    """Metin çevir."""
    if from_lang == "auto":
        prompt = f"Bu metni {to} diline çevir:\n\n{text}"
    else:
        prompt = f"Bu metni {from_lang} dilinden {to} diline çevir:\n\n{text}"

    response = get_response(
        prompt,
        system_prompt="Sen profesyonel bir çevirmensin. Sadece çeviriyi döndür.",
        temperature=0.3,
        stream=True
    )


@cli.command()
@click.argument("text")
@click.option("--style", "-s", type=click.Choice(["short", "medium", "long"]),
              default="medium", help="Özet uzunluğu")
def summarize(text: str, style: str):
    """Metin özetle."""
    style_map = {
        "short": "1-2 cümle ile",
        "medium": "1 paragraf ile",
        "long": "detaylı bir şekilde"
    }

    prompt = f"Bu metni {style_map[style]} özetle:\n\n{text}"

    response = get_response(
        prompt,
        system_prompt="Sen metin özetleme uzmanısın.",
        temperature=0.5,
        stream=True
    )


@cli.command()
def config():
    """Yapılandırmayı göster."""
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Model: {MODEL_NAME}")
    print(f"API Key: {'*' * 8}...{API_KEY[-4:] if len(API_KEY) > 4 else '****'}")


# ============================================================================
# Ana Giriş
# ============================================================================

if __name__ == "__main__":
    cli()
