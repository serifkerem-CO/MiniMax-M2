"""
MODULllm.com - Öz Veritabanı Sistemi

Sadece bizim içeriğimiz, bizim kullanıcılarımız, bizim zekamız!
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import hashlib
from enum import Enum


class IcerikTipi(str, Enum):
    """Öz içerik tipleri"""
    SORU_CEVAP = "soru_cevap"           # Kullanıcı soruları ve cevaplar
    DERS_ICERIGI = "ders_icerigi"       # B1Z KODLAB dersleri
    KULLANICI_KODU = "kullanici_kodu"   # Kullanıcıların yazdığı kodlar
    AI_SENTEZI = "ai_sentezi"           # 12. Akıl sentezleri
    TOPLULUK = "topluluk"               # Topluluk içeriği
    PODCAST = "podcast"                  # Podcast içerikleri
    MAYA = "maya"                        # MAYA içerik sentezleri
    VIZYON = "vizyon"                    # Platform vizyonu ve stratejiler


@dataclass
class OzIcerik:
    """Öz veritabanı içerik modeli"""
    id: str                              # Unique ID
    tip: IcerikTipi                      # İçerik tipi
    baslik: str                          # İçerik başlığı
    icerik: str                          # Ana içerik
    etiketler: List[str]                 # Etiketler (arama için)
    yaratici: str                        # Kim oluşturdu
    embedding: Optional[List[float]]     # Vector embedding (semantic search için)
    metadata: Dict[str, Any]             # Ekstra bilgiler
    created_at: datetime
    updated_at: datetime
    goruntuleme: int = 0                 # Kaç kez kullanıldı
    guven_skoru: float = 1.0             # İçerik güvenilirliği (0-1)


@dataclass
class AramaSonucu:
    """Arama sonucu"""
    icerik: OzIcerik
    benzerlik_skoru: float  # Sorguyla ne kadar benzer (0-1)
    kullanim_skoru: float   # Ne kadar kullanışlı (0-1)


class OzVeritabani:
    """
    MODULllm.com Öz Veritabanı

    Prensipler:
    1. Sadece bizim içeriğimiz
    2. Kolektif zeka büyüyor
    3. Her soru, veritabanını zenginleştirir
    4. Dış kaynak yok!
    """

    def __init__(self, db_path: str = "modulllm_oz.db"):
        self.db_path = db_path
        self.icerikler: Dict[str, OzIcerik] = {}
        self._load_from_disk()

    def _generate_id(self, icerik: str) -> str:
        """İçerikten unique ID üret"""
        content_hash = hashlib.sha256(icerik.encode()).hexdigest()
        return content_hash[:16]

    def _calculate_embedding(self, text: str) -> List[float]:
        """
        TODO: Gerçek embedding hesaplama
        Şimdilik basit hash-based embedding
        Production'da: sentence-transformers veya OpenAI embeddings
        """
        # Basit placeholder embedding
        return [float(ord(c)) / 1000 for c in text[:128]]

    def ekle(
        self,
        tip: IcerikTipi,
        baslik: str,
        icerik: str,
        etiketler: List[str],
        yaratici: str = "modulllm_platform",
        metadata: Optional[Dict[str, Any]] = None
    ) -> OzIcerik:
        """Yeni içerik ekle"""
        icerik_id = self._generate_id(icerik)

        # Zaten varsa güncelle
        if icerik_id in self.icerikler:
            existing = self.icerikler[icerik_id]
            existing.goruntuleme += 1
            existing.updated_at = datetime.now()
            return existing

        # Yeni içerik oluştur
        oz_icerik = OzIcerik(
            id=icerik_id,
            tip=tip,
            baslik=baslik,
            icerik=icerik,
            etiketler=etiketler,
            yaratici=yaratici,
            embedding=self._calculate_embedding(icerik),
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            goruntuleme=0,
            guven_skoru=1.0
        )

        self.icerikler[icerik_id] = oz_icerik
        self._save_to_disk()

        print(f"✅ Öz veritabanına eklendi: {baslik} ({tip.value})")

        return oz_icerik

    def ara(
        self,
        sorgu: str,
        tip_filtre: Optional[IcerikTipi] = None,
        limit: int = 11
    ) -> List[AramaSonucu]:
        """
        Semantik arama yap

        TODO: Gerçek vector search implementasyonu
        Şimdilik basit keyword matching
        """
        sorgu_lower = sorgu.lower()
        sorgu_embedding = self._calculate_embedding(sorgu)

        sonuclar = []

        for icerik in self.icerikler.values():
            # Tip filtresi
            if tip_filtre and icerik.tip != tip_filtre:
                continue

            # Basit benzerlik hesaplama (keyword matching)
            # TODO: Gerçek cosine similarity hesapla
            benzerlik = 0.0

            # Başlıkta geçiyor mu?
            if sorgu_lower in icerik.baslik.lower():
                benzerlik += 0.4

            # İçerikte geçiyor mu?
            if sorgu_lower in icerik.icerik.lower():
                benzerlik += 0.3

            # Etiketlerde geçiyor mu?
            for etiket in icerik.etiketler:
                if sorgu_lower in etiket.lower():
                    benzerlik += 0.2
                    break

            # Kullanım skoru (ne kadar popüler)
            kullanim_skoru = min(icerik.goruntuleme / 100, 1.0)

            if benzerlik > 0:
                sonuclar.append(
                    AramaSonucu(
                        icerik=icerik,
                        benzerlik_skoru=benzerlik,
                        kullanim_skoru=kullanim_skoru
                    )
                )

        # Sırala: benzerlik + kullanım + güven
        sonuclar.sort(
            key=lambda x: (
                x.benzerlik_skoru * 0.6 +
                x.kullanim_skoru * 0.2 +
                x.icerik.guven_skoru * 0.2
            ),
            reverse=True
        )

        # Kullanım sayısını artır
        for sonuc in sonuclar[:limit]:
            sonuc.icerik.goruntuleme += 1

        return sonuclar[:limit]

    def get_context_for_query(self, sorgu: str, limit: int = 11) -> str:
        """
        Sorgu için context string oluştur
        Orchestrator'ın kullanacağı format
        """
        sonuclar = self.ara(sorgu, limit=limit)

        if not sonuclar:
            return "Henüz bu konuda öz içeriğimiz yok. İlk sorgu!"

        context_parts = []
        for i, sonuc in enumerate(sonuclar, 1):
            icerik = sonuc.icerik
            context_parts.append(
                f"### [{i}] {icerik.baslik} ({icerik.tip.value})\n"
                f"{icerik.icerik[:500]}...\n"
                f"Etiketler: {', '.join(icerik.etiketler)}\n"
            )

        return "\n".join(context_parts)

    def soru_cevap_ekle(
        self,
        soru: str,
        cevap: str,
        akil_yanitlari: Optional[List[Dict]] = None
    ) -> OzIcerik:
        """Soru-cevap çifti ekle (öğrenme için)"""
        return self.ekle(
            tip=IcerikTipi.SORU_CEVAP,
            baslik=soru[:100],
            icerik=f"SORU: {soru}\n\nCEVAP: {cevap}",
            etiketler=self._extract_keywords(soru),
            yaratici="11_akil_harmanlar",
            metadata={
                "akil_yanitlari": akil_yanitlari or [],
                "sentezlendi": True
            }
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """Metinden anahtar kelimeler çıkar (basit)"""
        # TODO: Daha sofistike keyword extraction
        words = text.lower().split()
        # Yaygın kelimeleri filtrele
        stopwords = {"bir", "bu", "şu", "ve", "ile", "için", "gibi", "nasıl", "nedir"}
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        return list(set(keywords))[:10]

    def istatistikler(self) -> Dict[str, Any]:
        """Öz veritabanı istatistikleri"""
        tip_dagılımı = {}
        for icerik in self.icerikler.values():
            tip_dagılımı[icerik.tip.value] = tip_dagılımı.get(icerik.tip.value, 0) + 1

        return {
            "toplam_icerik": len(self.icerikler),
            "tip_dagilimi": tip_dagılımı,
            "en_cok_kullanilan": sorted(
                self.icerikler.values(),
                key=lambda x: x.goruntuleme,
                reverse=True
            )[:11],
            "son_eklenenler": sorted(
                self.icerikler.values(),
                key=lambda x: x.created_at,
                reverse=True
            )[:11]
        }

    def _save_to_disk(self):
        """Diske kaydet"""
        try:
            data = {
                "icerikler": {
                    id: {
                        **asdict(icerik),
                        "created_at": icerik.created_at.isoformat(),
                        "updated_at": icerik.updated_at.isoformat(),
                        "tip": icerik.tip.value
                    }
                    for id, icerik in self.icerikler.items()
                }
            }

            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"⚠️ Disk'e kaydetme hatası: {e}")

    def _load_from_disk(self):
        """Diskten yükle"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for id, icerik_data in data.get("icerikler", {}).items():
                self.icerikler[id] = OzIcerik(
                    id=icerik_data["id"],
                    tip=IcerikTipi(icerik_data["tip"]),
                    baslik=icerik_data["baslik"],
                    icerik=icerik_data["icerik"],
                    etiketler=icerik_data["etiketler"],
                    yaratici=icerik_data["yaratici"],
                    embedding=icerik_data.get("embedding"),
                    metadata=icerik_data.get("metadata", {}),
                    created_at=datetime.fromisoformat(icerik_data["created_at"]),
                    updated_at=datetime.fromisoformat(icerik_data["updated_at"]),
                    goruntuleme=icerik_data.get("goruntuleme", 0),
                    guven_skoru=icerik_data.get("guven_skoru", 1.0)
                )

            print(f"✅ Öz veritabanı yüklendi: {len(self.icerikler)} içerik")

        except FileNotFoundError:
            print("📝 Yeni öz veritabanı oluşturuluyor...")
        except Exception as e:
            print(f"⚠️ Diskten yükleme hatası: {e}")


