"""
MiniMax-M2 Log Analizci Şablonu
===============================
AI destekli log analizi ve anomali tespiti.

Özellikler:
- Log parsing (çoklu format)
- Anomali tespiti
- Hata kümeleme
- Root cause analizi
- Trend analizi

Gereksinimler:
    pip install openai pandas rich

Kullanım:
    python main.py analyze app.log
    python main.py errors app.log --top 10
    python main.py trends app.log --hours 24
"""

import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
from collections import Counter

import pandas as pd
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress

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
class LogEntry:
    """Log girişi."""
    timestamp: Optional[datetime]
    level: str
    message: str
    source: Optional[str] = None
    raw: str = ""
    line_number: int = 0


@dataclass
class LogPattern:
    """Log deseni."""
    pattern: str
    count: int
    level: str
    samples: list[str] = field(default_factory=list)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


@dataclass
class Anomaly:
    """Anomali."""
    type: str  # spike, drop, new_error, pattern_change
    severity: str  # critical, warning, info
    description: str
    evidence: list[str] = field(default_factory=list)
    timestamp: Optional[datetime] = None


# ============================================================================
# Log Parsing
# ============================================================================

# Yaygın log formatları
LOG_PATTERNS = {
    "apache": r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] "(?P<request>[^"]*)" (?P<status>\d+) (?P<size>\S+)',
    "nginx": r'(?P<ip>\S+) - \S+ \[(?P<timestamp>[^\]]+)\] "(?P<request>[^"]*)" (?P<status>\d+) (?P<size>\d+)',
    "syslog": r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+) (?P<host>\S+) (?P<process>\S+): (?P<message>.*)',
    "python": r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),?\d* - (?P<name>\S+) - (?P<level>\w+) - (?P<message>.*)',
    "java": r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s+(?P<level>\w+)\s+(?P<thread>\S+)\s+(?P<class>\S+)\s*:\s*(?P<message>.*)',
    "json": r'\{.*"timestamp".*"level".*"message".*\}',
    "generic": r'(?P<timestamp>\d{4}[-/]\d{2}[-/]\d{2}[T ]\d{2}:\d{2}:\d{2}).*?(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL).*?(?P<message>.*)',
}

TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%SZ",
    "%d/%b/%Y:%H:%M:%S",
    "%b %d %H:%M:%S",
]


