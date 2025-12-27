"""
🔗 N8N INTEGRATION
==================
N8N Workflow Webhook Entegrasyonu

Dua Çarkları'nı gerçek N8N workflow'larına bağlar.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import hashlib

# HTTP client (optional)
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class WebhookTrigger(Enum):
    """N8N Webhook tetikleyici türleri"""
    ON_DATA_RECEIVED = "on_data_received"
    ON_LAYER_COMPLETE = "on_layer_complete"
    ON_JOURNEY_START = "on_journey_start"
    ON_JOURNEY_END = "on_journey_end"
    ON_CRYSTAL_CREATED = "on_crystal_created"
    ON_ERROR = "on_error"
    MANUAL = "manual"


@dataclass
class WebhookConfig:
    """Webhook yapılandırması"""

    name: str
    url: str
    trigger: WebhookTrigger
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0
    retry_count: int = 3
    enabled: bool = True
    secret_key: Optional[str] = None

    def __post_init__(self):
        if not self.headers:
            self.headers = {"Content-Type": "application/json"}

    def sign_payload(self, payload: str) -> str:
        """Payload'ı imzala"""
        if not self.secret_key:
            return ""
        return hashlib.sha256(
            f"{self.secret_key}:{payload}".encode()
        ).hexdigest()


@dataclass
class WebhookResult:
    """Webhook çağrı sonucu"""

    webhook_name: str
    success: bool
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "webhook": self.webhook_name,
            "success": self.success,
            "status_code": self.status_code,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat()
        }


