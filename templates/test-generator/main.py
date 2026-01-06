"""
MiniMax-M2 Test Üretici Şablonu
===============================
AI destekli otomatik test üretimi.

Özellikler:
- Fonksiyon/sınıf analizi
- Unit test üretimi
- Edge case tespiti
- Mock/stub önerileri
- Çoklu framework desteği

Gereksinimler:
    pip install openai rich

Kullanım:
    python main.py generate file.py
    python main.py generate file.py --function my_func
    python main.py coverage file.py
"""

import os
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
class FunctionInfo:
    """Fonksiyon bilgisi."""
    name: str
    args: list[str]
    defaults: list[str]
    returns: Optional[str]
    docstring: Optional[str]
    body: str
    decorators: list[str] = field(default_factory=list)
    is_async: bool = False
    is_method: bool = False
    class_name: Optional[str] = None


@dataclass
class ClassInfo:
    """Sınıf bilgisi."""
    name: str
    bases: list[str]
    methods: list[FunctionInfo]
    docstring: Optional[str]


@dataclass
class TestCase:
    """Test case."""
    name: str
    description: str
    test_code: str
    category: str  # unit, edge, error, integration


# ============================================================================
# Kod Analizi
# ============================================================================

class CodeAnalyzer(ast.NodeVisitor):
    """Python kod analizi."""

    def __init__(self):
        self.functions: list[FunctionInfo] = []
        self.classes: list[ClassInfo] = []
        self.imports: list[str] = []
        self._current_class: Optional[str] = None
        self._source_lines: list[str] = []

    def analyze(self, code: str) -> dict:
        """Kodu analiz et."""
        self._source_lines = code.split("\n")
        tree = ast.parse(code)
        self.visit(tree)

        return {
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
        }

    def _get_source(self, node) -> str:
        """Node kaynak kodunu al."""
        try:
            return ast.get_source_segment("\n".join(self._source_lines), node) or ""
        except Exception:
            return ""

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module or ""
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self._process_function(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._process_function(node, is_async=True)
        self.generic_visit(node)

    def _process_function(self, node, is_async: bool):
        """Fonksiyon bilgisini çıkar."""
        # Argümanlar
        args = []
        defaults = []

        for arg in node.args.args:
            args.append(arg.arg)

        for default in node.args.defaults:
            if isinstance(default, ast.Constant):
                defaults.append(repr(default.value))
            else:
                defaults.append("...")

        # Return tipi
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)

        # Decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    decorators.append(dec.func.id)

        func_info = FunctionInfo(
            name=node.name,
            args=args,
            defaults=defaults,
            returns=returns,
            docstring=ast.get_docstring(node),
            body=self._get_source(node),
            decorators=decorators,
            is_async=is_async,
            is_method=self._current_class is not None,
            class_name=self._current_class,
        )

        self.functions.append(func_info)

    def visit_ClassDef(self, node):
        """Sınıf bilgisini çıkar."""
        old_class = self._current_class
        self._current_class = node.name

        # Temel sınıflar
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)

        # Sınıfı kaydet
        class_info = ClassInfo(
            name=node.name,
            bases=bases,
            methods=[],
            docstring=ast.get_docstring(node),
        )

        # Alt node'ları ziyaret et
        self.generic_visit(node)

        # Metodları ekle
        class_info.methods = [
            f for f in self.functions
            if f.class_name == node.name
        ]

        self.classes.append(class_info)
        self._current_class = old_class


# ============================================================================
# Test Üretimi
# ============================================================================

