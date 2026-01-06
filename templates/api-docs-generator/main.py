"""
MiniMax-M2 API Dokümantasyon Üretici Şablonu
=============================================
AI destekli API dokümantasyon üretimi.

Özellikler:
- Kod analizi ile otomatik dokümantasyon
- OpenAPI/Swagger üretimi
- Markdown dokümantasyon
- Örnek kod üretimi
- Çoklu dil desteği

Gereksinimler:
    pip install openai pyyaml rich

Kullanım:
    python main.py generate app.py --format openapi
    python main.py generate app.py --format markdown
    python main.py examples app.py
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field

import yaml
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
class Parameter:
    """API parametresi."""
    name: str
    type: str
    required: bool = True
    description: str = ""
    default: Optional[Any] = None
    location: str = "query"  # query, path, body, header


@dataclass
class Endpoint:
    """API endpoint."""
    path: str
    method: str
    summary: str = ""
    description: str = ""
    parameters: list[Parameter] = field(default_factory=list)
    request_body: Optional[dict] = None
    responses: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class APIDoc:
    """API dokümantasyonu."""
    title: str
    version: str = "1.0.0"
    description: str = ""
    base_url: str = "/"
    endpoints: list[Endpoint] = field(default_factory=list)


# ============================================================================
# Kod Analizi
# ============================================================================

def extract_fastapi_endpoints(code: str) -> list[Endpoint]:
    """FastAPI endpoint'lerini çıkar."""
    endpoints = []

    # Decorator pattern
    patterns = [
        (r'@(?:app|router)\.(\w+)\(["\']([^"\']+)["\']', "fastapi"),
        (r'@route\(["\']([^"\']+)["\'].*methods=\[(.*?)\]', "flask"),
    ]

    lines = code.split("\n")

    for i, line in enumerate(lines):
        # FastAPI/Flask decorator
        for pattern, framework in patterns:
            match = re.search(pattern, line)
            if match:
                if framework == "fastapi":
                    method = match.group(1).upper()
                    path = match.group(2)
                elif framework == "flask":
                    path = match.group(1)
                    methods = match.group(2)
                    method = methods.split(",")[0].strip().strip("'\"").upper()

                # Fonksiyon bilgisini al
                func_info = extract_function_after(lines, i)

                endpoints.append(Endpoint(
                    path=path,
                    method=method,
                    summary=func_info.get("name", ""),
                    description=func_info.get("docstring", ""),
                    parameters=func_info.get("parameters", []),
                ))

    return endpoints


def extract_function_after(lines: list[str], start: int) -> dict:
    """Decorator sonrasındaki fonksiyonu çıkar."""
    result = {"name": "", "docstring": "", "parameters": []}

    for i in range(start + 1, min(start + 10, len(lines))):
        line = lines[i].strip()

        # Fonksiyon tanımı
        func_match = re.match(r'(?:async\s+)?def\s+(\w+)\((.*?)\)', line)
        if func_match:
            result["name"] = func_match.group(1)
            args_str = func_match.group(2)

            # Argümanları parse et
            for arg in args_str.split(","):
                arg = arg.strip()
                if arg and arg not in ["self", "request", "db"]:
                    # Tip anotasyonu
                    if ":" in arg:
                        name, type_hint = arg.split(":", 1)
                        name = name.strip()
                        type_hint = type_hint.split("=")[0].strip()
                    else:
                        name = arg.split("=")[0].strip()
                        type_hint = "string"

                    result["parameters"].append(Parameter(
                        name=name,
                        type=type_hint,
                        required="=" not in arg
                    ))

            # Docstring
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('"""') or next_line.startswith("'''"):
                    docstring_lines = []
                    quote = next_line[:3]

                    if next_line.endswith(quote) and len(next_line) > 6:
                        result["docstring"] = next_line[3:-3]
                    else:
                        docstring_lines.append(next_line[3:])
                        for j in range(i + 2, min(i + 20, len(lines))):
                            doc_line = lines[j]
                            if quote in doc_line:
                                docstring_lines.append(doc_line.split(quote)[0])
                                break
                            docstring_lines.append(doc_line)
                        result["docstring"] = "\n".join(docstring_lines).strip()

            break

    return result


