"""
MODULllm.com - Orchestration Engine
11 Akıl Harmanlar + 12. Akıl Sentez Sistemi

"Öz Kodundan Doğan Güç!"
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import httpx
from datetime import datetime


class AkilTipi(str, Enum):
    """11 Akıl Harmanları Tipleri"""
    TEKNIK = "teknik"           # 1. Akıl - Teknik analiz
    YARATICI = "yaratici"       # 2. Akıl - Yaratıcı düşünce
    ELESTREL = "elestrel"       # 3. Akıl - Eleştirel bakış
    PRAGMATIK = "pragmatik"     # 4. Akıl - Pratik çözüm
    VIZYONER = "vizyoner"       # 5. Akıl - Uzun vadeli vizyon
    ANALITIK = "analitik"       # 6. Akıl - Derin analiz
    SEZGISEL = "sezgisel"       # 7. Akıl - Sezgisel yaklaşım
    SISTEMATIK = "sistematik"   # 8. Akıl - Sistemsel düşünce
    DENEYSEL = "deneysel"       # 9. Akıl - Deneysel metod
    FELSEFI = "felsefi"         # 10. Akıl - Felsefi derinlik
    SENTETIK = "sentetik"       # 11. Akıl - Sentez öncüsü
    # 12. Akıl - Sentez (ayrı sistem)


@dataclass
class AkilYaniti:
    """Bir Akıl'ın yanıtı"""
    akil_tipi: AkilTipi
    yanitlayan: str  # Model adı
    icerik: str
    perspektif: str  # Bu akıl hangi açıdan baktı
    guven_skoru: float  # 0-1 arası
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class SentezYaniti:
    """12. Akıl'ın sentez yanıtı"""
    sentez: str
    kullanilan_akillar: List[AkilTipi]
    guven_skoru: float
    ic_goruler: List[str]  # Her akildan çıkan önemli noktalar
    oneriler: List[str]
    timestamp: datetime


class OrchestratorConfig:
    """Orchestrator ayarları"""
    def __init__(self):
        # LLM Endpoints (Self-hosted on DEAVAEM Gemi)
        self.llm_endpoints = {
            "minimax": "http://gemi.modulllm.com:8000/v1",
            "local_llm_1": "http://localhost:11434/api",  # Ollama
            "local_llm_2": "http://localhost:5000/v1",    # vLLM
            # Eklenecek: Gemideki diğer self-hosted LLM'ler
        }

        # Öz Veritabanı
        self.oz_db_endpoint = "http://modulllm.com/api/ozdb"

        # 11 Akıl mapping (hangi model hangi Akıl'ı oynar)
        self.akil_model_mapping = {
            AkilTipi.TEKNIK: "minimax",
            AkilTipi.YARATICI: "local_llm_1",
            AkilTipi.ELESTREL: "minimax",
            AkilTipi.PRAGMATIK: "local_llm_2",
            AkilTipi.VIZYONER: "minimax",
            AkilTipi.ANALITIK: "local_llm_1",
            AkilTipi.SEZGISEL: "local_llm_2",
            AkilTipi.SISTEMATIK: "minimax",
            AkilTipi.DENEYSEL: "local_llm_1",
            AkilTipi.FELSEFI: "local_llm_2",
            AkilTipi.SENTETIK: "minimax",
        }

        # 12. Akıl (Sentez)
        self.sentez_model = "minimax"  # En güçlü model sentez yapar

        # Timeout ayarları
        self.timeout = 30
        self.max_retries = 3


