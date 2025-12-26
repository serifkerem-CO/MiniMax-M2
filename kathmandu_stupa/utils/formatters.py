"""
📜 FORMATTERS - Kehanet Formatlayıcıları
========================================

Veriyi "Kehanet Parşömeni" formatına dönüştürür.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ProphecyScroll:
    """Kehanet Parşömeni"""
    id: str
    title: str
    wisdom: str
    frequency_hz: int
    confidence: float
    source_chain: List[str]
    created_at: datetime

    def render(self) -> str:
        """ASCII art formatında render"""
        width = 70
        border = "═" * (width - 2)

        lines = [
            f"╔{border}╗",
            f"║  🌌 CAZIBE.IO - KEHANET PARŞÖMENİ{' ' * (width - 38)}║",
            f"╠{border}╣",
            f"║  ID: {self.id[:30]}{' ' * (width - 37 - min(30, len(self.id)))}║",
            f"║  Frekans: {self.frequency_hz} Hz | Güven: {self.confidence:.1%}{' ' * (width - 40)}║",
            f"╠{border}╣",
            f"║  BİLGELİK:{' ' * (width - 13)}║",
        ]

        # Wisdom'u satırlara böl
        wisdom_lines = self._wrap_text(self.wisdom, width - 6)
        for line in wisdom_lines[:5]:  # Max 5 satır
            padded = line + " " * (width - 4 - len(line))
            lines.append(f"║  {padded}║")

        if len(wisdom_lines) > 5:
            lines.append(f"║  {'...' + ' ' * (width - 7)}║")

        lines.extend([
            f"╠{border}╣",
            f"║  Kaynak: {' -> '.join(self.source_chain[:3])[:50]}{' ' * (width - 61)}║",
            f"║  Tarih: {self.created_at.strftime('%Y-%m-%d %H:%M')}{' ' * (width - 30)}║",
            f"╚{border}╝",
        ])

        return "\n".join(lines)

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Metni satırlara sar"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return lines


class ProphecyFormatter:
    """
    📜 Kehanet Formatlayıcı

    Farklı çıktı formatları için dönüştürücü.
    """

    @staticmethod
    def to_scroll(data: Dict) -> ProphecyScroll:
        """Dict'ten Scroll'a dönüştür"""
        return ProphecyScroll(
            id=data.get("id", f"SCROLL_{datetime.now().timestamp()}"),
            title=data.get("title", "Kehanet"),
            wisdom=data.get("wisdom", data.get("content", "")),
            frequency_hz=data.get("frequency_hz", 963),
            confidence=data.get("confidence", 0.8),
            source_chain=data.get("source_chain", ["UNKNOWN"]),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
        )

    @staticmethod
    def to_json(scroll: ProphecyScroll) -> Dict:
        """Scroll'dan JSON'a"""
        return {
            "id": scroll.id,
            "title": scroll.title,
            "wisdom": scroll.wisdom,
            "frequency_hz": scroll.frequency_hz,
            "confidence": scroll.confidence,
            "source_chain": scroll.source_chain,
            "created_at": scroll.created_at.isoformat(),
        }

    @staticmethod
    def to_markdown(scroll: ProphecyScroll) -> str:
        """Markdown formatı"""
        return f"""
# 🌌 {scroll.title}

**ID:** `{scroll.id}`
**Frekans:** {scroll.frequency_hz} Hz
**Güven:** {scroll.confidence:.1%}

## Bilgelik

> {scroll.wisdom}

---

**Kaynak Zinciri:** {' → '.join(scroll.source_chain)}
**Oluşturulma:** {scroll.created_at.strftime('%Y-%m-%d %H:%M:%S')}
"""

    @staticmethod
    def to_html(scroll: ProphecyScroll) -> str:
        """HTML formatı"""
        return f"""
<div class="prophecy-scroll" style="
    background: linear-gradient(135deg, #1a0a2e, #0d0015);
    border: 2px solid #ffd700;
    border-radius: 15px;
    padding: 20px;
    color: #e0d4f7;
    font-family: serif;
    max-width: 600px;
    margin: 20px auto;
">
    <h2 style="color: #ffd700; text-align: center;">🌌 {scroll.title}</h2>
    <div style="
        background: rgba(0,0,0,0.3);
        padding: 15px;
        border-left: 3px solid #ffd700;
        margin: 15px 0;
        font-style: italic;
    ">
        {scroll.wisdom}
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 0.9em;">
        <span>🎵 {scroll.frequency_hz} Hz</span>
        <span>📊 {scroll.confidence:.1%}</span>
    </div>
    <div style="margin-top: 15px; font-size: 0.8em; color: #9370db;">
        Kaynak: {' → '.join(scroll.source_chain)}
    </div>
</div>
"""


def create_scroll(
    wisdom: str,
    frequency_hz: int = 963,
    confidence: float = 0.85,
    source_chain: Optional[List[str]] = None
) -> ProphecyScroll:
    """Hızlı scroll oluşturma"""
    return ProphecyScroll(
        id=f"SCROLL_{int(datetime.now().timestamp())}",
        title="Kehanet Parşömeni",
        wisdom=wisdom,
        frequency_hz=frequency_hz,
        confidence=confidence,
        source_chain=source_chain or ["KATHMANDU_STUPA"],
        created_at=datetime.now(),
    )


# Demo
if __name__ == "__main__":
    scroll = create_scroll(
        wisdom="Türkiye sanayisi için bu kriz değil, bir dönüşüm fırsatıdır. "
               "Veriler gösteriyor ki dijitalleşme oranı %47'ye ulaştı.",
        source_chain=["TOPRAK", "SU", "ATEŞ", "HAVA", "ETER"],
    )

    print(scroll.render())
    print("\n" + "=" * 70 + "\n")
    print(ProphecyFormatter.to_markdown(scroll))