# ============================================================================
# AI Dokümantasyon
# ============================================================================

def ai_document_endpoint(endpoint: Endpoint, code_context: str = "") -> Endpoint:
    """Endpoint'i AI ile dokümante et."""

    prompt = f"""Bu API endpoint için detaylı dokümantasyon üret:

Endpoint: {endpoint.method} {endpoint.path}
Mevcut açıklama: {endpoint.description}
Parametreler: {[p.name for p in endpoint.parameters]}

Kod bağlamı:
{code_context[:1000] if code_context else 'Yok'}

JSON formatında döndür:
{{
    "summary": "<kısa özet>",
    "description": "<detaylı açıklama>",
    "parameters": [
        {{
            "name": "<parametre adı>",
            "type": "<tip>",
            "required": true/false,
            "description": "<açıklama>"
        }}
    ],
    "request_body": {{
        "description": "<açıklama>",
        "content": {{"<örnek alan>": "<örnek değer>"}}
    }},
    "responses": {{
        "200": {{"description": "<başarılı yanıt>"}},
        "400": {{"description": "<hatalı istek>"}},
        "404": {{"description": "<bulunamadı>"}}
    }},
    "tags": ["<tag1>", "<tag2>"]
}}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen API dokümantasyon uzmanısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    try:
        content = response.choices[0].message.content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0]
        else:
            json_str = content

        data = json.loads(json_str)

        endpoint.summary = data.get("summary", endpoint.summary)
        endpoint.description = data.get("description", endpoint.description)
        endpoint.request_body = data.get("request_body")
        endpoint.responses = data.get("responses", {})
        endpoint.tags = data.get("tags", [])

        # Parametreleri güncelle
        for p_data in data.get("parameters", []):
            for p in endpoint.parameters:
                if p.name == p_data.get("name"):
                    p.description = p_data.get("description", "")
                    p.type = p_data.get("type", p.type)

    except Exception:
        pass

    return endpoint


def ai_generate_examples(endpoint: Endpoint) -> dict:
    """Endpoint için örnek kod üret."""

    prompt = f"""Bu API endpoint için örnek kodlar üret:

Endpoint: {endpoint.method} {endpoint.path}
Açıklama: {endpoint.description}
Parametreler: {[(p.name, p.type) for p in endpoint.parameters]}

3 farklı dil için örnek ver:
1. Python (requests)
2. JavaScript (fetch)
3. cURL

JSON formatında döndür:
{{
    "python": "<kod>",
    "javascript": "<kod>",
    "curl": "<komut>"
}}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen API entegrasyon uzmanısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    try:
        content = response.choices[0].message.content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0]
        else:
            json_str = content
        return json.loads(json_str)
    except Exception:
        return {}


# ============================================================================
# Format Üretimi
# ============================================================================

def generate_openapi(api_doc: APIDoc) -> dict:
    """OpenAPI 3.0 spec üret."""

    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": api_doc.title,
            "version": api_doc.version,
            "description": api_doc.description,
        },
        "servers": [{"url": api_doc.base_url}],
        "paths": {},
    }

    for endpoint in api_doc.endpoints:
        path = endpoint.path
        method = endpoint.method.lower()

        if path not in spec["paths"]:
            spec["paths"][path] = {}

        operation = {
            "summary": endpoint.summary,
            "description": endpoint.description,
            "tags": endpoint.tags,
            "parameters": [],
            "responses": endpoint.responses or {"200": {"description": "Başarılı"}},
        }

        for param in endpoint.parameters:
            operation["parameters"].append({
                "name": param.name,
                "in": param.location,
                "required": param.required,
                "description": param.description,
                "schema": {"type": param.type.lower() if param.type else "string"},
            })

        if endpoint.request_body:
            operation["requestBody"] = {
                "description": endpoint.request_body.get("description", ""),
                "content": {
                    "application/json": {
                        "schema": {"type": "object"},
                        "example": endpoint.request_body.get("content", {}),
                    }
                }
            }

        spec["paths"][path][method] = operation

    return spec