class OzKodOrchestrator:
    """
    MODULllm.com Orchestration Engine

    11 Akıl Harmanları + 12. Akıl Sentezi
    Sadece öz veritabanımızı kullanır!
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self.client = httpx.AsyncClient(timeout=self.config.timeout)

    async def _query_oz_db(self, soru: str) -> Dict[str, Any]:
        """Öz veritabanımızdan ilgili içeriği çek"""
        try:
            response = await self.client.post(
                self.config.oz_db_endpoint + "/search",
                json={"query": soru, "limit": 11}  # 11 en alakalı içerik
            )
            return response.json()
        except Exception as e:
            print(f"⚠️ Öz DB query hatası: {e}")
            return {"results": [], "context": ""}

    async def _query_single_akil(
        self,
        akil_tipi: AkilTipi,
        soru: str,
        oz_context: str
    ) -> AkilYaniti:
        """Tek bir Akıl'a soru sor"""
        model_key = self.config.akil_model_mapping[akil_tipi]
        endpoint = self.config.llm_endpoints[model_key]

        # Her Akıl'ın özel perspektifi
        perspektif_prompts = {
            AkilTipi.TEKNIK: "Teknik ve mühendislik açısından değerlendir",
            AkilTipi.YARATICI: "Yaratıcı ve yenilikçi açılardan yaklaş",
            AkilTipi.ELESTREL: "Eleştirel ve analitik bir bakış sun",
            AkilTipi.PRAGMATIK: "Pratik ve uygulanabilir çözümler öner",
            AkilTipi.VIZYONER: "Uzun vadeli vizyon ve geleceği değerlendir",
            AkilTipi.ANALITIK: "Derin veri analizi ve metriklerle yaklaş",
            AkilTipi.SEZGISEL: "Sezgisel ve deneyim bazlı düşün",
            AkilTipi.SISTEMATIK: "Sistemsel ve yapısal bir çerçeve sun",
            AkilTipi.DENEYSEL: "Deneysel ve test edilebilir hipotezler kur",
            AkilTipi.FELSEFI: "Felsefi derinlik ve temel prensiplerden bak",
            AkilTipi.SENTETIK: "Farklı bakış açılarını birleştir",
        }

        system_prompt = f"""Sen MODULllm.com platformunun {akil_tipi.value.upper()} Akıl'ısın.
{perspektif_prompts[akil_tipi]}.

ÖNEMLİ: Sadece aşağıdaki MODULllm.com öz veritabanı içeriğini kullan:
{oz_context}

Dış kaynak kullanma, sadece öz kodumuzdan doğan bilgiyi kullan!"""

        try:
            # LLM'e query gönder
            response = await self.client.post(
                f"{endpoint}/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": soru}
                    ],
                    "temperature": 0.7 if akil_tipi in [AkilTipi.YARATICI, AkilTipi.SEZGISEL] else 0.5,
                }
            )

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            return AkilYaniti(
                akil_tipi=akil_tipi,
                yanitlayan=model_key,
                icerik=content,
                perspektif=perspektif_prompts[akil_tipi],
                guven_skoru=0.8,  # TODO: Gerçek güven skoru hesapla
                timestamp=datetime.now(),
                metadata={"endpoint": endpoint}
            )

        except Exception as e:
            print(f"⚠️ {akil_tipi.value} Akıl hatası: {e}")
            return AkilYaniti(
                akil_tipi=akil_tipi,
                yanitlayan=model_key,
                icerik=f"[Hata: {akil_tipi.value} Akıl şu an yanıt veremiyor]",
                perspektif=perspektif_prompts[akil_tipi],
                guven_skoru=0.0,
                timestamp=datetime.now(),
                metadata={"error": str(e)}
            )

    async def on_bir_akil_harmanla(self, soru: str) -> List[AkilYaniti]:
        """
        11 Akıl Harmanları'na paralel soru sor
        Sadece öz veritabanımızı kullanarak!
        """
        print(f"\n🧠 11 Akıl Harmanları devrede... Soru: {soru}\n")

        # 1. Önce öz veritabanından context çek
        oz_context_data = await self._query_oz_db(soru)
        oz_context = oz_context_data.get("context", "Henüz veri yok - ilk sorgu!")

        print(f"📚 Öz veritabanından {len(oz_context_data.get('results', []))} sonuç bulundu\n")

        # 2. 11 Akıl'a paralel olarak sor
        tasks = []
        for akil_tipi in AkilTipi:
            if akil_tipi != AkilTipi.SENTETIK:  # SENTETIK ayrı çalışır
                task = self._query_single_akil(akil_tipi, soru, oz_context)
                tasks.append(task)

        # 3. Tüm yanıtları topla
        yanitlar = await asyncio.gather(*tasks)

        print(f"✅ 11 Akıl Harmanları tamamlandı!\n")

        return yanitlar

    async def on_ikinci_akil_sentezle(
        self,
        soru: str,
        akil_yanitlari: List[AkilYaniti]
    ) -> SentezYaniti:
        """
        12. Akıl: 11 Akıl'ın yanıtlarını sentezler
        """
        print(f"\n⚡ 12. Akıl sentez yapıyor...\n")

        # 11 Akıl'dan gelen önemli noktaları çıkar
        ic_goruler = []
        akillar_ozeti = ""

        for yanit in akil_yanitlari:
            if yanit.guven_skoru > 0.5:  # Sadece güvenilir yanıtları al
                ic_goruler.append(f"{yanit.akil_tipi.value}: {yanit.icerik[:200]}...")
                akillar_ozeti += f"\n### {yanit.akil_tipi.value.upper()} Akıl:\n{yanit.icerik}\n"

        # 12. Akıl'a sentez yaptır
        sentez_prompt = f"""Sen MODULllm.com'un 12. Akıl'ısın - SENTEZ USTASISIN!

11 Akıl Harmanları'ndan gelen yanıtları sentezle ve özgün bir cevap üret.

ORİJİNAL SORU:
{soru}

11 AKIL HARMANLARI'NDAN GELEN YANITLAR:
{akillar_ozeti}

GÖREVİN:
1. Tüm Akıllardan gelen bilgiyi harmanlayıp sentezle
2. En değerli içgörüleri çıkar
3. Özgün, kapsamlı bir cevap üret
4. Pratik öneriler sun

UNUTMA: Sadece öz kodumuzdan doğan bilgiyi kullan!"""

        try:
            endpoint = self.config.llm_endpoints[self.config.sentez_model]
            response = await self.client.post(
                f"{endpoint}/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "Sen 12. Akıl'sın - Sentez Ustası. 11 Akıl'ı harmonize edersin."},
                        {"role": "user", "content": sentez_prompt}
                    ],
                    "temperature": 0.8,  # Sentez için biraz daha yaratıcı
                }
            )

            result = response.json()
            sentez_icerigi = result["choices"][0]["message"]["content"]

            print(f"✅ 12. Akıl sentezi tamamlandı!\n")

            return SentezYaniti(
                sentez=sentez_icerigi,
                kullanilan_akillar=[y.akil_tipi for y in akil_yanitlari if y.guven_skoru > 0.5],
                guven_skoru=0.9,
                ic_goruler=ic_goruler,
                oneriler=self._extract_recommendations(sentez_icerigi),
                timestamp=datetime.now()
            )

        except Exception as e:
            print(f"⚠️ 12. Akıl sentez hatası: {e}")
            return SentezYaniti(
                sentez=f"Sentez hatası: {e}",
                kullanilan_akillar=[],
                guven_skoru=0.0,
                ic_goruler=ic_goruler,
                oneriler=[],
                timestamp=datetime.now()
            )

    def _extract_recommendations(self, sentez: str) -> List[str]:
        """Sentezden önerileri çıkar (basit implementasyon)"""
        # TODO: Daha sofistike öneri çıkarma
        lines = sentez.split('\n')
        recommendations = [
            line.strip('- ').strip()
            for line in lines
            if line.strip().startswith('-') or line.strip().startswith('•')
        ]
        return recommendations[:5]  # İlk 5 öneri

    async def oz_koddan_yanitla(self, soru: str) -> Dict[str, Any]:
        """
        Ana orchestration fonksiyonu

        1. Öz veritabanından context çek
        2. 11 Akıl Harmanları'na sor
        3. 12. Akıl sentez yapsın
        4. Yanıtı öz veritabanına ekle (öğrenme)
        """
        print(f"\n{'='*60}")
        print(f"🌌 MODULllm.com Öz Kod Orchestration Başlıyor...")
        print(f"📝 Soru: {soru}")
        print(f"{'='*60}\n")

        # 1. 11 Akıl Harmanları
        akil_yanitlari = await self.on_bir_akil_harmanla(soru)

        # 2. 12. Akıl Sentezi
        sentez = await self.on_ikinci_akil_sentezle(soru, akil_yanitlari)

        # 3. Sonucu formatla
        sonuc = {
            "soru": soru,
            "on_bir_akil": [
                {
                    "akil": y.akil_tipi.value,
                    "perspektif": y.perspektif,
                    "yanitlayan_model": y.yanitlayan,
                    "icerik": y.icerik,
                    "guven": y.guven_skoru
                }
                for y in akil_yanitlari
            ],
            "on_ikinci_akil_sentezi": {
                "sentez": sentez.sentez,
                "kullanilan_akillar": [a.value for a in sentez.kullanilan_akillar],
                "ic_goruler": sentez.ic_goruler,
                "oneriler": sentez.oneriler,
                "guven": sentez.guven_skoru
            },
            "timestamp": datetime.now().isoformat(),
            "platform": "MODULllm.com - Öz Kodundan Doğan Güç!"
        }

        # 4. TODO: Öz veritabanına kaydet (öğrenme için)
        # await self._save_to_oz_db(soru, sonuc)

        print(f"\n{'='*60}")
        print(f"✅ Orchestration Tamamlandı!")
        print(f"{'='*60}\n")

        return sonuc

    async def close(self):
        """Cleanup"""
        await self.client.aclose()


# Kullanım örneği
async def test_orchestrator():
    """Test fonksiyonu"""
    orchestrator = OzKodOrchestrator()

    soru = "Python ile asenkron programlama nasıl yapılır?"

    sonuc = await orchestrator.oz_koddan_yanitla(soru)

    print("\n📊 SONUÇ ÖZETI:")
    print(f"11 Akıl'dan {len(sonuc['on_bir_akil'])} yanıt alındı")
    print(f"12. Akıl {len(sonuc['on_ikinci_akil_sentezi']['kullanilan_akillar'])} Akıl'ı kullanarak sentez yaptı")
    print(f"\n💡 Sentez:\n{sonuc['on_ikinci_akil_sentezi']['sentez'][:500]}...")

    await orchestrator.close()


if __name__ == "__main__":
    # Test
    asyncio.run(test_orchestrator())
