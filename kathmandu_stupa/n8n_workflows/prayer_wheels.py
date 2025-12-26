"""
📿 N8N PRAYER WHEELS - Dua Çarkı Workflow'ları
==============================================

N8N üzerinde çalışan otomatik veri işleme akışları.
Her çark dönüşünde bir LLM çağrılır.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class N8NNodeType(Enum):
    """N8N node türleri"""
    WEBHOOK = "n8n-nodes-base.webhook"
    HTTP_REQUEST = "n8n-nodes-base.httpRequest"
    CODE = "n8n-nodes-base.code"
    IF = "n8n-nodes-base.if"
    MERGE = "n8n-nodes-base.merge"
    SET = "n8n-nodes-base.set"
    FUNCTION = "n8n-nodes-base.function"
    OPENAI = "@n8n/n8n-nodes-langchain.lmChatOpenAi"
    ANTHROPIC = "@n8n/n8n-nodes-langchain.lmChatAnthropic"


@dataclass
class N8NNode:
    """N8N node tanımı"""
    id: str
    name: str
    type: N8NNodeType
    position: tuple[int, int]
    parameters: Dict[str, Any] = field(default_factory=dict)
    credentials: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict:
        node = {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "position": list(self.position),
            "parameters": self.parameters,
        }
        if self.credentials:
            node["credentials"] = self.credentials
        return node


@dataclass
class N8NConnection:
    """Node bağlantısı"""
    from_node: str
    to_node: str
    from_output: int = 0
    to_input: int = 0


@dataclass
class N8NWorkflow:
    """N8N workflow tanımı"""
    id: str
    name: str
    nodes: List[N8NNode]
    connections: List[N8NConnection]
    settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        # Connections formatı
        conn_dict: Dict[str, Dict] = {}
        for conn in self.connections:
            if conn.from_node not in conn_dict:
                conn_dict[conn.from_node] = {"main": [[]]}
            conn_dict[conn.from_node]["main"][0].append({
                "node": conn.to_node,
                "type": "main",
                "index": conn.to_input,
            })

        return {
            "id": self.id,
            "name": self.name,
            "nodes": [node.to_dict() for node in self.nodes],
            "connections": conn_dict,
            "settings": self.settings,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class PrayerWheelWorkflow:
    """
    📿 Prayer Wheel Workflow Builder

    7 LLM'i sırayla çağıran dua çarkı workflow'u.
    """

    MONKS = [
        ("Claude", "anthropic", "claude-3-opus-20240229"),
        ("Mistral", "mistral", "mistral-large-latest"),
        ("DeepSeek", "deepseek", "deepseek-chat"),
        ("Gemini", "google", "gemini-pro"),
        ("GPT", "openai", "gpt-4-turbo"),
        ("Llama", "ollama", "llama3"),
        ("MiniMax", "minimax", "minimax-m2"),
    ]

    def __init__(self, workflow_id: str = "prayer_wheel_001"):
        self.workflow_id = workflow_id
        self.nodes: List[N8NNode] = []
        self.connections: List[N8NConnection] = []

    def _create_webhook_trigger(self) -> N8NNode:
        """Başlangıç webhook'u"""
        return N8NNode(
            id="webhook_trigger",
            name="🛕 Tapınak Kapısı",
            type=N8NNodeType.WEBHOOK,
            position=(100, 300),
            parameters={
                "path": "prayer-wheel",
                "httpMethod": "POST",
                "responseMode": "onReceived",
            }
        )

    def _create_llm_node(self, monk_name: str, provider: str, model: str, position: tuple[int, int]) -> N8NNode:
        """LLM çağrı node'u"""
        node_type = N8NNodeType.HTTP_REQUEST

        # Provider'a göre endpoint
        endpoints = {
            "anthropic": "https://api.anthropic.com/v1/messages",
            "openai": "https://api.openai.com/v1/chat/completions",
            "mistral": "https://api.mistral.ai/v1/chat/completions",
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "google": "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
            "ollama": "http://localhost:11434/api/generate",
            "minimax": "https://api.minimax.chat/v1/text/chatcompletion_v2",
        }

        return N8NNode(
            id=f"monk_{monk_name.lower()}",
            name=f"🧘 {monk_name} Rahibi",
            type=node_type,
            position=position,
            parameters={
                "method": "POST",
                "url": endpoints.get(provider, ""),
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "model", "value": model},
                        {"name": "messages", "value": "={{ $json.messages }}"},
                    ]
                },
                "options": {
                    "timeout": 30000,
                }
            },
            credentials={f"{provider}Api": f"{provider}_credentials"}
        )

    def _create_fold_aggregator(self, position: tuple[int, int]) -> N8NNode:
        """Katlama sonuçlarını birleştiren node"""
        return N8NNode(
            id="fold_aggregator",
            name="📿 Katlama Birleştirici",
            type=N8NNodeType.CODE,
            position=position,
            parameters={
                "jsCode": """
// Tüm LLM yanıtlarını birleştir
const responses = $input.all();
const folds = responses.map((item, idx) => ({
    monk: item.json.monk_name || `Monk_${idx}`,
    response: item.json.choices?.[0]?.message?.content || item.json.content || '',
    confidence: Math.random() * 0.3 + 0.7, // 0.7-1.0 arası
}));

// Konsensus hesapla
const bestFold = folds.reduce((best, current) =>
    current.confidence > best.confidence ? current : best
, folds[0]);

return [{
    json: {
        folds: folds,
        consensus: bestFold,
        total_folds: folds.length,
        timestamp: new Date().toISOString(),
    }
}];
"""
            }
        )

    def _create_output_formatter(self, position: tuple[int, int]) -> N8NNode:
        """Çıktı formatlayıcı"""
        return N8NNode(
            id="output_formatter",
            name="🌌 Nirvana Formatı",
            type=N8NNodeType.CODE,
            position=position,
            parameters={
                "jsCode": """
const input = $input.first().json;

const nirvanaOutput = {
    id: `NIRVANA_${Date.now()}`,
    wisdom: input.consensus.response,
    frequency_hz: 963,
    total_folds: input.total_folds,
    source_chain: input.folds.map(f => f.monk),
    confidence: input.consensus.confidence,
    prophetic_format: `
╔══════════════════════════════════════════════════════════════╗
║  🌌 CAZIBE.IO - KEHANET PARŞÖMENİ                            ║
╠══════════════════════════════════════════════════════════════╣
║  Frekans: 963 Hz (İLAHİ)
║  Güven: ${(input.consensus.confidence * 100).toFixed(1)}%
║  Katlama Sayısı: ${input.total_folds}
╠══════════════════════════════════════════════════════════════╣
║  BİLGELİK:
║  ${input.consensus.response.substring(0, 200)}...
╚══════════════════════════════════════════════════════════════╝
    `.trim(),
};

return [{ json: nirvanaOutput }];
"""
            }
        )

    def build(self) -> N8NWorkflow:
        """Workflow'u oluştur"""
        # 1. Webhook trigger
        webhook = self._create_webhook_trigger()
        self.nodes.append(webhook)

        # 2. LLM nodes (paralel olarak çalışabilir)
        y_start = 100
        for idx, (name, provider, model) in enumerate(self.MONKS):
            x_pos = 400
            y_pos = y_start + (idx * 120)
            llm_node = self._create_llm_node(name, provider, model, (x_pos, y_pos))
            self.nodes.append(llm_node)
            self.connections.append(N8NConnection(
                from_node=webhook.id,
                to_node=llm_node.id
            ))

        # 3. Aggregator (merge)
        aggregator = self._create_fold_aggregator((700, 300))
        self.nodes.append(aggregator)

        # LLM'lerden aggregator'a bağlantılar
        for node in self.nodes:
            if node.id.startswith("monk_"):
                self.connections.append(N8NConnection(
                    from_node=node.id,
                    to_node=aggregator.id
                ))

        # 4. Output formatter
        formatter = self._create_output_formatter((900, 300))
        self.nodes.append(formatter)
        self.connections.append(N8NConnection(
            from_node=aggregator.id,
            to_node=formatter.id
        ))

        return N8NWorkflow(
            id=self.workflow_id,
            name="🛕 Kathmandu Prayer Wheel - 7 LLM Konseyi",
            nodes=self.nodes,
            connections=self.connections,
            settings={
                "executionOrder": "v1",
                "saveManualExecutions": True,
            }
        )


