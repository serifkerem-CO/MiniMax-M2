"""
MiniMax-M2 Web Scraper Şablonu
==============================
AI destekli akıllı web kazıma.

Özellikler:
- Dinamik sayfa analizi
- Akıllı veri çıkarma
- Yapılandırılmış çıktı
- Rate limiting
- Retry mekanizması

Gereksinimler:
    pip install openai requests beautifulsoup4 lxml

Kullanım:
    python main.py "https://example.com" --extract "ürün bilgileri"
"""

import os
import re
import json
import time
from typing import Optional, Any
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# Scraper ayarları
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
REQUEST_TIMEOUT = 30
RATE_LIMIT_DELAY = 1.0  # saniye

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)


# ============================================================================
# Veri Yapıları
# ============================================================================

@dataclass
class ScrapedPage:
    """Kazınan sayfa."""
    url: str
    title: str
    content: str
    html: str
    links: list = field(default_factory=list)
    images: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Çıkarma sonucu."""
    url: str
    query: str
    data: Any
    raw_text: str
    confidence: float


# ============================================================================
# Web Fetcher
# ============================================================================

class WebFetcher:
    """Web sayfası çekici."""

    def __init__(self, timeout: int = REQUEST_TIMEOUT, delay: float = RATE_LIMIT_DELAY):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.timeout = timeout
        self.delay = delay
        self.last_request_time = 0

    def _rate_limit(self):
        """Rate limiting uygula."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def fetch(self, url: str, retries: int = 3) -> Optional[str]:
        """Sayfa HTML'ini getir."""
        self._rate_limit()

        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"⚠️ Deneme {attempt + 1}/{retries}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def fetch_json(self, url: str) -> Optional[dict]:
        """JSON API çağrısı."""
        self._rate_limit()

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"❌ JSON hatası: {e}")
            return None


# ============================================================================
# HTML Parser
# ============================================================================

