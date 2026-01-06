"""
MiniMax-M2 Kod İnceleme Şablonu
===============================
AI destekli kod inceleme ve kalite analizi.

Özellikler:
- Kod kalitesi analizi
- Güvenlik açıkları tespiti
- Performans önerileri
- Best practice kontrolleri
- Git diff inceleme

Gereksinimler:
    pip install openai gitpython rich

Kullanım:
    python main.py review file.py
    python main.py diff HEAD~1
    python main.py security src/
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
console = Console()


# ============================================================================
# Veri Yapıları
# ============================================================================

@dataclass
class ReviewIssue:
    """İnceleme sorunu."""
    severity: str  # critical, warning, info, suggestion
    category: str  # security, performance, quality, style
    line: Optional[int]
    message: str
    suggestion: Optional[str] = None


@dataclass
class ReviewResult:
    """İnceleme sonucu."""
    file_path: str
    language: str
    issues: list[ReviewIssue] = field(default_factory=list)
    summary: str = ""
    score: int = 0  # 0-100


# ============================================================================
# Kod Analizi
# ============================================================================

def detect_language(file_path: str) -> str:
    """Dosya dilini tespit et."""
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".cpp": "cpp",
        ".c": "c",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".cs": "csharp",
        ".sh": "bash",
        ".sql": "sql",
    }
    ext = Path(file_path).suffix.lower()
    return ext_map.get(ext, "text")


def get_syntax_errors(code: str, language: str) -> list[str]:
    """Syntax hatalarını kontrol et."""
    errors = []

    if language == "python":
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Satır {e.lineno}: {e.msg}")

    return errors


# ============================================================================
# AI İnceleme
# ============================================================================

def review_code(code: str, language: str, focus: str = "general") -> ReviewResult:
    """Kodu AI ile incele."""

    focus_prompts = {
        "general": "Genel kod kalitesi, okunabilirlik ve best practice",
        "security": "Güvenlik açıkları ve zafiyetler",
        "performance": "Performans sorunları ve optimizasyon fırsatları",
        "style": "Kod stili ve formatlama",
    }

    prompt = f"""Bu {language} kodunu incele. Odak: {focus_prompts.get(focus, focus)}

KOD:
```{language}
{code}
```

Analiz sonucunu şu JSON formatında döndür:
{{
    "issues": [
        {{
            "severity": "critical|warning|info|suggestion",
            "category": "security|performance|quality|style",
            "line": <satır numarası veya null>,
            "message": "<sorun açıklaması>",
            "suggestion": "<düzeltme önerisi>"
        }}
    ],
    "summary": "<genel değerlendirme>",
    "score": <0-100 arası puan>
}}

Sadece JSON döndür."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen uzman bir kod inceleme asistanısın. Türkçe yanıt ver."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4000,
    )

    try:
        import json
        content = response.choices[0].message.content

        # JSON'u çıkar
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0]
        else:
            json_str = content

        data = json.loads(json_str)

        issues = [
            ReviewIssue(
                severity=i.get("severity", "info"),
                category=i.get("category", "quality"),
                line=i.get("line"),
                message=i.get("message", ""),
                suggestion=i.get("suggestion")
            )
            for i in data.get("issues", [])
        ]

        return ReviewResult(
            file_path="",
            language=language,
            issues=issues,
            summary=data.get("summary", ""),
            score=data.get("score", 0)
        )
    except Exception as e:
        return ReviewResult(
            file_path="",
            language=language,
            issues=[ReviewIssue("warning", "quality", None, f"Analiz hatası: {e}", None)],
            summary="Kod analiz edilemedi.",
            score=0
        )


