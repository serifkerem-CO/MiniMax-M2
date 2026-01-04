"""
N8N CONNECTOR - Dua Carki Baglayici
===================================
N8N workflow sistemine baglanip carklari dondurur.
"""

import asyncio
import aiohttp
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Callable
import json


class WorkflowTrigger(Enum):
    """Workflow Tetikleyicileri"""
    WEBHOOK = "webhook"          # HTTP webhook
    SCHEDULE = "schedule"        # Zamanli calistirma
    MANUAL = "manual"            # Elle tetikleme
    EVENT = "event"              # Olay bazli


@dataclass
class N8NCredentials:
    """N8N Kimlik Bilgileri"""
    host: str = "http://localhost:5678"
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class N8NWorkflow:
    """N8N Workflow Tanimlayicisi"""
    workflow_id: str
    name: str
    description: str
    trigger: WorkflowTrigger
    nodes: list[dict] = field(default_factory=list)
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "trigger": self.trigger.value,
            "nodes": self.nodes,
            "active": self.is_active,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class WorkflowExecution:
    """Workflow Calistirma Sonucu"""
    execution_id: str
    workflow_id: str
    status: str  # running, success, error
    start_time: datetime
    end_time: Optional[datetime] = None
    input_data: Any = None
    output_data: Any = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "output": self.output_data,
            "error": self.error
        }


