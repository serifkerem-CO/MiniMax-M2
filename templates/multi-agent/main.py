"""
MiniMax-M2 Multi-Agent Sistem Şablonu
=====================================
Birden fazla uzman ajanın birlikte çalıştığı sistem.

Bu şablon, farklı uzmanlık alanlarına sahip ajanların
koordineli şekilde görev tamamlamasını sağlar.

Gereksinimler:
    pip install openai

Kullanım:
    python main.py
"""

import os
import json
from typing import Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from openai import OpenAI

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)


# ============================================================================
# Temel Yapılar
# ============================================================================

class AgentRole(Enum):
    """Ajan rolleri."""
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"
    WRITER = "writer"
    COORDINATOR = "coordinator"


@dataclass
class Message:
    """Ajanlar arası mesaj."""
    sender: str
    receiver: str
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class Task:
    """Görev tanımı."""
    id: str
    description: str
    assigned_to: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None
    subtasks: list = field(default_factory=list)


# ============================================================================
# Temel Ajan Sınıfı
# ============================================================================

class BaseAgent(ABC):
    """Temel ajan sınıfı."""

    def __init__(
        self,
        name: str,
        role: AgentRole,
        system_prompt: str,
        temperature: float = 0.7
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.memory: list[Message] = []

    def think(self, prompt: str, context: Optional[str] = None) -> str:
        """Düşün ve yanıt üret."""
        messages = [{"role": "system", "content": self.system_prompt}]

        if context:
            messages.append({"role": "user", "content": f"Bağlam:\n{context}"})

        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=self.temperature,
            max_tokens=2048,
        )

        return response.choices[0].message.content

    def receive_message(self, message: Message):
        """Mesaj al."""
        self.memory.append(message)

    def send_message(self, receiver: str, content: str) -> Message:
        """Mesaj gönder."""
        message = Message(sender=self.name, receiver=receiver, content=content)
        return message

    @abstractmethod
    def execute(self, task: Task) -> str:
        """Görevi çalıştır."""
        pass


# ============================================================================
# Uzman Ajanlar
# ============================================================================

class PlannerAgent(BaseAgent):
    """Planlama ajanı - görevleri alt görevlere böler."""

    def __init__(self):
        super().__init__(
            name="Planlayıcı",
            role=AgentRole.PLANNER,
            system_prompt="""Sen deneyimli bir proje planlayıcısısın.
Görevin: Verilen hedefi analiz et ve somut, uygulanabilir adımlara böl.

Her adım için:
1. Net ve özlü bir açıklama yaz
2. Hangi uzmanlık alanı gerektiğini belirt (researcher, coder, writer, reviewer)
3. Bağımlılıkları belirt

JSON formatında döndür:
{
    "analysis": "Genel analiz",
    "steps": [
        {"id": 1, "task": "Açıklama", "assignee": "rol", "depends_on": []}
    ]
}""",
            temperature=0.3
        )

    def execute(self, task: Task) -> str:
        result = self.think(f"Bu hedef için plan oluştur:\n{task.description}")
        return result


class ResearcherAgent(BaseAgent):
    """Araştırma ajanı - bilgi toplar."""

    def __init__(self):
        super().__init__(
            name="Araştırmacı",
            role=AgentRole.RESEARCHER,
            system_prompt="""Sen uzman bir araştırmacısın.
Görevin: Verilen konu hakkında kapsamlı bilgi topla ve özetle.

Yanıtın şunları içermeli:
1. Konunun özeti
2. Önemli noktalar
3. İlgili kavramlar
4. Kaynaklar ve referanslar

Bilimsel ve objektif ol.""",
            temperature=0.5
        )

    def execute(self, task: Task) -> str:
        result = self.think(f"Bu konuyu araştır:\n{task.description}")
        return result


class CoderAgent(BaseAgent):
    """Kodlama ajanı - kod yazar."""

    def __init__(self):
        super().__init__(
            name="Geliştirici",
            role=AgentRole.CODER,
            system_prompt="""Sen uzman bir yazılım geliştiricisisin.
Görevin: Temiz, okunabilir ve iyi belgelenmiş kod yaz.

Kod yazarken:
1. En iyi pratikleri uygula
2. Hata yönetimi ekle
3. Yorumlar ekle
4. Test edilebilir kod yaz

Markdown kod blokları kullan.""",
            temperature=0.2
        )

    def execute(self, task: Task) -> str:
        result = self.think(f"Bu özelliği kodla:\n{task.description}")
        return result