def generate_tests(
    func: FunctionInfo,
    framework: str = "pytest",
    style: str = "comprehensive"
) -> list[TestCase]:
    """Fonksiyon için test üret."""

    prompt = f"""Bu Python fonksiyonu için {framework} testleri üret:

```python
{func.body}
```

Fonksiyon bilgileri:
- İsim: {func.name}
- Argümanlar: {func.args}
- Varsayılanlar: {func.defaults}
- Return tipi: {func.returns}
- Async: {func.is_async}
- Docstring: {func.docstring or 'Yok'}

Test türleri:
1. Normal kullanım (happy path)
2. Edge cases (sınır değerler, boş değerler)
3. Hata durumları (exceptions)
4. Tip kontrolleri

Her test için JSON formatında döndür:
[
    {{
        "name": "test_<fonksiyon>_<durum>",
        "description": "<test açıklaması>",
        "category": "unit|edge|error|integration",
        "code": "<test kodu>"
    }}
]

Kurallar:
- {framework} syntax kullan
- Assert mesajları ekle
- Mock gerekiyorsa belirt
- Türkçe açıklama, İngilizce kod"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen uzman bir test mühendisisin."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4000,
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

        data = json.loads(json_str)

        return [
            TestCase(
                name=t.get("name", f"test_{func.name}"),
                description=t.get("description", ""),
                test_code=t.get("code", ""),
                category=t.get("category", "unit")
            )
            for t in data
        ]
    except Exception as e:
        return [TestCase(
            name=f"test_{func.name}",
            description=f"Üretim hatası: {e}",
            test_code="# Test üretilemedi",
            category="unit"
        )]


def generate_test_file(
    functions: list[FunctionInfo],
    source_file: str,
    framework: str = "pytest"
) -> str:
    """Tam test dosyası üret."""

    func_bodies = "\n\n".join(f.body for f in functions)
    func_names = [f.name for f in functions]

    prompt = f"""Bu Python dosyası için kapsamlı {framework} test dosyası üret:

Kaynak dosya: {source_file}

```python
{func_bodies}
```

Test edilecek fonksiyonlar: {func_names}

Gereksinimler:
1. Gerekli import'lar
2. Fixture'lar (gerekirse)
3. Her fonksiyon için en az 3 test
4. Parametrize kullanımı (uygunsa)
5. Mock kullanımı (gerekirse)
6. Setup/teardown (gerekirse)

Sadece çalışır Python test kodu döndür."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen uzman bir test mühendisisin."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=6000,
    )

    content = response.choices[0].message.content

    if "```python" in content:
        code = content.split("```python")[1].split("```")[0]
    elif "```" in content:
        code = content.split("```")[1].split("```")[0]
    else:
        code = content

    return code.strip()