class N8NConnector:
    """
    N8N API Connector

    N8N workflow sistemine baglanip:
    - Workflow olusturma
    - Workflow calistirma
    - Sonuc alma

    islemlerini yapar.
    """

    def __init__(self, credentials: Optional[N8NCredentials] = None):
        self.credentials = credentials or N8NCredentials()
        self._session: Optional[aiohttp.ClientSession] = None
        self.workflows: dict[str, N8NWorkflow] = {}
        self.executions: list[WorkflowExecution] = []

        # Simulated mode (N8N bagli degilken)
        self._simulated = True

    async def _get_session(self) -> aiohttp.ClientSession:
        """HTTP session al veya olustur"""
        if self._session is None or self._session.closed:
            headers = {}
            if self.credentials.api_key:
                headers["X-N8N-API-KEY"] = self.credentials.api_key
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def close(self):
        """Baglantıyı kapat"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def health_check(self) -> bool:
        """N8N sunucu saglik kontrolu"""
        if self._simulated:
            return True

        try:
            session = await self._get_session()
            async with session.get(f"{self.credentials.host}/healthz") as resp:
                return resp.status == 200
        except Exception:
            return False

    async def create_workflow(self, workflow: N8NWorkflow) -> N8NWorkflow:
        """Yeni workflow olustur"""
        if self._simulated:
            self.workflows[workflow.workflow_id] = workflow
            print(f"   [N8N] Workflow olusturuldu (simulated): {workflow.name}")
            return workflow

        session = await self._get_session()
        payload = {
            "name": workflow.name,
            "nodes": workflow.nodes,
            "connections": {},
            "active": workflow.is_active
        }

        async with session.post(
            f"{self.credentials.host}/api/v1/workflows",
            json=payload
        ) as resp:
            if resp.status == 201:
                data = await resp.json()
                workflow.workflow_id = data.get("id", workflow.workflow_id)
                self.workflows[workflow.workflow_id] = workflow
                return workflow
            else:
                raise RuntimeError(f"Workflow olusturulamadi: {await resp.text()}")

    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Any = None
    ) -> WorkflowExecution:
        """Workflow calistir"""
        execution = WorkflowExecution(
            execution_id=f"exec_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            workflow_id=workflow_id,
            status="running",
            start_time=datetime.now(),
            input_data=input_data
        )

        if self._simulated:
            # Simulated execution
            await asyncio.sleep(0.1)
            execution.status = "success"
            execution.end_time = datetime.now()
            execution.output_data = {
                "result": f"Simulated output for {workflow_id}",
                "input_processed": input_data
            }
            self.executions.append(execution)
            return execution

        session = await self._get_session()

        try:
            async with session.post(
                f"{self.credentials.host}/api/v1/workflows/{workflow_id}/execute",
                json={"data": input_data}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    execution.status = "success"
                    execution.output_data = data
                else:
                    execution.status = "error"
                    execution.error = await resp.text()
        except Exception as e:
            execution.status = "error"
            execution.error = str(e)

        execution.end_time = datetime.now()
        self.executions.append(execution)
        return execution

    async def get_workflow_status(self, workflow_id: str) -> dict:
        """Workflow durumunu al"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow bulunamadi"}

        executions = [
            e for e in self.executions
            if e.workflow_id == workflow_id
        ]

        return {
            "workflow": workflow.to_dict(),
            "total_executions": len(executions),
            "last_execution": executions[-1].to_dict() if executions else None
        }

    def create_llm_council_workflow(self, council_name: str) -> N8NWorkflow:
        """
        LLM Konseyi Workflow'u Olustur

        7 LLM'in sirayla veya paralel calismasi icin
        standart bir workflow sablonu.
        """
        nodes = [
            {
                "name": "Webhook Trigger",
                "type": "n8n-nodes-base.webhook",
                "position": [250, 300],
                "parameters": {
                    "path": f"council/{council_name}",
                    "method": "POST"
                }
            },
            {
                "name": "Claude Monk",
                "type": "n8n-nodes-base.httpRequest",
                "position": [450, 200],
                "parameters": {
                    "url": "{{$env.CLAUDE_API}}",
                    "method": "POST",
                    "body": {"prompt": "={{$json.input}}", "dimension": "ethics"}
                }
            },
            {
                "name": "Mistral Monk",
                "type": "n8n-nodes-base.httpRequest",
                "position": [450, 300],
                "parameters": {
                    "url": "{{$env.MISTRAL_API}}",
                    "method": "POST",
                    "body": {"prompt": "={{$json.input}}", "dimension": "logic"}
                }
            },
            {
                "name": "DeepSeek Monk",
                "type": "n8n-nodes-base.httpRequest",
                "position": [450, 400],
                "parameters": {
                    "url": "{{$env.DEEPSEEK_API}}",
                    "method": "POST",
                    "body": {"prompt": "={{$json.input}}", "dimension": "code"}
                }
            },
            {
                "name": "Vote Aggregator",
                "type": "n8n-nodes-base.function",
                "position": [650, 300],
                "parameters": {
                    "functionCode": """
                        const votes = items;
                        const avgConfidence = votes.reduce((a,b) => a + b.confidence, 0) / votes.length;
                        return [{
                            consensus: avgConfidence > 0.7,
                            result: votes.map(v => v.fold_result).join(' | '),
                            confidence: avgConfidence
                        }];
                    """
                }
            },
            {
                "name": "Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "position": [850, 300],
                "parameters": {}
            }
        ]

        workflow = N8NWorkflow(
            workflow_id=f"council_{council_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=f"LLM Council: {council_name}",
            description=f"7 LLM Voting Mantra workflow for {council_name}",
            trigger=WorkflowTrigger.WEBHOOK,
            nodes=nodes,
            is_active=True
        )

        return workflow

    def get_connector_stats(self) -> dict:
        """Connector istatistikleri"""
        success_count = len([e for e in self.executions if e.status == "success"])
        error_count = len([e for e in self.executions if e.status == "error"])

        return {
            "host": self.credentials.host,
            "simulated_mode": self._simulated,
            "workflows_registered": len(self.workflows),
            "total_executions": len(self.executions),
            "successful_executions": success_count,
            "failed_executions": error_count,
            "success_rate": success_count / max(1, len(self.executions))
        }


# Factory fonksiyonu
def create_prayer_wheel_connector(
    host: str = "http://localhost:5678",
    api_key: Optional[str] = None
) -> N8NConnector:
    """Prayer Wheel (N8N) connector olustur"""
    credentials = N8NCredentials(host=host, api_key=api_key)
    return N8NConnector(credentials)