def generate_markdown(api_doc: APIDoc) -> str:
    """Markdown dokümantasyon üret."""

    lines = [
        f"# {api_doc.title}",
        "",
        api_doc.description,
        "",
        f"**Versiyon:** {api_doc.version}",
        f"**Base URL:** `{api_doc.base_url}`",
        "",
        "---",
        "",
        "## Endpoints",
        "",
    ]

    # Tag'lere göre grupla
    tags = {}
    for endpoint in api_doc.endpoints:
        tag = endpoint.tags[0] if endpoint.tags else "Genel"
        if tag not in tags:
            tags[tag] = []
        tags[tag].append(endpoint)

    for tag, endpoints in tags.items():
        lines.append(f"### {tag}")
        lines.append("")

        for ep in endpoints:
            lines.append(f"#### `{ep.method}` {ep.path}")
            lines.append("")
            lines.append(ep.description or ep.summary or "Açıklama yok.")
            lines.append("")

            # Parametreler
            if ep.parameters:
                lines.append("**Parametreler:**")
                lines.append("")
                lines.append("| İsim | Tip | Zorunlu | Açıklama |")
                lines.append("|------|-----|---------|----------|")
                for p in ep.parameters:
                    req = "✅" if p.required else "❌"
                    lines.append(f"| `{p.name}` | {p.type} | {req} | {p.description} |")
                lines.append("")

            # Request body
            if ep.request_body:
                lines.append("**Request Body:**")
                lines.append("")
                lines.append("```json")
                lines.append(json.dumps(ep.request_body.get("content", {}), indent=2, ensure_ascii=False))
                lines.append("```")
                lines.append("")

            # Responses
            if ep.responses:
                lines.append("**Responses:**")
                lines.append("")
                for code, resp in ep.responses.items():
                    desc = resp.get("description", "") if isinstance(resp, dict) else resp
                    lines.append(f"- `{code}`: {desc}")
                lines.append("")

            lines.append("---")
            lines.append("")

    return "\n".join(lines)


# ============================================================================
# Çıktı Formatlama
# ============================================================================

def display_endpoints(api_doc: APIDoc):
    """Endpoint'leri göster."""
    console.print()
    console.print(Panel(
        f"[bold]{api_doc.title}[/bold]\n{api_doc.description}",
        title="📚 API Dokümantasyonu"
    ))

    table = Table(show_header=True)
    table.add_column("Method")
    table.add_column("Path")
    table.add_column("Açıklama")
    table.add_column("Parametreler")

    method_colors = {
        "GET": "green",
        "POST": "blue",
        "PUT": "yellow",
        "PATCH": "yellow",
        "DELETE": "red",
    }

    for ep in api_doc.endpoints:
        color = method_colors.get(ep.method, "white")
        params = ", ".join(p.name for p in ep.parameters) or "-"
        table.add_row(
            f"[{color}]{ep.method}[/{color}]",
            ep.path,
            ep.summary[:40] + "..." if len(ep.summary) > 40 else ep.summary,
            params[:30] + "..." if len(params) > 30 else params
        )

    console.print(table)


def display_examples(endpoint: Endpoint, examples: dict):
    """Örnekleri göster."""
    console.print()
    console.print(Panel(
        f"[bold]{endpoint.method} {endpoint.path}[/bold]",
        title="💻 Kod Örnekleri"
    ))

    if examples.get("python"):
        console.print("\n[bold]Python:[/bold]")
        syntax = Syntax(examples["python"], "python", theme="monokai")
        console.print(syntax)

    if examples.get("javascript"):
        console.print("\n[bold]JavaScript:[/bold]")
        syntax = Syntax(examples["javascript"], "javascript", theme="monokai")
        console.print(syntax)

    if examples.get("curl"):
        console.print("\n[bold]cURL:[/bold]")
        syntax = Syntax(examples["curl"], "bash", theme="monokai")
        console.print(syntax)


# ============================================================================
# CLI
# ============================================================================