def detect_format(lines: list[str]) -> str:
    """Log formatını tespit et."""
    for name, pattern in LOG_PATTERNS.items():
        matches = sum(1 for line in lines[:100] if re.match(pattern, line))
        if matches > 50:
            return name
    return "generic"


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Timestamp parse et."""
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(ts_str.strip(), fmt)
        except ValueError:
            continue
    return None


def parse_log_line(line: str, line_number: int, format_name: str = "generic") -> Optional[LogEntry]:
    """Log satırını parse et."""
    pattern = LOG_PATTERNS.get(format_name, LOG_PATTERNS["generic"])

    match = re.match(pattern, line, re.IGNORECASE)
    if not match:
        # Fallback: level tespiti
        level = "INFO"
        for lvl in ["ERROR", "WARN", "WARNING", "CRITICAL", "FATAL", "DEBUG"]:
            if lvl in line.upper():
                level = lvl
                break

        return LogEntry(
            timestamp=None,
            level=level,
            message=line,
            raw=line,
            line_number=line_number
        )

    groups = match.groupdict()

    timestamp = None
    if "timestamp" in groups:
        timestamp = parse_timestamp(groups["timestamp"])

    level = groups.get("level", "INFO").upper()
    if level == "WARNING":
        level = "WARN"

    message = groups.get("message", line)
    source = groups.get("class") or groups.get("process") or groups.get("name")

    return LogEntry(
        timestamp=timestamp,
        level=level,
        message=message,
        source=source,
        raw=line,
        line_number=line_number
    )


def parse_log_file(file_path: str) -> list[LogEntry]:
    """Log dosyasını parse et."""
    path = Path(file_path)
    lines = path.read_text(errors="ignore").split("\n")

    format_name = detect_format(lines)
    console.print(f"[dim]Tespit edilen format: {format_name}[/dim]")

    entries = []
    for i, line in enumerate(lines, 1):
        if line.strip():
            entry = parse_log_line(line.strip(), i, format_name)
            if entry:
                entries.append(entry)

    return entries


# ============================================================================
# Analiz
# ============================================================================

def extract_patterns(entries: list[LogEntry], min_count: int = 2) -> list[LogPattern]:
    """Log desenlerini çıkar."""
    # Mesajları normalize et
    def normalize(msg: str) -> str:
        # Sayıları, ID'leri, IP'leri vb. maskele
        msg = re.sub(r'\b\d+\b', '<NUM>', msg)
        msg = re.sub(r'\b[0-9a-f]{8,}\b', '<HEX>', msg, flags=re.IGNORECASE)
        msg = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '<IP>', msg)
        msg = re.sub(r'\"[^\"]+\"', '"<STR>"', msg)
        msg = re.sub(r"'[^']+'", "'<STR>'", msg)
        return msg

    # Desenleri say
    pattern_entries: dict[str, list[LogEntry]] = {}
    for entry in entries:
        pattern = normalize(entry.message)
        if pattern not in pattern_entries:
            pattern_entries[pattern] = []
        pattern_entries[pattern].append(entry)

    # LogPattern oluştur
    patterns = []
    for pattern, group_entries in pattern_entries.items():
        if len(group_entries) >= min_count:
            timestamps = [e.timestamp for e in group_entries if e.timestamp]
            patterns.append(LogPattern(
                pattern=pattern,
                count=len(group_entries),
                level=group_entries[0].level,
                samples=[e.message for e in group_entries[:3]],
                first_seen=min(timestamps) if timestamps else None,
                last_seen=max(timestamps) if timestamps else None,
            ))

    return sorted(patterns, key=lambda p: p.count, reverse=True)


def detect_anomalies(entries: list[LogEntry]) -> list[Anomaly]:
    """Anomalileri tespit et."""
    anomalies = []

    # Hata spike tespiti
    error_entries = [e for e in entries if e.level in ["ERROR", "CRITICAL", "FATAL"]]
    if len(error_entries) > len(entries) * 0.1:  # >10% hata
        anomalies.append(Anomaly(
            type="spike",
            severity="critical",
            description=f"Yüksek hata oranı: {len(error_entries)}/{len(entries)} (%{len(error_entries)*100//len(entries)})",
            evidence=[e.message[:100] for e in error_entries[:5]]
        ))

    # Ardışık hatalar
    consecutive_errors = 0
    max_consecutive = 0
    for entry in entries:
        if entry.level in ["ERROR", "CRITICAL", "FATAL"]:
            consecutive_errors += 1
            max_consecutive = max(max_consecutive, consecutive_errors)
        else:
            consecutive_errors = 0

    if max_consecutive > 10:
        anomalies.append(Anomaly(
            type="spike",
            severity="warning",
            description=f"Ardışık hata serisi tespit edildi: {max_consecutive} hata"
        ))

    # Yeni hata tipleri (son %20'de ortaya çıkan)
    if len(entries) > 100:
        old_errors = set(e.message[:50] for e in entries[:-len(entries)//5] if e.level == "ERROR")
        new_errors = set(e.message[:50] for e in entries[-len(entries)//5:] if e.level == "ERROR")
        unique_new = new_errors - old_errors

        if len(unique_new) > 3:
            anomalies.append(Anomaly(
                type="new_error",
                severity="warning",
                description=f"Son dönemde {len(unique_new)} yeni hata türü tespit edildi",
                evidence=list(unique_new)[:5]
            ))

    return anomalies


def ai_analyze(entries: list[LogEntry], question: str = "genel analiz") -> str:
    """AI ile log analizi."""
    # Son 100 entry'yi özetle
    sample = entries[-100:] if len(entries) > 100 else entries

    log_summary = "\n".join([
        f"[{e.level}] {e.message[:200]}"
        for e in sample
    ])

    # İstatistikler
    level_counts = Counter(e.level for e in entries)

    prompt = f"""Bu log verilerini analiz et:

İstatistikler:
- Toplam: {len(entries)} log
- Seviyeler: {dict(level_counts)}

Son loglar (örnek):
{log_summary}

İstek: {question}

Analiz sonucunu şu formatta ver:
1. Özet
2. Tespit edilen sorunlar
3. Root cause tahminleri
4. Öneriler

