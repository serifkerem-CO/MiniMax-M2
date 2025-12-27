"""
📦 SAMPLE DATA - Örnek Veriler
==============================

Demo ve test için örnek veri setleri.
"""

import random
from typing import Any, Dict, List


# ===== ÇED RAPORLARI =====
SAMPLE_CED_DATA = [
    {
        "id": "CED_2024_001",
        "title": "Marmara Bölgesi Endüstriyel Atık Yönetimi",
        "year": 2024,
        "region": "Marmara",
        "sector": "Atık Yönetimi",
        "summary": """
        Marmara Bölgesi'nde 2023 yılında toplam 2.4 milyon ton endüstriyel atık üretilmiştir.
        Bu atıkların %65'i geri dönüştürülmüş, %20'si enerji üretiminde kullanılmıştır.
        Kalan %15'lik kısım düzenli depolama tesislerinde bertaraf edilmiştir.
        Öneriler: Döngüsel ekonomi modelinin genişletilmesi, atık azaltma teşvikleri.
        """,
        "risk_level": "ORTA",
        "tags": ["atık", "marmara", "geri dönüşüm", "endüstri"],
    },
    {
        "id": "CED_2024_002",
        "title": "Ege Bölgesi Yenilenebilir Enerji Dönüşümü",
        "year": 2024,
        "region": "Ege",
        "sector": "Enerji",
        "summary": """
        Ege Bölgesi, 2024 itibariyle elektrik üretiminin %42'sini yenilenebilir kaynaklardan
        sağlamaktadır. Güneş enerjisi kurulu gücü 5.2 GW'a ulaşmıştır.
        Rüzgar enerjisi potansiyelinin %60'ı henüz kullanılmamaktadır.
        2030 hedefi: %70 yenilenebilir enerji payı.
        """,
        "risk_level": "DÜŞÜK",
        "tags": ["enerji", "güneş", "rüzgar", "ege", "yenilenebilir"],
    },
    {
        "id": "CED_2024_003",
        "title": "İç Anadolu Su Kaynakları Değerlendirmesi",
        "year": 2024,
        "region": "İç Anadolu",
        "sector": "Su Kaynakları",
        "summary": """
        Konya Kapalı Havzası'nda yeraltı su seviyeleri son 10 yılda ortalama 25 metre düşmüştür.
        Tarımsal sulama verimliliği %40 altındadır. Damlama sulama oranı sadece %15'tir.
        Acil önlem: Su tasarruflu tarım teknolojilerine geçiş, yer altı suyu kullanım kotaları.
        """,
        "risk_level": "YÜKSEK",
        "tags": ["su", "kuraklık", "tarım", "iç anadolu", "acil"],
    },
]

# ===== SANAYİ VERİLERİ =====
SAMPLE_INDUSTRY_DATA = [
    {
        "id": "IND_2024_Q3",
        "title": "Türkiye Sanayi Üretim Endeksi Q3 2024",
        "period": "2024-Q3",
        "metrics": {
            "production_index": 112.5,
            "yoy_change": 4.2,
            "capacity_utilization": 76.8,
            "export_share": 0.34,
        },
        "sectors": {
            "otomotiv": {"growth": 8.5, "employment": 450000},
            "tekstil": {"growth": 2.1, "employment": 620000},
            "makine": {"growth": 6.3, "employment": 280000},
            "gida": {"growth": 3.8, "employment": 520000},
            "kimya": {"growth": 5.2, "employment": 180000},
        },
        "analysis": """
        Türkiye sanayi sektörü 2024 Q3'te %4.2 büyüme kaydetmiştir.
        Otomotiv sektörü lider konumunu korurken, tekstil sektöründe yavaşlama görülmektedir.
        Dijital dönüşüm yatırımları %25 artış göstermiştir.
        Ana riskler: enerji maliyetleri, hammadde tedariki, nitelikli işgücü açığı.
        """,
        "tags": ["sanayi", "üretim", "q3", "2024", "endeks"],
    },
    {
        "id": "IND_DIGITAL_2024",
        "title": "Sanayi 4.0 Dönüşüm Raporu",
        "year": 2024,
        "metrics": {
            "digitalization_rate": 0.47,
            "iot_adoption": 0.32,
            "ai_usage": 0.18,
            "robotics_density": 42,  # per 10k workers
        },
        "analysis": """
        Türkiye'de sanayi dijitalleşme oranı %47'ye ulaşmıştır.
        IoT sensör kullanımı son 2 yılda 3 kat artmıştır.
        Yapay zeka uygulamaları henüz başlangıç aşamasında (%18).
        Robot yoğunluğu (42/10bin işçi) dünya ortalamasının altında.
        Hedef 2028: %75 dijitalleşme, 100 robot/10bin işçi.
        """,
        "tags": ["dijital", "sanayi 4.0", "iot", "yapay zeka", "robotik"],
    },
]