class N8NClient:
    """
    N8N Webhook İstemcisi

    N8N workflow'larını tetiklemek için webhook çağrıları yapar.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or "http://localhost:5678"
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.results: List[WebhookResult] = []
        self._client: Optional[Any] = None

        if HTTPX_AVAILABLE:
            self._client = httpx.AsyncClient(timeout=30.0)

    def register_webhook(self, config: WebhookConfig) -> None:
        """Webhook kaydet"""
        self.webhooks[config.name] = config

    def unregister_webhook(self, name: str) -> bool:
        """Webhook kaydını sil"""
        if name in self.webhooks:
            del self.webhooks[name]
            return True
        return False

    async def trigger(
        self,
        webhook_name: str,
        payload: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> WebhookResult:
        """
        Webhook tetikle

        Args:
            webhook_name: Tetiklenecek webhook adı
            payload: Gönderilecek veri
            context: Ek bağlam

        Returns:
            WebhookResult: Çağrı sonucu
        """
        if webhook_name not in self.webhooks:
            return WebhookResult(
                webhook_name=webhook_name,
                success=False,
                error=f"Webhook bulunamadı: {webhook_name}"
            )

        config = self.webhooks[webhook_name]

        if not config.enabled:
            return WebhookResult(
                webhook_name=webhook_name,
                success=False,
                error="Webhook devre dışı"
            )

        # Payload hazırla
        full_payload = {
            "trigger": config.trigger.value,
            "timestamp": datetime.now().isoformat(),
            "data": payload,
            "context": context or {}
        }

        payload_json = json.dumps(full_payload)

        # İmza ekle
        if config.secret_key:
            signature = config.sign_payload(payload_json)
            config.headers["X-Webhook-Signature"] = signature

        # Çağrı yap
        result = await self._make_request(config, payload_json)
        self.results.append(result)

        return result

    async def _make_request(
        self,
        config: WebhookConfig,
        payload: str
    ) -> WebhookResult:
        """HTTP isteği yap"""
        start_time = datetime.now()

        if not HTTPX_AVAILABLE or not self._client:
            # Mock mod - gerçek istek yapma
            await asyncio.sleep(0.1)  # Simüle gecikme
            return WebhookResult(
                webhook_name=config.name,
                success=True,
                status_code=200,
                response_body='{"status": "ok", "mode": "mock"}',
                duration_ms=100.0
            )

        # Gerçek HTTP isteği
        for attempt in range(config.retry_count):
            try:
                response = await self._client.request(
                    method=config.method,
                    url=config.url,
                    content=payload,
                    headers=config.headers,
                    timeout=config.timeout
                )

                duration = (datetime.now() - start_time).total_seconds() * 1000

                return WebhookResult(
                    webhook_name=config.name,
                    success=response.status_code < 400,
                    status_code=response.status_code,
                    response_body=response.text[:1000],
                    duration_ms=duration
                )

            except Exception as e:
                if attempt == config.retry_count - 1:
                    duration = (datetime.now() - start_time).total_seconds() * 1000
                    return WebhookResult(
                        webhook_name=config.name,
                        success=False,
                        error=str(e),
                        duration_ms=duration
                    )
                await asyncio.sleep(1.0 * (attempt + 1))  # Exponential backoff

        return WebhookResult(
            webhook_name=config.name,
            success=False,
            error="Max retry exceeded"
        )

    async def trigger_by_event(
        self,
        event: WebhookTrigger,
        payload: Dict[str, Any]
    ) -> List[WebhookResult]:
        """
        Olay türüne göre tüm ilgili webhook'ları tetikle

        Args:
            event: Olay türü
            payload: Gönderilecek veri

        Returns:
            Tüm sonuçların listesi
        """
        matching = [
            config for config in self.webhooks.values()
            if config.trigger == event and config.enabled
        ]

        if not matching:
            return []

        tasks = [
            self.trigger(config.name, payload)
            for config in matching
        ]

        return await asyncio.gather(*tasks)

    def get_stats(self) -> Dict[str, Any]:
        """İstatistikler"""
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful

        return {
            "total_webhooks": len(self.webhooks),
            "enabled_webhooks": sum(1 for w in self.webhooks.values() if w.enabled),
            "total_calls": len(self.results),
            "successful_calls": successful,
            "failed_calls": failed,
            "success_rate": successful / len(self.results) if self.results else 0,
            "recent_results": [r.to_dict() for r in self.results[-10:]]
        }

    async def close(self) -> None:
        """İstemciyi kapat"""
        if self._client:
            await self._client.aclose()


class N8NWorkflowBuilder:
    """
    N8N Workflow Oluşturucu

    Kathmandu Engine için standart N8N workflow şablonları.
    """

    @staticmethod
    def create_layer_workflow(layer_name: str) -> Dict[str, Any]:
        """Katman workflow şablonu oluştur"""
        return {
            "name": f"Kathmandu_{layer_name}_Workflow",
            "nodes": [
                {
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "position": [250, 300],
                    "parameters": {
                        "path": f"kathmandu/{layer_name.lower()}",
                        "httpMethod": "POST"
                    }
                },
                {
                    "name": "Process Data",
                    "type": "n8n-nodes-base.function",
                    "position": [450, 300],
                    "parameters": {
                        "functionCode": f"""
// {layer_name} Layer Processing
const data = items[0].json.data;
const context = items[0].json.context;

// Transform data
const processed = {{
    layer: '{layer_name}',
    processed_at: new Date().toISOString(),
    input: data,
    output: `${{layer_name}}_PROCESSED_${{JSON.stringify(data).slice(0, 50)}}`
}};