# İlk içerikleri ekle
def initialize_oz_db():
    """Platform başlarken öz veritabanını başlat"""
    db = OzVeritabani()

    # B1Z KODLAB ders içeriklerini ekle
    db.ekle(
        tip=IcerikTipi.DERS_ICERIGI,
        baslik="Python Temelleri - Ders 1",
        icerik="""Python programlamaya giriş dersi.
Değişkenler, veri tipleri, kontrol yapıları, fonksiyonlar.
Fibonacci, asal sayı kontrolü gibi temel algoritmalar.""",
        etiketler=["python", "programlama", "temel", "algoritma"],
        yaratici="b1z_kodlab"
    )

    db.ekle(
        tip=IcerikTipi.DERS_ICERIGI,
        baslik="JavaScript/TypeScript Basics - Ders 2",
        icerik="""Modern JavaScript ve TypeScript temelleri.
Arrow functions, async/await, Promises, type annotations.
ES6+ özellikleri ve TypeScript interface'leri.""",
        etiketler=["javascript", "typescript", "async", "modern-js"],
        yaratici="b1z_kodlab"
    )

    # Platform vizyonu ekle
    db.ekle(
        tip=IcerikTipi.VIZYON,
        baslik="MODULllm.com - Öz Kodundan Doğan Güç",
        icerik="""MODULllm.com, tamamen bağımsız ve özerk bir yapay zeka platformudur.
11 Akıl Harmanları + 12. Akıl Sentezi ile çalışır.
Sadece kendi öz veritabanımızı kullanır, dış kaynak kullanmaz.
DEAVAEM gemisinin su soğutmalı enerjisi ile güçlenir.""",
        etiketler=["vizyon", "modulllm", "oz-kod", "11-akil", "deavaem"],
        yaratici="modulllm_platform"
    )

    stats = db.istatistikler()
    print(f"\n📊 Öz Veritabanı Başlatıldı:")
    print(f"   Toplam içerik: {stats['toplam_icerik']}")
    print(f"   Tip dağılımı: {stats['tip_dagilimi']}")

    return db


if __name__ == "__main__":
    # Test
    db = initialize_oz_db()

    # Arama testi
    sonuclar = db.ara("Python async programlama")
    print(f"\n🔍 Arama: 'Python async programlama'")
    print(f"   {len(sonuclar)} sonuç bulundu")

    # Context oluşturma testi
    context = db.get_context_for_query("JavaScript promises")
    print(f"\n📝 Context:\n{context[:500]}...")