def review_diff(diff_text: str) -> str:
    """Git diff'i incele."""

    prompt = f"""Bu git diff'ini incele ve değişiklikleri değerlendir:

{diff_text}

Şunları analiz et:
1. Değişikliklerin amacı
2. Potansiyel sorunlar
3. İyileştirme önerileri
4. Genel değerlendirme

Türkçe ve markdown formatında yanıt ver."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen uzman bir kod inceleme asistanısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4000,
    )

    return response.choices[0].message.content


def security_scan(code: str, language: str) -> list[ReviewIssue]:
    """Güvenlik taraması yap."""

    security_patterns = {
        "python": [
            (r"eval\s*\(", "Tehlikeli eval() kullanımı"),
            (r"exec\s*\(", "Tehlikeli exec() kullanımı"),
            (r"subprocess\..*shell\s*=\s*True", "Shell injection riski"),
            (r"pickle\.load", "Güvensiz pickle kullanımı"),
            (r"input\s*\(", "Doğrulanmamış kullanıcı girdisi"),
            (r"password\s*=\s*['\"]", "Hardcoded şifre"),
            (r"api_key\s*=\s*['\"]", "Hardcoded API anahtarı"),
            (r"\.format\(.*\)", "Potansiyel format string vulnerability"),
            (r"os\.system\s*\(", "OS command injection riski"),
        ],
        "javascript": [
            (r"eval\s*\(", "Tehlikeli eval() kullanımı"),
            (r"innerHTML\s*=", "XSS riski - innerHTML"),
            (r"document\.write\s*\(", "XSS riski - document.write"),
            (r"password\s*[=:]\s*['\"]", "Hardcoded şifre"),
            (r"api_key\s*[=:]\s*['\"]", "Hardcoded API anahtarı"),
            (r"localStorage\.setItem.*password", "Şifre localStorage'da"),
        ],
    }

    issues = []
    patterns = security_patterns.get(language, [])
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        for pattern, message in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(ReviewIssue(
                    severity="critical",
                    category="security",
                    line=i,
                    message=message,
                    suggestion="Bu kodu gözden geçirin ve güvenli alternatif kullanın."
                ))

    return issues


# ============================================================================
# Çıktı Formatlama
# ============================================================================

def display_result(result: ReviewResult, code: str = None):
    """Sonucu göster."""

    # Başlık
    console.print()
    console.print(Panel(
        f"[bold]Kod İnceleme Sonucu[/bold]\n"
        f"Dil: {result.language} | Puan: {result.score}/100",
        title="📝 MiniMax-M2 Code Review"
    ))

    # Kod (varsa)
    if code and len(code) < 2000:
        console.print("\n[bold]Kod:[/bold]")
        syntax = Syntax(code, result.language, theme="monokai", line_numbers=True)
        console.print(syntax)

    # Sorunlar tablosu
    if result.issues:
        console.print("\n[bold]Bulunan Sorunlar:[/bold]")

        table = Table(show_header=True)
        table.add_column("Seviye", style="bold")
        table.add_column("Kategori")
        table.add_column("Satır")
        table.add_column("Mesaj")

        severity_colors = {
            "critical": "red",
            "warning": "yellow",
            "info": "blue",
            "suggestion": "green",
        }

        for issue in result.issues:
            color = severity_colors.get(issue.severity, "white")
            table.add_row(
                f"[{color}]{issue.severity}[/{color}]",
                issue.category,
                str(issue.line) if issue.line else "-",
                issue.message
            )

        console.print(table)

        # Öneriler
        suggestions = [i for i in result.issues if i.suggestion]
        if suggestions:
            console.print("\n[bold]Öneriler:[/bold]")
            for i, issue in enumerate(suggestions, 1):
                console.print(f"  {i}. [dim]Satır {issue.line or '?'}:[/dim] {issue.suggestion}")

    # Özet
    if result.summary:
        console.print("\n[bold]Özet:[/bold]")
        console.print(Panel(result.summary))

    # Puan göstergesi
    score = result.score
    if score >= 80:
        color = "green"
        emoji = "✅"
    elif score >= 60:
        color = "yellow"
        emoji = "⚠️"
    else:
        color = "red"
        emoji = "❌"

    console.print(f"\n{emoji} Kod Kalitesi: [{color}]{score}/100[/{color}]")


def display_diff_review(review: str):
    """Diff incelemesini göster."""
    console.print()
    console.print(Panel(
        Markdown(review),
        title="📝 Git Diff İncelemesi"
    ))


# ============================================================================
# CLI
# ============================================================================

def main():
    """Ana fonksiyon."""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax-M2 Kod İnceleme")
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # review komutu
    review_parser = subparsers.add_parser("review", help="Dosya incele")
    review_parser.add_argument("file", help="İncelenecek dosya")
    review_parser.add_argument("--focus", "-f",
        choices=["general", "security", "performance", "style"],
        default="general", help="İnceleme odağı")

    # diff komutu
    diff_parser = subparsers.add_parser("diff", help="Git diff incele")
    diff_parser.add_argument("ref", nargs="?", default="HEAD", help="Git referansı")

    # security komutu
    security_parser = subparsers.add_parser("security", help="Güvenlik taraması")
    security_parser.add_argument("path", help="Taranacak dosya/dizin")

    # demo komutu
    subparsers.add_parser("demo", help="Demo")

    args = parser.parse_args()

    if args.command == "review":
        # Dosya incele
        file_path = Path(args.file)
        if not file_path.exists():
            console.print(f"[red]Dosya bulunamadı: {file_path}[/red]")
            return

        code = file_path.read_text()
        language = detect_language(str(file_path))

        console.print(f"[dim]İnceleniyor: {file_path} ({language})[/dim]")

        # Syntax kontrol
        syntax_errors = get_syntax_errors(code, language)

        # AI inceleme
        result = review_code(code, language, args.focus)
        result.file_path = str(file_path)

        # Syntax hatalarını ekle
        for error in syntax_errors:
            result.issues.insert(0, ReviewIssue(
                severity="critical",
                category="quality",
                line=None,
                message=f"Syntax hatası: {error}",
                suggestion="Syntax hatasını düzeltin."
            ))

        display_result(result, code)

    elif args.command == "diff":
        # Git diff incele
        try:
            import subprocess
            diff = subprocess.check_output(
                ["git", "diff", args.ref],
                text=True
            )

            if not diff:
                console.print("[yellow]Değişiklik yok.[/yellow]")
                return

            console.print(f"[dim]Git diff inceleniyor: {args.ref}[/dim]")
            review = review_diff(diff)
            display_diff_review(review)

        except subprocess.CalledProcessError:
            console.print("[red]Git diff alınamadı.[/red]")

    elif args.command == "security":
        # Güvenlik taraması
        path = Path(args.path)

        if path.is_file():
            files = [path]
        else:
            files = list(path.rglob("*"))

        all_issues = []

        for file_path in files:
            if not file_path.is_file():
                continue

            language = detect_language(str(file_path))
            if language == "text":
                continue

            try:
                code = file_path.read_text()
                issues = security_scan(code, language)

                for issue in issues:
                    issue.message = f"[{file_path}] {issue.message}"
                    all_issues.append(issue)
            except Exception:
                continue

        if all_issues:
            console.print(Panel(
                f"[red]⚠️ {len(all_issues)} güvenlik sorunu bulundu![/red]",
                title="🔒 Güvenlik Taraması"
            ))

            table = Table()
            table.add_column("Dosya/Satır")
            table.add_column("Sorun")

            for issue in all_issues:
                table.add_row(
                    f"Satır {issue.line or '?'}",
                    issue.message
                )

            console.print(table)
        else:
            console.print(Panel(
                "[green]✅ Güvenlik sorunu bulunamadı.[/green]",
                title="🔒 Güvenlik Taraması"
            ))

    elif args.command == "demo":
        # Demo
        demo_code = '''
def login(username, password):
    # Hardcoded credentials - güvenlik açığı!
    admin_password = "admin123"

    query = f"SELECT * FROM users WHERE name='{username}'"  # SQL injection!
    result = eval(user_input)  # Tehlikeli eval!

    if password == admin_password:
        return True
    return False
'''

        console.print("[bold]Demo: Güvenlik Açıklı Kod İnceleme[/bold]")

        result = review_code(demo_code, "python", "security")

        # Manuel güvenlik taraması
        security_issues = security_scan(demo_code, "python")
        result.issues.extend(security_issues)

        display_result(result, demo_code)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
