"""
MiniMax-M2 SQL Asistan Şablonu
==============================
AI destekli SQL sorgu üretici ve analiz aracı.

Özellikler:
- Doğal dil → SQL dönüşümü
- SQL açıklama ve analiz
- Sorgu optimizasyonu
- Şema analizi
- Çoklu veritabanı desteği

Gereksinimler:
    pip install openai sqlparse rich

Kullanım:
    python main.py query "son 30 gündeki siparişleri getir"
    python main.py explain "SELECT * FROM users WHERE age > 18"
    python main.py optimize "SELECT * FROM orders WHERE date > '2024-01-01'"
"""

import os
import re
from typing import Optional
from dataclasses import dataclass, field

import sqlparse
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
class TableSchema:
    """Tablo şeması."""
    name: str
    columns: list[dict]
    primary_key: Optional[str] = None
    foreign_keys: list[dict] = field(default_factory=list)


@dataclass
class DatabaseSchema:
    """Veritabanı şeması."""
    dialect: str  # postgresql, mysql, sqlite
    tables: list[TableSchema] = field(default_factory=list)

    def to_prompt(self) -> str:
        """Şemayı prompt formatına çevir."""
        lines = [f"Veritabanı: {self.dialect}\n"]
        for table in self.tables:
            lines.append(f"Tablo: {table.name}")
            for col in table.columns:
                pk = " (PK)" if col.get("name") == table.primary_key else ""
                lines.append(f"  - {col['name']}: {col['type']}{pk}")
            if table.foreign_keys:
                for fk in table.foreign_keys:
                    lines.append(f"  FK: {fk['column']} -> {fk['references']}")
            lines.append("")
        return "\n".join(lines)


# ============================================================================
# Örnek Şemalar
# ============================================================================

SAMPLE_SCHEMAS = {
    "ecommerce": DatabaseSchema(
        dialect="postgresql",
        tables=[
            TableSchema(
                name="users",
                columns=[
                    {"name": "id", "type": "SERIAL"},
                    {"name": "name", "type": "VARCHAR(100)"},
                    {"name": "email", "type": "VARCHAR(255)"},
                    {"name": "created_at", "type": "TIMESTAMP"},
                ],
                primary_key="id"
            ),
            TableSchema(
                name="products",
                columns=[
                    {"name": "id", "type": "SERIAL"},
                    {"name": "name", "type": "VARCHAR(200)"},
                    {"name": "price", "type": "DECIMAL(10,2)"},
                    {"name": "category_id", "type": "INTEGER"},
                    {"name": "stock", "type": "INTEGER"},
                ],
                primary_key="id",
                foreign_keys=[{"column": "category_id", "references": "categories(id)"}]
            ),
            TableSchema(
                name="orders",
                columns=[
                    {"name": "id", "type": "SERIAL"},
                    {"name": "user_id", "type": "INTEGER"},
                    {"name": "total", "type": "DECIMAL(10,2)"},
                    {"name": "status", "type": "VARCHAR(20)"},
                    {"name": "created_at", "type": "TIMESTAMP"},
                ],
                primary_key="id",
                foreign_keys=[{"column": "user_id", "references": "users(id)"}]
            ),
            TableSchema(
                name="order_items",
                columns=[
                    {"name": "id", "type": "SERIAL"},
                    {"name": "order_id", "type": "INTEGER"},
                    {"name": "product_id", "type": "INTEGER"},
                    {"name": "quantity", "type": "INTEGER"},
                    {"name": "price", "type": "DECIMAL(10,2)"},
                ],
                primary_key="id",
                foreign_keys=[
                    {"column": "order_id", "references": "orders(id)"},
                    {"column": "product_id", "references": "products(id)"}
                ]
            ),
            TableSchema(
                name="categories",
                columns=[
                    {"name": "id", "type": "SERIAL"},
                    {"name": "name", "type": "VARCHAR(100)"},
                    {"name": "parent_id", "type": "INTEGER"},
                ],
                primary_key="id"
            ),
        ]
    ),
}


# ============================================================================
# SQL İşlemleri
# ============================================================================

def format_sql(sql: str) -> str:
    """SQL'i formatla."""
    return sqlparse.format(
        sql,
        reindent=True,
        keyword_case="upper",
        indent_width=4
    )


def validate_sql(sql: str) -> tuple[bool, Optional[str]]:
    """SQL syntax kontrolü."""
    try:
        parsed = sqlparse.parse(sql)
        if not parsed or not parsed[0].tokens:
            return False, "Geçersiz SQL"
        return True, None
    except Exception as e:
        return False, str(e)