class ReviewerAgent(BaseAgent):
    """İnceleme ajanı - kod ve içerik inceler."""

    def __init__(self):
        super().__init__(
            name="İnceleyici",
            role=AgentRole.REVIEWER,
            system_prompt="""Sen deneyimli bir kod ve içerik inceleyicisisin.
Görevin: Verilen içeriği kritik gözle incele.

İnceleme kriterleri:
1. Doğruluk
2. Kalite
3. En iyi pratikler
4. Güvenlik
5. Performans

Yapıcı geri bildirim ver ve iyileştirme önerileri sun.""",
            temperature=0.3
        )

    def execute(self, task: Task) -> str:
        result = self.think(f"Bu içeriği incele:\n{task.description}")
        return result


class WriterAgent(BaseAgent):
    """Yazı ajanı - dokümantasyon ve içerik yazar."""

    def __init__(self):
        super().__init__(
            name="Yazar",
            role=AgentRole.WRITER,
            system_prompt="""Sen profesyonel bir teknik yazarsın.
Görevin: Net, anlaşılır ve iyi yapılandırılmış içerik yaz.

Yazarken:
1. Hedef kitleyi düşün
2. Açık ve öz ol
3. Örnekler kullan
4. Düzgün formatla

Markdown kullan.""",
            temperature=0.6
        )

    def execute(self, task: Task) -> str:
        result = self.think(f"Bu içeriği yaz:\n{task.description}")
        return result


# ============================================================================
# Koordinatör
# ============================================================================