return [{{ json: processed }}];
"""
                    }
                },
                {
                    "name": "Return Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "position": [650, 300],
                    "parameters": {}
                }
            ],
            "connections": {
                "Webhook Trigger": {
                    "main": [[{"node": "Process Data", "type": "main", "index": 0}]]
                },
                "Process Data": {
                    "main": [[{"node": "Return Response", "type": "main", "index": 0}]]
                }
            }
        }

    @staticmethod
    def create_full_pipeline_workflow() -> Dict[str, Any]:
        """Tam pipeline workflow şablonu"""
        return {
            "name": "Kathmandu_Full_Pipeline",
            "nodes": [
                {
                    "name": "Start",
                    "type": "n8n-nodes-base.webhook",
                    "position": [250, 300],
                    "parameters": {
                        "path": "kathmandu/pipeline",
                        "httpMethod": "POST"
                    }
                },
                {
                    "name": "TOPRAK",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [450, 300],
                    "parameters": {
                        "url": "={{$env.KATHMANDU_API}}/layers/toprak",
                        "method": "POST"
                    }
                },
                {
                    "name": "SU",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [650, 300],
                    "parameters": {
                        "url": "={{$env.KATHMANDU_API}}/layers/su",
                        "method": "POST"
                    }
                },
                {
                    "name": "ATES",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [850, 300],
                    "parameters": {
                        "url": "={{$env.KATHMANDU_API}}/layers/ates",
                        "method": "POST"
                    }
                },
                {
                    "name": "HAVA",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [1050, 300],
                    "parameters": {
                        "url": "={{$env.KATHMANDU_API}}/layers/hava",
                        "method": "POST"
                    }
                },
                {
                    "name": "ETER",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [1250, 300],
                    "parameters": {
                        "url": "={{$env.KATHMANDU_API}}/layers/eter",
                        "method": "POST"
                    }
                },
                {
                    "name": "Respond",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "position": [1450, 300]
                }
            ],
            "connections": {
                "Start": {"main": [[{"node": "TOPRAK", "type": "main", "index": 0}]]},
                "TOPRAK": {"main": [[{"node": "SU", "type": "main", "index": 0}]]},
                "SU": {"main": [[{"node": "ATES", "type": "main", "index": 0}]]},
                "ATES": {"main": [[{"node": "HAVA", "type": "main", "index": 0}]]},
                "HAVA": {"main": [[{"node": "ETER", "type": "main", "index": 0}]]},
                "ETER": {"main": [[{"node": "Respond", "type": "main", "index": 0}]]}
            }
        }

    @staticmethod
    def export_workflow(workflow: Dict[str, Any], filepath: str) -> None:
        """Workflow'u JSON dosyasına kaydet"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)


# Stupa ile entegrasyon
class N8NIntegratedStupa:
    """
    N8N Entegreli Stupa

    Her katman geçişinde N8N webhook'larını tetikler.
    """

    def __init__(self, stupa, n8n_client: Optional[N8NClient] = None):
        self.stupa = stupa
        self.n8n = n8n_client or N8NClient()

        # Varsayılan webhook'ları kaydet
        self._setup_default_webhooks()

    def _setup_default_webhooks(self) -> None:
        """Varsayılan webhook'ları ayarla"""
        default_webhooks = [
            WebhookConfig(
                name="journey_start",
                url=f"{self.n8n.base_url}/webhook/kathmandu/journey/start",
                trigger=WebhookTrigger.ON_JOURNEY_START
            ),
            WebhookConfig(
                name="journey_end",
                url=f"{self.n8n.base_url}/webhook/kathmandu/journey/end",
                trigger=WebhookTrigger.ON_JOURNEY_END
            ),
            WebhookConfig(
                name="crystal_created",
                url=f"{self.n8n.base_url}/webhook/kathmandu/crystal",
                trigger=WebhookTrigger.ON_CRYSTAL_CREATED
            ),
        ]

        for webhook in default_webhooks:
            self.n8n.register_webhook(webhook)

    async def process_with_hooks(
        self,
        data: Any,
        context: Optional[Dict] = None
    ):
        """N8N hook'larıyla birlikte işle"""
        context = context or {}

        # Yolculuk başlangıcı
        await self.n8n.trigger_by_event(
            WebhookTrigger.ON_JOURNEY_START,
            {"data": str(data)[:500], "context": context}
        )

        # İşleme
        journey = await self.stupa.process(data, context)

        # Yolculuk sonu
        await self.n8n.trigger_by_event(
            WebhookTrigger.ON_JOURNEY_END,
            {
                "journey_id": journey.journey_id,
                "duration": journey.duration_seconds,
                "layers": journey.layers_traversed,
                "state": journey.state.value
            }
        )

        # Kristal oluşturuldu
        if journey.final_output:
            crystal = journey.final_output.get("crystal", {})
            if crystal:
                await self.n8n.trigger_by_event(
                    WebhookTrigger.ON_CRYSTAL_CREATED,
                    crystal
                )

        return journey
