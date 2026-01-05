"""
MODULllm.com - n8n Client
n8n API ile workflow orchestration
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime


class N8nClient:
    """
    n8n Workflow Automation Client

    MODULllm.com ile n8n entegrasyonu
    """

    def __init__(
        self,
        n8n_url: str = "http://localhost:5678",
        api_key: Optional[str] = None,
        username: str = "admin",
        password: str = "modulllm_n8n_2026"
    ):
        self.n8n_url = n8n_url.rstrip('/')
        self.api_key = api_key
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(timeout=120)

        # Authentication
        if api_key:
            self.headers = {
                "X-N8N-API-KEY": api_key,
                "Content-Type": "application/json"
            }
        else:
            # Basic auth
            self.headers = {
                "Content-Type": "application/json"
            }
            self.auth = (username, password)

    async def trigger_webhook(
        self,
        webhook_path: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Webhook trigger

        Args:
            webhook_path: Webhook yolu (örn: "111-akil")
            data: Gönderilecek data
        """
        url = f"{self.n8n_url}/webhook/{webhook_path}"

        try:
            response = await self.client.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()

            return {
                "success": True,
                "data": response.json(),
                "status_code": response.status_code
            }

        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "status_code": e.response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": 0
            }

    async def get_workflows(self) -> List[Dict[str, Any]]:
        """Tüm workflow'ları listele"""
        url = f"{self.n8n_url}/api/v1/workflows"

        try:
            response = await self.client.get(
                url,
                headers=self.headers,
                auth=self.auth if not self.api_key else None
            )

            response.raise_for_status()

            workflows = response.json().get("data", [])

            return workflows

        except Exception as e:
            print(f"❌ Workflow listesi alınamadı: {e}")
            return []

    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Specific workflow detayları"""
        url = f"{self.n8n_url}/api/v1/workflows/{workflow_id}"

        try:
            response = await self.client.get(
                url,
                headers=self.headers,
                auth=self.auth if not self.api_key else None
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:
            print(f"❌ Workflow detayı alınamadı: {e}")
            return None

    async def execute_workflow(
        self,
        workflow_id: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Workflow'u manuel execute et

        Args:
            workflow_id: Workflow ID
            data: Input data
        """
        url = f"{self.n8n_url}/api/v1/workflows/{workflow_id}/execute"

        try:
            response = await self.client.post(
                url,
                json=data or {},
                headers=self.headers,
                auth=self.auth if not self.api_key else None
            )

            response.raise_for_status()

            return {
                "success": True,
                "execution": response.json(),
                "status": "executed"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_executions(
        self,
        workflow_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Workflow execution history"""
        url = f"{self.n8n_url}/api/v1/executions"

        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id

        try:
            response = await self.client.get(
                url,
                params=params,
                headers=self.headers,
                auth=self.auth if not self.api_key else None
            )

            response.raise_for_status()

            executions = response.json().get("data", [])

            return executions

        except Exception as e:
            print(f"❌ Execution history alınamadı: {e}")
            return []

    async def close(self):
        """Cleanup"""
        await self.client.aclose()


# MODULllm.com Integration
class MODULllmN8nOrchestrator:
    """
    MODULllm.com n8n Orchestration

    Tüm LLM'leri n8n ile orchestrate et
    """

    def __init__(self, n8n_url: str = "http://localhost:5678"):
        self.n8n = N8nClient(n8n_url)

    async def query_111_akil(
        self,
        soru: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        111 Akıl Sistemine soru sor (n8n üzerinden)

        n8n workflow'u tüm LLM'lere paralel sorgu gönderir
        """
        print(f"\n🔗 n8n ile 111 Akıl Sistemi aktif...")
        print(f"📝 Soru: {soru}\n")

        # Webhook trigger
        result = await self.n8n.trigger_webhook(
            webhook_path="111-akil",
            data={
                "soru": soru,
                "context": context or ""
            }
        )

        if result["success"]:
            print(f"✅ n8n workflow başarıyla tamamlandı!")
            return result["data"]
        else:
            print(f"❌ n8n workflow hatası: {result['error']}")
            return {
                "error": result["error"],
                "success": False
            }

    async def multi_llm_compare(
        self,
        prompt: str,
        llms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Aynı prompt'u farklı LLM'lere gönder, karşılaştır

        Args:
            prompt: Test prompt
            llms: LLM listesi (default: ["gemini", "gpt4", "claude", "minimax"])
        """
        if llms is None:
            llms = ["gemini", "gpt4", "claude", "minimax", "llama"]

        result = await self.n8n.trigger_webhook(
            webhook_path="multi-llm-compare",
            data={
                "prompt": prompt,
                "llms": llms
            }
        )

        return result

    async def auto_translate(
        self,
        content: str,
        target_languages: List[str] = None
    ) -> Dict[str, Any]:
        """
        İçeriği birden fazla dile otomatik çevir

        Args:
            content: Çevrilecek içerik
            target_languages: Hedef diller (default: 30+ dil)
        """
        if target_languages is None:
            # Default: MODULllm.com ana dilleri
            target_languages = [
                "tr", "en", "ar", "zh", "ru", "es", "fr", "de",
                "ja", "ko", "hi", "pt", "it", "nl", "pl"
            ]

        result = await self.n8n.trigger_webhook(
            webhook_path="auto-translate",
            data={
                "content": content,
                "languages": target_languages
            }
        )

        return result

    async def smart_router(
        self,
        query: str,
        priority: str = "cost"  # "cost", "speed", "quality"
    ) -> Dict[str, Any]:
        """
        Akıllı LLM routing

        priority:
          - "cost": En ucuz LLM'i kullan
          - "speed": En hızlı LLM'i kullan
          - "quality": En kaliteli LLM'i kullan
        """
        result = await self.n8n.trigger_webhook(
            webhook_path="smart-router",
            data={
                "query": query,
                "priority": priority
            }
        )

        return result

    async def workflow_stats(self) -> Dict[str, Any]:
        """n8n workflow istatistikleri"""
        workflows = await self.n8n.get_workflows()
        executions = await self.n8n.get_executions(limit=100)

        # Success rate hesapla
        total_executions = len(executions)
        successful = sum(1 for e in executions if e.get("finished") == True)
        success_rate = (successful / total_executions * 100) if total_executions > 0 else 0

        return {
            "total_workflows": len(workflows),
            "active_workflows": sum(1 for w in workflows if w.get("active") == True),
            "total_executions": total_executions,
            "successful_executions": successful,
            "success_rate": f"{success_rate:.1f}%",
            "workflows": [
                {
                    "id": w["id"],
                    "name": w["name"],
                    "active": w.get("active", False),
                    "nodes": len(w.get("nodes", []))
                }
                for w in workflows
            ]
        }

    async def close(self):
        """Cleanup"""
        await self.n8n.close()


# Test & Demo
async def test_n8n_integration():
    """n8n entegrasyonu test"""
    print("\n" + "="*80)
    print("🔗 MODULllm.com n8n Integration Test")
    print("="*80 + "\n")

    orchestrator = MODULllmN8nOrchestrator()

    # Test 1: 111 Akıl Query
    print("📝 Test 1: 111 Akıl Sistemi\n")

    result = await orchestrator.query_111_akil(
        soru="n8n ile AI orchestration'ın avantajları nedir?"
    )

    if "error" not in result:
        print(f"✅ 111 Akıl Yanıtı alındı!")
        print(f"\nUltimate Sentez:\n{result.get('ultimate_synthesis', 'N/A')[:500]}...\n")
    else:
        print(f"⚠️ Workflow henüz kurulmamış veya n8n offline")
        print(f"Hata: {result.get('error')}\n")

    # Test 2: Workflow Stats
    print("\n" + "-"*80)
    print("📊 Test 2: Workflow İstatistikleri\n")

    stats = await orchestrator.workflow_stats()

    print(f"Toplam Workflow: {stats['total_workflows']}")
    print(f"Aktif Workflow: {stats['active_workflows']}")
    print(f"Toplam Execution: {stats['total_executions']}")
    print(f"Success Rate: {stats['success_rate']}\n")

    if stats['workflows']:
        print("Workflows:")
        for w in stats['workflows'][:5]:
            print(f"  - {w['name']} (ID: {w['id'][:8]}..., Nodes: {w['nodes']})")

    await orchestrator.close()

    print("\n" + "="*80)
    print("✅ Test tamamlandı!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_n8n_integration())