Türkçe yanıt ver."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen uzman bir DevOps mühendisi ve log analiz uzmanısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def ai_root_cause(error_logs: list[LogEntry]) -> str:
    """Root cause analizi."""

    error_messages = "\n".join([
        f"[{e.timestamp or 'N/A'}] {e.message}"
        for e in error_logs[:50]
    ])

    prompt = f"""Bu hata loglarının root cause analizini yap:

{error_messages}

Analiz et:
1. Hatanın olası nedenleri (en muhtemelden en az muhtemele)
2. Hata zinciri (birbirini tetikleyen hatalar)
3. Düzeltme önerileri
4. Önleme stratejileri

Türkçe yanıt ver."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen uzman bir sistem analisti ve hata ayıklama uzmanısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    return response.choices[0].message.content


# ============================================================================
# Çıktı Formatlama
# ============================================================================

def display_summary(entries: list[LogEntry]):
    """Özet göster."""
    level_counts = Counter(e.level for e in entries)

    console.print()
    console.print(Panel("[bold]Log Özeti[/bold]", title="📊 Summary"))

    table = Table(show_header=True)
    table.add_column("Seviye")
    table.add_column("Sayı")
    table.add_column("Oran")

    colors = {
        "ERROR": "red",
        "CRITICAL": "red bold",
        "FATAL": "red bold",
        "WARN": "yellow",
        "WARNING": "yellow",
        "INFO": "blue",
        "DEBUG": "dim",
    }

    for level, count in level_counts.most_common():
        color = colors.get(level, "white")
        pct = count * 100 / len(entries)
        table.add_row(
            f"[{color}]{level}[/{color}]",
            str(count),
            f"%{pct:.1f}"
        )

    console.print(table)

    # Zaman aralığı
    timestamps = [e.timestamp for e in entries if e.timestamp]
    if timestamps:
        console.print(f"\n[dim]Zaman aralığı: {min(timestamps)} - {max(timestamps)}[/dim]")


def display_patterns(patterns: list[LogPattern], limit: int = 10):
    """Desenleri göster."""
    console.print()
    console.print(Panel(f"[bold]En Sık {limit} Log Deseni[/bold]", title="🔄 Patterns"))

    for i, p in enumerate(patterns[:limit], 1):
        console.print(f"\n[bold]{i}. [{p.level}] x{p.count}[/bold]")
        console.print(f"[dim]{p.pattern[:100]}...[/dim]" if len(p.pattern) > 100 else f"[dim]{p.pattern}[/dim]")
        if p.samples:
            console.print(f"   Örnek: {p.samples[0][:80]}...")


def display_errors(entries: list[LogEntry], limit: int = 10):
    """Hataları göster."""
    errors = [e for e in entries if e.level in ["ERROR", "CRITICAL", "FATAL"]]

    console.print()
    console.print(Panel(f"[bold]{len(errors)} Hata Bulundu[/bold]", title="❌ Errors"))

    # Hata grupları
    error_groups = Counter(e.message[:100] for e in errors)

    table = Table(show_header=True)
    table.add_column("#")
    table.add_column("Sayı")
    table.add_column("Hata")

    for i, (msg, count) in enumerate(error_groups.most_common(limit), 1):
        table.add_row(str(i), str(count), msg[:80] + ("..." if len(msg) > 80 else ""))

    console.print(table)


def display_anomalies(anomalies: list[Anomaly]):
    """Anomalileri göster."""
    if not anomalies:
        console.print("\n[green]✅ Anomali tespit edilmedi.[/green]")
        return

    console.print()
    console.print(Panel(f"[bold]{len(anomalies)} Anomali Tespit Edildi[/bold]", title="⚠️ Anomalies"))

    for a in anomalies:
        severity_colors = {"critical": "red", "warning": "yellow", "info": "blue"}
        color = severity_colors.get(a.severity, "white")

        console.print(f"\n[{color}]• [{a.severity.upper()}] {a.type}[/{color}]")
        console.print(f"  {a.description}")

        if a.evidence:
            console.print("  [dim]Kanıtlar:[/dim]")
            for ev in a.evidence[:3]:
                console.print(f"    - {ev[:60]}...")


# ============================================================================
# CLI
# ============================================================================

def main():
    """Ana fonksiyon."""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax-M2 Log Analizci")
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # analyze komutu
    analyze_parser = subparsers.add_parser("analyze", help="Genel analiz")
    analyze_parser.add_argument("file", help="Log dosyası")
    analyze_parser.add_argument("--question", "-q", default="genel analiz", help="Analiz sorusu")

    # errors komutu
    errors_parser = subparsers.add_parser("errors", help="Hata analizi")
    errors_parser.add_argument("file", help="Log dosyası")
    errors_parser.add_argument("--top", "-t", type=int, default=10, help="Gösterilecek hata sayısı")
    errors_parser.add_argument("--root-cause", "-r", action="store_true", help="Root cause analizi")

    # patterns komutu
    patterns_parser = subparsers.add_parser("patterns", help="Desen analizi")
    patterns_parser.add_argument("file", help="Log dosyası")
    patterns_parser.add_argument("--top", "-t", type=int, default=10, help="Gösterilecek desen sayısı")

    # anomalies komutu
    anomalies_parser = subparsers.add_parser("anomalies", help="Anomali tespiti")
    anomalies_parser.add_argument("file", help="Log dosyası")

    # demo komutu
    subparsers.add_parser("demo", help="Demo")

    args = parser.parse_args()

    if args.command == "analyze":
        console.print(f"[dim]Dosya okunuyor: {args.file}[/dim]")
        entries = parse_log_file(args.file)

        display_summary(entries)

        console.print("\n[dim]AI analizi yapılıyor...[/dim]")
        analysis = ai_analyze(entries, args.question)
        console.print(Panel(analysis, title="🤖 AI Analizi"))

    elif args.command == "errors":
        entries = parse_log_file(args.file)
        display_summary(entries)
        display_errors(entries, args.top)

        if args.root_cause:
            error_entries = [e for e in entries if e.level in ["ERROR", "CRITICAL", "FATAL"]]
            if error_entries:
                console.print("\n[dim]Root cause analizi yapılıyor...[/dim]")
                analysis = ai_root_cause(error_entries)
                console.print(Panel(analysis, title="🔍 Root Cause Analizi"))

    elif args.command == "patterns":
        entries = parse_log_file(args.file)
        patterns = extract_patterns(entries)
        display_summary(entries)
        display_patterns(patterns, args.top)

    elif args.command == "anomalies":
        entries = parse_log_file(args.file)
        anomalies = detect_anomalies(entries)
        display_summary(entries)
        display_anomalies(anomalies)

    elif args.command == "demo":
        console.print(Panel("[bold]MiniMax-M2 Log Analizci Demo[/bold]"))

        # Demo log oluştur
        demo_logs = """