def extract_tables(sql: str) -> list[str]:
    """SQL'den tablo adlarını çıkar."""
    tables = set()

    # FROM ve JOIN sonrası tablo adları
    patterns = [
        r'\bFROM\s+(\w+)',
        r'\bJOIN\s+(\w+)',
        r'\bINTO\s+(\w+)',
        r'\bUPDATE\s+(\w+)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, sql, re.IGNORECASE)
        tables.update(matches)

    return list(tables)


# ============================================================================
# AI Fonksiyonları
# ============================================================================

def natural_to_sql(query: str, schema: DatabaseSchema) -> str:
    """Doğal dili SQL'e çevir."""

    prompt = f"""Aşağıdaki veritabanı şemasını kullanarak, verilen doğal dil sorgusunu SQL'e çevir.

{schema.to_prompt()}

SORGU: {query}

Kurallar:
1. Sadece geçerli SQL döndür
2. Şemadaki tablo ve sütun adlarını kullan
3. {schema.dialect} syntax kullan
4. Açıklama yazma, sadece SQL

SQL:"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen uzman bir SQL geliştiricisisin."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=1000,
    )

    sql = response.choices[0].message.content.strip()

    # SQL bloğunu temizle
    if "```sql" in sql:
        sql = sql.split("```sql")[1].split("```")[0]
    elif "```" in sql:
        sql = sql.split("```")[1].split("```")[0]

    return format_sql(sql.strip())


def explain_sql(sql: str) -> str:
    """SQL sorgusunu açıkla."""

    prompt = f"""Bu SQL sorgusunu ayrıntılı açıkla:

```sql
{sql}
```

Şunları dahil et:
1. Sorgunun amacı
2. Kullanılan tablolar
3. JOIN'ler ve ilişkiler
4. WHERE koşulları
5. Sıralama ve gruplama
6. Potansiyel performans etkileri

Türkçe ve markdown formatında yanıt ver."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen uzman bir veritabanı öğretmenisin."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def optimize_sql(sql: str, schema: Optional[DatabaseSchema] = None) -> dict:
    """SQL sorgusunu optimize et."""

    schema_info = schema.to_prompt() if schema else "Şema bilgisi yok."

    prompt = f"""Bu SQL sorgusunu analiz et ve optimize et:

```sql
{sql}
```

Şema:
{schema_info}

JSON formatında yanıt ver:
{{
    "original_query": "<orijinal sorgu>",
    "optimized_query": "<optimize edilmiş sorgu>",
    "improvements": ["<iyileştirme 1>", "<iyileştirme 2>"],
    "index_suggestions": ["<index önerisi 1>"],
    "explanation": "<açıklama>",
    "estimated_improvement": "<tahmini performans artışı>"
}}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen veritabanı optimizasyon uzmanısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=2000,
    )

    try:
        import json
        content = response.choices[0].message.content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0]
        else:
            json_str = content
        return json.loads(json_str)
    except Exception:
        return {
            "original_query": sql,
            "optimized_query": sql,
            "improvements": [],
            "explanation": response.choices[0].message.content
        }


def generate_schema(description: str, dialect: str = "postgresql") -> str:
    """Açıklamadan şema oluştur."""

    prompt = f"""Aşağıdaki açıklamaya göre {dialect} veritabanı şeması oluştur:

{description}

Kurallar:
1. CREATE TABLE ifadeleri kullan
2. Uygun veri tipleri seç
3. Primary ve foreign key tanımla
4. Index önerileri ekle
5. Yorum satırları ekle

Sadece SQL döndür."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen veritabanı tasarım uzmanısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=3000,
    )

    sql = response.choices[0].message.content
    if "```sql" in sql:
        sql = sql.split("```sql")[1].split("```")[0]
    elif "```" in sql:
        sql = sql.split("```")[1].split("```")[0]

    return sql.strip()


# ============================================================================
# Çıktı Formatlama
# ============================================================================

def display_sql(sql: str, title: str = "SQL"):
    """SQL'i göster."""
    console.print()
    syntax = Syntax(sql, "sql", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"💾 {title}"))


def display_optimization(result: dict):
    """Optimizasyon sonucunu göster."""
    console.print()

    # Orijinal sorgu
    console.print("[bold]Orijinal Sorgu:[/bold]")
    syntax = Syntax(result.get("original_query", ""), "sql", theme="monokai")
    console.print(syntax)

    # Optimize edilmiş sorgu
    if result.get("optimized_query") and result["optimized_query"] != result.get("original_query"):
        console.print("\n[bold]Optimize Edilmiş Sorgu:[/bold]")
        syntax = Syntax(result["optimized_query"], "sql", theme="monokai")
        console.print(syntax)

    # İyileştirmeler
    improvements = result.get("improvements", [])
    if improvements:
        console.print("\n[bold]İyileştirmeler:[/bold]")
        for i, imp in enumerate(improvements, 1):
            console.print(f"  {i}. {imp}")

    # Index önerileri
    indexes = result.get("index_suggestions", [])
    if indexes:
        console.print("\n[bold]Index Önerileri:[/bold]")
        for idx in indexes:
            console.print(f"  • {idx}")

    # Açıklama
    if result.get("explanation"):
        console.print("\n[bold]Açıklama:[/bold]")
        console.print(Panel(result["explanation"]))

    # Tahmini iyileşme
    if result.get("estimated_improvement"):
        console.print(f"\n[green]📈 Tahmini İyileşme: {result['estimated_improvement']}[/green]")


