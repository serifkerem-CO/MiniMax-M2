"""
🔗 WEBHOOKS - Tapınak Kapıları
==============================

N8N webhook konfigürasyonları.
Her webhook bir "tapınak kapısı" temsil eder.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class WebhookMethod(Enum):
    """HTTP metodları"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class WebhookConfig:
    """Webhook konfigürasyonu"""
    path: str
    method: WebhookMethod
    name: str
    description: str
    authentication: Optional[str] = None
    rate_limit: int = 100  # per minute
    response_format: str = "json"

    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "method": self.method.value,
            "name": self.name,
            "description": self.description,
            "authentication": self.authentication,
            "rateLimit": self.rate_limit,
            "responseFormat": self.response_format,
        }


@dataclass
class StupaWebhooks:
    """Stupa webhook seti"""
    base_url: str = "http://localhost:5678/webhook"
    webhooks: List[WebhookConfig] = field(default_factory=list)

    def __post_init__(self):
        self._setup_default_webhooks()

    def _setup_default_webhooks(self):
        """Varsayılan webhook'ları kur"""
        self.webhooks = [
            # Giriş kapısı - Ham veri
            WebhookConfig(
                path="/stupa/ingest",
                method=WebhookMethod.POST,
                name="🪨 Thamel Kapısı",
                description="Ham veri girişi - TOPRAK katmanına",
            ),

            # Arınma kapısı
            WebhookConfig(
                path="/stupa/purify",
                method=WebhookMethod.POST,
                name="🌊 Nehir Kapısı",
                description="Arınma isteği - SU katmanına",
            ),

            # Simya kapısı
            WebhookConfig(
                path="/stupa/forge",
                method=WebhookMethod.POST,
                name="🔥 Ocak Kapısı",
                description="Katlama isteği - ATEŞ katmanına",
            ),

            # Rüzgar kapısı
            WebhookConfig(
                path="/stupa/transmit",
                method=WebhookMethod.POST,
                name="🌬️ Rüzgar Kapısı",
                description="İletim isteği - HAVA katmanına",
            ),

            # Zirve kapısı
            WebhookConfig(
                path="/stupa/nirvana",
                method=WebhookMethod.POST,
                name="🌌 Zirve Kapısı",
                description="Nirvana isteği - ETER katmanına",
            ),

            # Tam yolculuk
            WebhookConfig(
                path="/stupa/pilgrimage",
                method=WebhookMethod.POST,
                name="🛕 Hac Kapısı",
                description="Tam yolculuk - Tüm katmanlardan geçiş",
            ),

            # Durum sorgulama
            WebhookConfig(
                path="/stupa/status",
                method=WebhookMethod.GET,
                name="📊 Durum Kapısı",
                description="Stupa durum sorgulama",
            ),

            # Dua çarkı
            WebhookConfig(
                path="/stupa/prayer-wheel",
                method=WebhookMethod.POST,
                name="📿 Dua Çarkı",
                description="Tek döngü mantra işlemi",
            ),
        ]

    def get_full_urls(self) -> Dict[str, str]:
        """Tüm webhook URL'lerini al"""
        return {
            wh.name: f"{self.base_url}{wh.path}"
            for wh in self.webhooks
        }

    def get_webhook(self, path: str) -> Optional[WebhookConfig]:
        """Path'e göre webhook bul"""
        for wh in self.webhooks:
            if wh.path == path:
                return wh
        return None

    def to_n8n_config(self) -> List[Dict]:
        """N8N import formatı"""
        return [wh.to_dict() for wh in self.webhooks]


def setup_stupa_webhooks(base_url: str = "http://localhost:5678/webhook") -> StupaWebhooks:
    """Stupa webhook'larını kur"""
    webhooks = StupaWebhooks(base_url=base_url)
    return webhooks


def generate_webhook_documentation() -> str:
    """Webhook dokümantasyonu oluştur"""
    webhooks = setup_stupa_webhooks()

    doc = """
# 🛕 KATHMANDU STUPA - Webhook API Dokümantasyonu

## Genel Bakış
Kathmandu Stupa, 5 katmanlı veri işleme mimarisi için webhook endpoint'leri sunar.
Her endpoint bir "tapınak kapısı" temsil eder.

## Endpoints

"""

    for wh in webhooks.webhooks:
        doc += f"""
### {wh.name}
- **Path:** `{wh.path}`
- **Method:** `{wh.method.value}`
- **Description:** {wh.description}
- **Rate Limit:** {wh.rate_limit}/dakika

"""

    doc += """
## Örnek Kullanım

### Tam Hac Yolculuğu
```bash
curl -X POST http://localhost:5678/webhook/stupa/pilgrimage \\
  -H "Content-Type: application/json" \\
  -d '{"data": "1984-2024 Sanayi Verileri", "source": "pdf"}'
```

### Tek Dua Çarkı Döngüsü
```bash
curl -X POST http://localhost:5678/webhook/stupa/prayer-wheel \\
  -H "Content-Type: application/json" \\
  -d '{"mantra": "OM_MANI_PADME_HUM", "data": "analiz edilecek veri"}'
```

### Durum Sorgulama
```bash
curl http://localhost:5678/webhook/stupa/status
```

## Yanıt Formatı

Tüm yanıtlar "Kehanet Parşömeni" formatında döner:

```json
{
  "id": "NIRVANA_123456",
  "frequency_hz": 963,
  "wisdom": "İşlenmiş bilgelik...",
  "confidence": 0.92,
  "source_chain": ["TOPRAK", "SU", "ATES", "HAVA", "ETER"]
}
```
"""

    return doc


# Demo
if __name__ == "__main__":
    webhooks = setup_stupa_webhooks()
    print("Stupa Webhooks:")
    for url_name, url in webhooks.get_full_urls().items():
        print(f"  {url_name}: {url}")