2024-01-15 10:00:01 - app - INFO - Application started
2024-01-15 10:00:02 - app - INFO - Connected to database
2024-01-15 10:00:05 - api - INFO - Request received: GET /users
2024-01-15 10:00:06 - api - INFO - Request completed: 200 OK
2024-01-15 10:00:10 - api - ERROR - Database connection timeout after 30s
2024-01-15 10:00:11 - api - ERROR - Failed to fetch user data: Connection refused
2024-01-15 10:00:12 - api - ERROR - Retry attempt 1 failed
2024-01-15 10:00:13 - api - ERROR - Retry attempt 2 failed
2024-01-15 10:00:14 - api - CRITICAL - Service unavailable, circuit breaker opened
2024-01-15 10:00:15 - app - WARN - High memory usage detected: 85%
2024-01-15 10:00:20 - api - INFO - Circuit breaker half-open, testing
2024-01-15 10:00:21 - api - INFO - Database connection restored
2024-01-15 10:00:22 - api - INFO - Circuit breaker closed
""".strip()

        # Geçici dosya
        demo_path = Path("/tmp/demo.log")
        demo_path.write_text(demo_logs)

        entries = parse_log_file(str(demo_path))

        display_summary(entries)
        display_errors(entries, 5)

        anomalies = detect_anomalies(entries)
        display_anomalies(anomalies)

        console.print("\n[dim]AI analizi yapılıyor...[/dim]")
        analysis = ai_analyze(entries, "Bu log verilerinde ne olmuş?")
        console.print(Panel(analysis, title="🤖 AI Analizi"))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