def analyze_coverage(code: str, tests: str) -> dict:
    """Test kapsamını analiz et."""

    prompt = f"""Bu kod ve testlerin kapsamını analiz et:

KAYNAK KOD:
```python
{code}
```

TESTLER:
```python
{tests}
```

JSON formatında döndür:
{{
    "covered_functions": ["<fonksiyon1>", "<fonksiyon2>"],
    "uncovered_functions": ["<fonksiyon3>"],
    "covered_branches": <sayı>,
    "total_branches": <sayı>,
    "estimated_coverage": "<yüzde>",
    "missing_tests": [
        {{
            "function": "<fonksiyon>",
            "missing": "<eksik test türü>"
        }}
    ],
    "suggestions": ["<öneri1>", "<öneri2>"]
}}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen test kapsam analiz uzmanısın."},
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
        return {"error": "Analiz yapılamadı"}


# ============================================================================
# Çıktı Formatlama
# ============================================================================

def display_tests(tests: list[TestCase], func_name: str):
    """Testleri göster."""
    console.print()
    console.print(Panel(f"[bold]Fonksiyon: {func_name}[/bold]", title="🧪 Test Üretimi"))

    categories = {"unit": "🔵", "edge": "🟡", "error": "🔴", "integration": "🟢"}

    for i, test in enumerate(tests, 1):
        icon = categories.get(test.category, "⚪")
        console.print(f"\n{icon} [bold]Test {i}: {test.name}[/bold]")
        console.print(f"[dim]{test.description}[/dim]")

        syntax = Syntax(test.test_code, "python", theme="monokai", line_numbers=True)
        console.print(syntax)


def display_coverage(analysis: dict):
    """Kapsam analizini göster."""
    console.print()
    console.print(Panel("[bold]Test Kapsam Analizi[/bold]", title="📊 Coverage"))

    # Kapsam yüzdesi
    coverage = analysis.get("estimated_coverage", "?")
    console.print(f"\n[bold]Tahmini Kapsam: {coverage}[/bold]")

    # Tablo
    table = Table(show_header=True)
    table.add_column("Metrik")
    table.add_column("Değer")

    table.add_row("Kaplanan Fonksiyonlar", str(len(analysis.get("covered_functions", []))))
    table.add_row("Kapanmayan Fonksiyonlar", str(len(analysis.get("uncovered_functions", []))))
    table.add_row("Branch Kapsamı", f"{analysis.get('covered_branches', '?')}/{analysis.get('total_branches', '?')}")

    console.print(table)

    # Eksik testler
    missing = analysis.get("missing_tests", [])
    if missing:
        console.print("\n[yellow]Eksik Testler:[/yellow]")
        for m in missing:
            console.print(f"  • {m.get('function', '?')}: {m.get('missing', '?')}")

    # Öneriler
    suggestions = analysis.get("suggestions", [])
    if suggestions:
        console.print("\n[green]Öneriler:[/green]")
        for s in suggestions:
            console.print(f"  • {s}")


# ============================================================================
# CLI
# ============================================================================

def main():
    """Ana fonksiyon."""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax-M2 Test Üretici")
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # generate komutu
    gen_parser = subparsers.add_parser("generate", help="Test üret")
    gen_parser.add_argument("file", help="Kaynak dosya")
    gen_parser.add_argument("--function", "-f", help="Belirli fonksiyon")
    gen_parser.add_argument("--framework", default="pytest", choices=["pytest", "unittest"])
    gen_parser.add_argument("--output", "-o", help="Çıktı dosyası")

    # coverage komutu
    cov_parser = subparsers.add_parser("coverage", help="Kapsam analizi")
    cov_parser.add_argument("source", help="Kaynak dosya")
    cov_parser.add_argument("tests", nargs="?", help="Test dosyası")

    # demo komutu
    subparsers.add_parser("demo", help="Demo")

    args = parser.parse_args()

    if args.command == "generate":
        file_path = Path(args.file)
        if not file_path.exists():
            console.print(f"[red]Dosya bulunamadı: {file_path}[/red]")
            return

        code = file_path.read_text()
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze(code)

        functions = analysis["functions"]

        # Belirli fonksiyon
        if args.function:
            functions = [f for f in functions if f.name == args.function]
            if not functions:
                console.print(f"[red]Fonksiyon bulunamadı: {args.function}[/red]")
                return

        # Public fonksiyonlar
        functions = [f for f in functions if not f.name.startswith("_")]

        if not functions:
            console.print("[yellow]Test edilecek fonksiyon bulunamadı.[/yellow]")
            return

        console.print(f"[dim]{len(functions)} fonksiyon bulundu.[/dim]")

        if args.output:
            # Tam test dosyası
            test_code = generate_test_file(functions, str(file_path), args.framework)

            output_path = Path(args.output)
            output_path.write_text(test_code)

            console.print(f"\n[green]✅ Test dosyası oluşturuldu: {output_path}[/green]")

            syntax = Syntax(test_code, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="📝 Üretilen Testler"))
        else:
            # Her fonksiyon için test
            for func in functions:
                tests = generate_tests(func, args.framework)
                display_tests(tests, func.name)

    elif args.command == "coverage":
        source_path = Path(args.source)
        if not source_path.exists():
            console.print(f"[red]Dosya bulunamadı: {source_path}[/red]")
            return

        source_code = source_path.read_text()

        if args.tests:
            test_path = Path(args.tests)
            test_code = test_path.read_text() if test_path.exists() else ""
        else:
            # Test dosyasını otomatik bul
            test_candidates = [
                source_path.parent / f"test_{source_path.name}",
                source_path.parent / "tests" / f"test_{source_path.name}",
            ]
            test_code = ""
            for candidate in test_candidates:
                if candidate.exists():
                    test_code = candidate.read_text()
                    console.print(f"[dim]Test dosyası bulundu: {candidate}[/dim]")
                    break

        if not test_code:
            console.print("[yellow]Test dosyası bulunamadı. Öneri üretiliyor...[/yellow]")

        analysis = analyze_coverage(source_code, test_code)
        display_coverage(analysis)

    elif args.command == "demo":
        console.print(Panel("[bold]MiniMax-M2 Test Üretici Demo[/bold]"))

        demo_code = '''
def calculate_discount(price: float, discount_percent: float) -> float:
    """Fiyata indirim uygula."""
    if price < 0:
        raise ValueError("Fiyat negatif olamaz")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("İndirim 0-100 arasında olmalı")

    discount = price * (discount_percent / 100)
    return round(price - discount, 2)


def is_valid_email(email: str) -> bool:
    """Email formatını kontrol et."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
'''

        console.print("\n[bold]Kaynak Kod:[/bold]")
        syntax = Syntax(demo_code, "python", theme="monokai", line_numbers=True)
        console.print(syntax)

        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze(demo_code)

        for func in analysis["functions"]:
            console.print(f"\n[dim]'{func.name}' için test üretiliyor...[/dim]")
            tests = generate_tests(func, "pytest")
            display_tests(tests, func.name)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