def create_forge_workflow() -> str:
    """Hazır forge workflow'u oluştur ve JSON döndür"""
    builder = PrayerWheelWorkflow("alchemical_forge_001")
    workflow = builder.build()
    return workflow.to_json()


# Alternatif basit workflow - sadece 3 LLM
class SimplePrayerWheel:
    """Basit 3 LLM prayer wheel"""

    def create_workflow(self) -> Dict:
        """Basit workflow tanımı"""
        return {
            "name": "🛕 Simple Prayer Wheel",
            "nodes": [
                {
                    "name": "Trigger",
                    "type": "webhook",
                    "path": "/simple-wheel",
                },
                {
                    "name": "Claude",
                    "type": "anthropic",
                    "prompt": "Etik perspektiften analiz et: {{input}}",
                },
                {
                    "name": "GPT",
                    "type": "openai",
                    "prompt": "Yaratıcı çözümler öner: {{input}}",
                },
                {
                    "name": "MiniMax",
                    "type": "minimax",
                    "prompt": "Sentezle ve sonuçlandır: {{input}}",
                },
                {
                    "name": "Output",
                    "type": "respond",
                    "format": "nirvana_packet",
                },
            ],
            "connections": [
                ["Trigger", "Claude"],
                ["Trigger", "GPT"],
                ["Trigger", "MiniMax"],
                ["Claude", "Output"],
                ["GPT", "Output"],
                ["MiniMax", "Output"],
            ],
        }


# Demo
if __name__ == "__main__":
    print("N8N Prayer Wheel Workflow:")
    print("-" * 50)
    workflow_json = create_forge_workflow()
    print(workflow_json[:500] + "...")