# ============================================================================
# CLI
# ============================================================================

def main():
    """Ana fonksiyon."""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax-M2 SQL Asistan")
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # query komutu
    query_parser = subparsers.add_parser("query", help="Doğal dil → SQL")
    query_parser.add_argument("text", help="Doğal dil sorgusu")
    query_parser.add_argument("--schema", "-s", default="ecommerce", help="Şema adı")

    # explain komutu
    explain_parser = subparsers.add_parser("explain", help="SQL açıkla")
    explain_parser.add_argument("sql", help="SQL sorgusu")

    # optimize komutu
    optimize_parser = subparsers.add_parser("optimize", help="SQL optimize et")
    optimize_parser.add_argument("sql", help="SQL sorgusu")
    optimize_parser.add_argument("--schema", "-s", default="ecommerce", help="Şema adı")

    # schema komutu
    schema_parser = subparsers.add_parser("schema", help="Şema oluştur")
    schema_parser.add_argument("description", help="Şema açıklaması")
    schema_parser.add_argument("--dialect", "-d", default="postgresql", help="SQL dialekti")

    # format komutu
    format_parser = subparsers.add_parser("format", help="SQL formatla")
    format_parser.add_argument("sql", help="SQL sorgusu")

    # demo komutu
    subparsers.add_parser("demo", help="Demo")

    args = parser.parse_args()

    if args.command == "query":
        schema = SAMPLE_SCHEMAS.get(args.schema)
        if not schema:
            console.print(f"[yellow]Şema bulunamadı: {args.schema}, varsayılan kullanılıyor.[/yellow]")
            schema = SAMPLE_SCHEMAS["ecommerce"]

        console.print(f"[dim]Sorgu: {args.text}[/dim]")
        sql = natural_to_sql(args.text, schema)
        display_sql(sql, "Üretilen SQL")

    elif args.command == "explain":
        console.print("[dim]SQL açıklanıyor...[/dim]")
        explanation = explain_sql(args.sql)
        console.print()
        console.print(Panel(Markdown(explanation), title="📖 SQL Açıklaması"))

    elif args.command == "optimize":
        schema = SAMPLE_SCHEMAS.get(args.schema)
        console.print("[dim]SQL optimize ediliyor...[/dim]")
        result = optimize_sql(args.sql, schema)
        display_optimization(result)

    elif args.command == "schema":
        console.print("[dim]Şema oluşturuluyor...[/dim]")
        sql = generate_schema(args.description, args.dialect)
        display_sql(sql, "Veritabanı Şeması")

    elif args.command == "format":
        formatted = format_sql(args.sql)
        display_sql(formatted, "Formatlanmış SQL")

    elif args.command == "demo":
        console.print(Panel("[bold]MiniMax-M2 SQL Asistan Demo[/bold]"))

        schema = SAMPLE_SCHEMAS["ecommerce"]

        # Demo 1: Doğal dil sorgusu
        console.print("\n[bold]1. Doğal Dil → SQL[/bold]")
        query = "Son 30 gündeki siparişleri toplam tutarına göre sırala"
        console.print(f"[dim]Sorgu: {query}[/dim]")
        sql = natural_to_sql(query, schema)
        display_sql(sql)

        # Demo 2: SQL açıklama
        console.print("\n[bold]2. SQL Açıklama[/bold]")
        sample_sql = """
        SELECT u.name, COUNT(o.id) as order_count, SUM(o.total) as total_spent
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE o.created_at > NOW() - INTERVAL '30 days'
        GROUP BY u.id, u.name
        HAVING SUM(o.total) > 1000
        ORDER BY total_spent DESC
        LIMIT 10;
        """
        explanation = explain_sql(sample_sql)
        console.print(Panel(Markdown(explanation), title="📖 Açıklama"))

        # Demo 3: Optimizasyon
        console.print("\n[bold]3. SQL Optimizasyon[/bold]")
        slow_sql = "SELECT * FROM orders WHERE DATE(created_at) = '2024-01-15'"
        result = optimize_sql(slow_sql, schema)
        display_optimization(result)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