class HTMLParser:
    """HTML ayrıştırıcı."""

    def __init__(self, html: str, base_url: str = ""):
        self.soup = BeautifulSoup(html, "lxml")
        self.base_url = base_url

    def get_title(self) -> str:
        """Sayfa başlığını al."""
        title = self.soup.find("title")
        return title.get_text().strip() if title else ""

    def get_text(self, selector: str = None) -> str:
        """Metin içeriğini al."""
        if selector:
            elements = self.soup.select(selector)
            return "\n".join(el.get_text().strip() for el in elements)

        # Ana içeriği bul
        for tag in ["article", "main", ".content", "#content", ".post", ".article"]:
            content = self.soup.select_one(tag)
            if content:
                return content.get_text(separator="\n", strip=True)

        # Body içeriği
        body = self.soup.find("body")
        if body:
            # Script ve style etiketlerini kaldır
            for tag in body.find_all(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return body.get_text(separator="\n", strip=True)

        return ""

    def get_links(self) -> list[dict]:
        """Linkleri al."""
        links = []
        for a in self.soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#"):
                continue
            full_url = urljoin(self.base_url, href)
            links.append({
                "url": full_url,
                "text": a.get_text().strip(),
            })
        return links

    def get_images(self) -> list[dict]:
        """Görselleri al."""
        images = []
        for img in self.soup.find_all("img", src=True):
            src = img["src"]
            full_url = urljoin(self.base_url, src)
            images.append({
                "url": full_url,
                "alt": img.get("alt", ""),
            })
        return images

    def get_metadata(self) -> dict:
        """Meta verileri al."""
        metadata = {}

        # Meta etiketleri
        for meta in self.soup.find_all("meta"):
            name = meta.get("name") or meta.get("property", "")
            content = meta.get("content", "")
            if name and content:
                metadata[name] = content

        return metadata

    def select(self, selector: str) -> list:
        """CSS selector ile seç."""
        return self.soup.select(selector)

    def select_one(self, selector: str):
        """Tek element seç."""
        return self.soup.select_one(selector)


# ============================================================================
# AI Extractor
# ============================================================================

class AIExtractor:
    """AI destekli veri çıkarıcı."""

    def extract(self, text: str, query: str) -> dict:
        """Metinden veri çıkar."""
        prompt = f"""Bu metinden aşağıdaki bilgileri çıkar:

ARADIĞIM: {query}

METİN:
{text[:4000]}

JSON formatında döndür. Bulunamayan bilgiler için null kullan.
Sadece JSON döndür, başka bir şey yazma."""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Sen web scraping ve veri çıkarma uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
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
        except json.JSONDecodeError:
            return {"raw_response": content}

    def analyze_page_structure(self, html: str) -> dict:
        """Sayfa yapısını analiz et."""
        # HTML'i kısalt
        soup = BeautifulSoup(html, "lxml")
        structure = []

        for tag in soup.find_all(["h1", "h2", "h3", "article", "section", "div"]):
            if tag.get("class") or tag.get("id"):
                structure.append({
                    "tag": tag.name,
                    "class": tag.get("class", []),
                    "id": tag.get("id", ""),
                    "sample": tag.get_text()[:50] if tag.get_text() else "",
                })

        prompt = f"""Bu sayfa yapısını analiz et ve veri çıkarmak için en uygun CSS selector'ları öner:

{json.dumps(structure[:20], ensure_ascii=False)}

JSON formatında döndür:
{{
    "main_content": "selector",
    "title": "selector",
    "items": "selector (liste elemanları için)",
    "suggested_extractions": ["çıkarılabilecek veri türleri"]
}}"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Sen web scraping uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500,
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
        except json.JSONDecodeError:
            return {}


# ============================================================================
# Web Scraper
# ============================================================================

class WebScraper:
    """Akıllı web kazıyıcı."""

    def __init__(self):
        self.fetcher = WebFetcher()
        self.extractor = AIExtractor()

    def scrape(self, url: str) -> Optional[ScrapedPage]:
        """Sayfayı kazı."""
        print(f"🌐 Sayfa çekiliyor: {url}")

        html = self.fetcher.fetch(url)
        if not html:
            return None

        parser = HTMLParser(html, url)

        return ScrapedPage(
            url=url,
            title=parser.get_title(),
            content=parser.get_text(),
            html=html,
            links=parser.get_links(),
            images=parser.get_images(),
            metadata=parser.get_metadata(),
        )

    def extract(self, url: str, query: str) -> Optional[ExtractionResult]:
        """Sayfadan veri çıkar."""
        page = self.scrape(url)
        if not page:
            return None

        print(f"🔍 Veri çıkarılıyor: {query}")
        data = self.extractor.extract(page.content, query)

        return ExtractionResult(
            url=url,
            query=query,
            data=data,
            raw_text=page.content[:1000],
            confidence=0.9,
        )

    def crawl(self, start_url: str, max_pages: int = 10, same_domain: bool = True) -> list[ScrapedPage]:
        """Birden fazla sayfayı kazı."""
        visited = set()
        to_visit = [start_url]
        pages = []

        domain = urlparse(start_url).netloc

        while to_visit and len(pages) < max_pages:
            url = to_visit.pop(0)

            if url in visited:
                continue

            visited.add(url)

            page = self.scrape(url)
            if not page:
                continue

            pages.append(page)

            # Linkleri ekle
            for link in page.links:
                link_url = link["url"]
                link_domain = urlparse(link_url).netloc

                if same_domain and link_domain != domain:
                    continue

                if link_url not in visited and link_url not in to_visit:
                    to_visit.append(link_url)

        return pages


# ============================================================================
# CLI
# ============================================================================

def main():
    """Ana fonksiyon."""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax-M2 Web Scraper")
    parser.add_argument("url", nargs="?", help="Kazınacak URL")
    parser.add_argument("--extract", "-e", help="Çıkarılacak veri açıklaması")
    parser.add_argument("--crawl", "-c", type=int, help="Taranacak sayfa sayısı")
    parser.add_argument("--output", "-o", help="Çıktı dosyası (JSON)")
    parser.add_argument("--demo", action="store_true", help="Demo modu")

    args = parser.parse_args()

    if args.demo:
        # Demo
        print("=" * 60)
        print("🕷️ MiniMax-M2 Web Scraper Demo")
        print("=" * 60)

        scraper = WebScraper()

        # Örnek URL
        url = "https://httpbin.org/html"
        print(f"\n📄 Sayfa kazınıyor: {url}")

        page = scraper.scrape(url)
        if page:
            print(f"\n✅ Başlık: {page.title}")
            print(f"📝 İçerik: {page.content[:200]}...")
            print(f"🔗 Link sayısı: {len(page.links)}")

        return

    if not args.url:
        parser.print_help()
        return

    scraper = WebScraper()

    if args.extract:
        # Veri çıkarma
        result = scraper.extract(args.url, args.extract)
        if result:
            print(f"\n📊 Çıkarılan Veri:")
            print(json.dumps(result.data, indent=2, ensure_ascii=False))

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(result.data, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Kaydedildi: {args.output}")

    elif args.crawl:
        # Çoklu sayfa
        pages = scraper.crawl(args.url, max_pages=args.crawl)
        print(f"\n📄 {len(pages)} sayfa kazındı")

        if args.output:
            data = [{"url": p.url, "title": p.title, "content": p.content[:500]} for p in pages]
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Kaydedildi: {args.output}")

    else:
        # Tek sayfa
        page = scraper.scrape(args.url)
        if page:
            print(f"\n📄 Başlık: {page.title}")
            print(f"📝 İçerik ({len(page.content)} karakter)")
            print(f"🔗 {len(page.links)} link, 🖼️ {len(page.images)} görsel")

            if args.output:
                data = {
                    "url": page.url,
                    "title": page.title,
                    "content": page.content,
                    "links": page.links,
                    "images": page.images,
                    "metadata": page.metadata,
                }
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Kaydedildi: {args.output}")


if __name__ == "__main__":
    main()