class Coordinator:
    """Ajanları koordine eden ana sınıf."""

    def __init__(self):
        self.agents: dict[str, BaseAgent] = {
            "planner": PlannerAgent(),
            "researcher": ResearcherAgent(),
            "coder": CoderAgent(),
            "reviewer": ReviewerAgent(),
            "writer": WriterAgent(),
        }
        self.messages: list[Message] = []
        self.tasks: list[Task] = []

    def delegate_task(self, task: Task, agent_name: str) -> str:
        """Görevi ilgili ajana delege et."""
        if agent_name not in self.agents:
            return f"Hata: '{agent_name}' ajanı bulunamadı."

        agent = self.agents[agent_name]
        task.assigned_to = agent_name
        task.status = "in_progress"

        print(f"📋 Görev {agent.name}'a atandı: {task.description[:50]}...")

        result = agent.execute(task)

        task.status = "completed"
        task.result = result

        return result

    def run_pipeline(self, goal: str) -> dict:
        """
        Tam pipeline çalıştır.

        1. Planlayıcı hedefi analiz eder
        2. Her adım için uygun ajan çalışır
        3. İnceleyici sonuçları kontrol eder
        4. Sonuç raporlanır
        """
        print(f"\n{'='*60}")
        print(f"🎯 Hedef: {goal}")
        print(f"{'='*60}\n")

        results = {
            "goal": goal,
            "steps": [],
            "final_output": ""
        }

        # Adım 1: Planlama
        print("📝 Adım 1: Planlama...")
        plan_task = Task(id="plan", description=goal)
        plan_result = self.delegate_task(plan_task, "planner")
        results["plan"] = plan_result

        # JSON planı parse et
        try:
            # JSON bloğunu bul
            if "```json" in plan_result:
                json_str = plan_result.split("```json")[1].split("```")[0]
            elif "```" in plan_result:
                json_str = plan_result.split("```")[1].split("```")[0]
            else:
                json_str = plan_result

            plan = json.loads(json_str)
            steps = plan.get("steps", [])
        except (json.JSONDecodeError, IndexError):
            print("⚠️ Plan parse edilemedi, varsayılan adımlar kullanılıyor.")
            steps = [
                {"id": 1, "task": goal, "assignee": "coder", "depends_on": []}
            ]

        # Adım 2: Her adımı çalıştır
        step_results = []
        for i, step in enumerate(steps):
            step_id = step.get("id", i + 1)
            step_task = step.get("task", "")
            assignee = step.get("assignee", "coder")

            print(f"\n🔄 Adım {step_id}: {step_task[:50]}...")

            task = Task(id=f"step_{step_id}", description=step_task)

            # Önceki sonuçları bağlam olarak ekle
            if step_results:
                context = "\n\n".join([f"Önceki sonuç:\n{r}" for r in step_results[-2:]])
                task.description = f"{step_task}\n\nBağlam:\n{context}"

            result = self.delegate_task(task, assignee)
            step_results.append(result)

            results["steps"].append({
                "step_id": step_id,
                "task": step_task,
                "assignee": assignee,
                "result": result
            })

        # Adım 3: İnceleme
        print("\n🔍 Son Adım: İnceleme...")
        review_content = "\n\n---\n\n".join(step_results)
        review_task = Task(
            id="review",
            description=f"Bu sonuçları incele ve genel değerlendirme yap:\n\n{review_content}"
        )
        review_result = self.delegate_task(review_task, "reviewer")
        results["review"] = review_result

        # Sonuç özeti
        results["final_output"] = step_results[-1] if step_results else ""

        print(f"\n{'='*60}")
        print("✅ Pipeline tamamlandı!")
        print(f"{'='*60}\n")

        return results

    def interactive_mode(self):
        """İnteraktif mod."""
        print("\n" + "="*60)
        print("🤖 Multi-Agent Sistem - İnteraktif Mod")
        print("="*60)
        print("\nKomutlar:")
        print("  /goal <hedef>  - Tam pipeline çalıştır")
        print("  /ask <ajan> <soru> - Belirli ajana sor")
        print("  /agents - Ajanları listele")
        print("  /quit - Çık")
        print()

        while True:
            try:
                user_input = input(">>> ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if not user_input:
                continue

            if user_input.startswith("/quit"):
                break
            elif user_input.startswith("/agents"):
                for name, agent in self.agents.items():
                    print(f"  - {agent.name} ({name}): {agent.role.value}")
            elif user_input.startswith("/goal "):
                goal = user_input[6:]
                results = self.run_pipeline(goal)
                print("\n📊 Sonuç Özeti:")
                print(results.get("review", "Sonuç yok"))
            elif user_input.startswith("/ask "):
                parts = user_input[5:].split(" ", 1)
                if len(parts) == 2:
                    agent_name, question = parts
                    if agent_name in self.agents:
                        task = Task(id="ask", description=question)
                        result = self.delegate_task(task, agent_name)
                        print(f"\n{result}")
                    else:
                        print(f"Ajan bulunamadı: {agent_name}")
                else:
                    print("Kullanım: /ask <ajan> <soru>")
            else:
                # Varsayılan: Tam pipeline
                results = self.run_pipeline(user_input)
                print("\n📊 Sonuç:")
                print(results.get("final_output", "Sonuç yok")[:500])

        print("\nGüle güle!")


# ============================================================================
# Demo
# ============================================================================

def demo():
    """Demo senaryosu."""
    coordinator = Coordinator()

    # Örnek hedef
    goal = """
    Bir Python web API tasarla ve dokümante et.
    API, kullanıcı kaydı ve giriş işlemlerini yönetmeli.
    JWT token kullanmalı.
    """

    results = coordinator.run_pipeline(goal)

    print("\n" + "="*60)
    print("📊 SONUÇ RAPORU")
    print("="*60)

    print("\n🎯 Hedef:")
    print(goal)

    print("\n📋 Plan:")
    print(results.get("plan", "")[:500])

    print("\n🔧 Adımlar:")
    for step in results.get("steps", []):
        print(f"\n--- Adım {step['step_id']} ({step['assignee']}) ---")
        print(step["result"][:300] + "...")

    print("\n🔍 İnceleme:")
    print(results.get("review", ""))


# ============================================================================
# Ana Giriş
# ============================================================================

def main():
    """Ana fonksiyon."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        coordinator = Coordinator()
        coordinator.interactive_mode()


if __name__ == "__main__":
    main()