# ===== SOSYAL MEDYA VERİLERİ =====
SAMPLE_SOCIAL_DATA = [
    {
        "platform": "twitter",
        "topic": "#YeşilDönüşüm",
        "sentiment": "positive",
        "volume": 15420,
        "sample_posts": [
            "Fabrikamızda güneş paneli kurulumu tamamlandı! #YeşilDönüşüm 🌱",
            "2024 çevre raporu: Sıfır atık hedefine %80 ulaştık",
            "Sürdürülebilir üretim artık zorunluluk değil fırsat!",
        ],
    },
    {
        "platform": "linkedin",
        "topic": "Sanayi Dönüşümü",
        "sentiment": "mixed",
        "volume": 8750,
        "sample_posts": [
            "Dijitalleşme yatırımları geri dönüyor mu? Analiz raporu yayında.",
            "Nitelikli işgücü açığı sanayinin en büyük sorunu",
            "Türkiye ihracatı 2024'te yeni rekor kırdı!",
        ],
    },
    {
        "platform": "reddit",
        "topic": "Turkey Manufacturing",
        "sentiment": "neutral",
        "volume": 3200,
        "sample_posts": [
            "What's happening with Turkish automotive industry?",
            "EV production in Turkey - timeline and projections",
            "Supply chain challenges in textile sector",
        ],
    },
]

# ===== KEHANET KONULARI =====
PROPHECY_TOPICS = [
    "Türkiye sanayisinin 2030 vizyonu",
    "Yeşil dönüşümün ekonomik etkileri",
    "Yapay zeka ve istihdam dengesi",
    "Döngüsel ekonomiye geçiş stratejisi",
    "Enerji bağımsızlığı yol haritası",
    "İhracat çeşitlendirme fırsatları",
    "Girişimcilik ekosisteminin geleceği",
    "Teknoloji transferi ve yerli üretim",
]

# ===== LEGEND İSİMLERİ =====
LEGENDS = [
    {"id": "ID1000", "name": "Luna", "title": "Veri Kahini"},
    {"id": "ID1006", "name": "Kira", "title": "Strateji Ustası"},
    {"id": "ID1111", "name": "Arin", "title": "Vizyon Mimarı"},
    {"id": "ID1042", "name": "Zephyr", "title": "Rüzgar Okuyucu"},
]


# ===== YARDIMCI FONKSİYONLAR =====

def get_random_sample(category: str = "all") -> Dict[str, Any]:
    """Rastgele örnek veri al"""
    pools = {
        "ced": SAMPLE_CED_DATA,
        "industry": SAMPLE_INDUSTRY_DATA,
        "social": SAMPLE_SOCIAL_DATA,
        "prophecy": PROPHECY_TOPICS,
        "legend": LEGENDS,
    }

    if category == "all":
        all_data = []
        for pool in pools.values():
            if isinstance(pool, list):
                all_data.extend(pool)
        return random.choice(all_data)

    pool = pools.get(category)
    if pool:
        return random.choice(pool)

    return {}


def get_sample_query() -> str:
    """Örnek sorgu al"""
    queries = [
        "Türkiye sanayisinin en büyük fırsatları neler?",
        "Yeşil dönüşüm için hangi sektörler öncelikli?",
        "2025 için kritik risk faktörleri nelerdir?",
        "Dijitalleşme yatırımları nasıl önceliklendirilmeli?",
        "İhracat performansını artırmak için stratejiler",
        "İstihdam ve otomasyon dengesini nasıl kurabiliriz?",
        "Enerji verimliliği için acil eylem planı",
        "KOBİ'lerin dijital dönüşüm yol haritası",
    ]
    return random.choice(queries)


def get_sample_content_for_fold() -> str:
    """Katlama için örnek içerik"""
    contents = [
        SAMPLE_CED_DATA[0]["summary"],
        SAMPLE_INDUSTRY_DATA[0]["analysis"],
        SAMPLE_INDUSTRY_DATA[1]["analysis"],
        "Türkiye ekonomisi 2024'te %4.5 büyüme hedefliyor. Sanayi sektörü bu büyümenin lokomotifi olarak görülüyor.",
        "Yapay zeka uygulamaları üretim verimliliğini %20-30 artırma potansiyeli taşıyor.",
    ]
    return random.choice(contents)


# Test
if __name__ == "__main__":
    print("📦 Örnek Veri Setleri")
    print("=" * 50)

    print(f"\n🌱 ÇED Raporları: {len(SAMPLE_CED_DATA)} adet")
    print(f"🏭 Sanayi Verileri: {len(SAMPLE_INDUSTRY_DATA)} adet")
    print(f"📱 Sosyal Medya: {len(SAMPLE_SOCIAL_DATA)} adet")
    print(f"🔮 Kehanet Konuları: {len(PROPHECY_TOPICS)} adet")

    print("\n📝 Rastgele Sorgu:", get_sample_query())
    print("📄 Rastgele İçerik:", get_sample_content_for_fold()[:100] + "...")
