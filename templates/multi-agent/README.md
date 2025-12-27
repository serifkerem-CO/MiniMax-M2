# MiniMax-M2 Multi-Agent Sistem Şablonu

Birden fazla uzman ajanın koordineli çalıştığı sistem.

## Özellikler

- **5 Uzman Ajan**: Planlayıcı, Araştırmacı, Geliştirici, İnceleyici, Yazar
- **Otomatik Koordinasyon**: Görev dağılımı ve sonuç birleştirme
- **Pipeline Modu**: Tam iş akışı otomasyonu
- **İnteraktif Mod**: Manuel ajan etkileşimi

## Ajanlar

| Ajan | Rol | Görev |
|------|-----|-------|
| Planlayıcı | planner | Hedefi alt görevlere böler |
| Araştırmacı | researcher | Bilgi toplar ve özetler |
| Geliştirici | coder | Kod yazar |
| İnceleyici | reviewer | Sonuçları inceler |
| Yazar | writer | Dokümantasyon yazar |

## Kullanım

### Demo Modu
```bash
python main.py --demo
```

### İnteraktif Mod
```bash
python main.py
```

### Komutlar
```
/goal <hedef>      - Tam pipeline çalıştır
/ask <ajan> <soru> - Belirli ajana sor
/agents            - Ajanları listele
/quit              - Çık
```

## Pipeline Akışı

```
┌─────────────┐
│   Hedef     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Planlayıcı │ ──▶ Alt görevlere böl
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Araştırmacı │ ──▶ Bilgi topla
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Geliştirici │ ──▶ Kod yaz
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Yazar     │ ──▶ Dokümante et
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ İnceleyici  │ ──▶ Son kontrol
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Sonuç     │
└─────────────┘
```

## Özelleştirme

### Yeni Ajan Ekleme

```python
class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Özel Ajan",
            role=AgentRole.CUSTOM,
            system_prompt="...",
            temperature=0.5
        )

    def execute(self, task: Task) -> str:
        return self.think(task.description)

# Koordinatöre ekle
coordinator.agents["custom"] = CustomAgent()
```

### Özel Pipeline

```python
coordinator = Coordinator()

# Sadece araştırma + yazma
result1 = coordinator.delegate_task(task1, "researcher")
result2 = coordinator.delegate_task(task2, "writer")
```

## Örnek Senaryolar

### Web API Geliştirme
```
/goal Kullanıcı yönetimi için REST API tasarla
```

### Kod Analizi
```
/goal Bu kodu analiz et ve dokümante et: [kod]
```

### Araştırma
```
/ask researcher Mikroservis mimarisinin avantajları
```