def main():
    """Ana fonksiyon."""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax-M2 API Dokümantasyon Üretici")
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # generate komutu
    gen_parser = subparsers.add_parser("generate", help="Dokümantasyon üret")
    gen_parser.add_argument("file", help="Kaynak dosya")
    gen_parser.add_argument("--format", "-f", choices=["openapi", "markdown", "both"], default="both")
    gen_parser.add_argument("--output", "-o", help="Çıktı dosyası")
    gen_parser.add_argument("--title", "-t", default="API Dokümantasyonu")

    # examples komutu
    ex_parser = subparsers.add_parser("examples", help="Örnek kod üret")
    ex_parser.add_argument("file", help="Kaynak dosya")
    ex_parser.add_argument("--endpoint", "-e", help="Belirli endpoint")

    # demo komutu
    subparsers.add_parser("demo", help="Demo")

    args = parser.parse_args()

    if args.command == "generate":
        file_path = Path(args.file)
        if not file_path.exists():
            console.print(f"[red]Dosya bulunamadı: {file_path}[/red]")
            return

        code = file_path.read_text()
        endpoints = extract_fastapi_endpoints(code)

        if not endpoints:
            console.print("[yellow]Endpoint bulunamadı. AI ile analiz ediliyor...[/yellow]")

        console.print(f"[dim]{len(endpoints)} endpoint bulundu.[/dim]")

        # AI ile zenginleştir
        for i, ep in enumerate(endpoints):
            console.print(f"[dim]Dokümante ediliyor: {ep.method} {ep.path}[/dim]")
            endpoints[i] = ai_document_endpoint(ep, code)

        api_doc = APIDoc(
            title=args.title,
            endpoints=endpoints,
            base_url=f"/{file_path.stem}"
        )

        display_endpoints(api_doc)

        # Format üret
        if args.format in ["openapi", "both"]:
            openapi_spec = generate_openapi(api_doc)
            output = args.output or f"{file_path.stem}_openapi.yaml"

            with open(output, "w") as f:
                yaml.dump(openapi_spec, f, default_flow_style=False, allow_unicode=True)

            console.print(f"\n[green]✅ OpenAPI spec: {output}[/green]")

        if args.format in ["markdown", "both"]:
            md = generate_markdown(api_doc)
            output = args.output or f"{file_path.stem}_docs.md"
            if args.format == "both":
                output = f"{file_path.stem}_docs.md"

            with open(output, "w") as f:
                f.write(md)

            console.print(f"[green]✅ Markdown docs: {output}[/green]")

    elif args.command == "examples":
        file_path = Path(args.file)
        code = file_path.read_text()
        endpoints = extract_fastapi_endpoints(code)

        if args.endpoint:
            endpoints = [e for e in endpoints if args.endpoint in e.path]

        for ep in endpoints:
            examples = ai_generate_examples(ep)
            display_examples(ep, examples)

    elif args.command == "demo":
        console.print(Panel("[bold]MiniMax-M2 API Dokümantasyon Demo[/bold]"))

        demo_code = '''
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str
    age: int

@app.get("/users")
async def get_users(skip: int = 0, limit: int = 10):
    """Kullanıcı listesini getir."""
    return {"users": [], "total": 0}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Belirli bir kullanıcıyı getir."""
    return {"id": user_id, "name": "Test"}

@app.post("/users")
async def create_user(user: User):
    """Yeni kullanıcı oluştur."""
    return {"id": 1, **user.dict()}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Kullanıcıyı sil."""
    return {"deleted": True}
'''

        console.print("\n[bold]Kaynak Kod:[/bold]")
        syntax = Syntax(demo_code, "python", theme="monokai", line_numbers=True)
        console.print(syntax)

        endpoints = extract_fastapi_endpoints(demo_code)

        console.print(f"\n[dim]{len(endpoints)} endpoint bulundu. AI ile dokümante ediliyor...[/dim]")

        for i, ep in enumerate(endpoints):
            endpoints[i] = ai_document_endpoint(ep, demo_code)

        api_doc = APIDoc(
            title="Demo API",
            description="FastAPI ile oluşturulmuş örnek API",
            endpoints=endpoints
        )

        display_endpoints(api_doc)

        # Markdown göster
        console.print("\n[bold]Markdown Çıktısı:[/bold]")
        md = generate_markdown(api_doc)
        console.print(Panel(Markdown(md[:2000] + "..."), title="📝 Dokümantasyon"))

        # Örnek kod
        if endpoints:
            examples = ai_generate_examples(endpoints[0])
            display_examples(endpoints[0], examples)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
