"""
MiniMax-M2 RAG (Retrieval Augmented Generation) Şablonu
=======================================================
Belgelerden bilgi alarak sorulara cevap veren bir RAG sistemi.

MiniMax-M2, kanıt takipli retrieval ve alıntı yapma konusunda mükemmeldir.

Gereksinimler:
    pip install openai chromadb sentence-transformers

Kullanım:
    python main.py
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from openai import OpenAI

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("Uyarı: chromadb yüklü değil. pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


# Yapılandırma
API_BASE_URL = "http://localhost:8000/v1"
API_KEY = "your-api-key-here"
MODEL_NAME = "MiniMax-M2"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Yerel embedding modeli


@dataclass
class Document:
    """Bir belge parçasını temsil eder."""
    id: str
    content: str
    metadata: dict
    source: str


@dataclass
class SearchResult:
    """Arama sonucunu temsil eder."""
    document: Document
    score: float


class SimpleEmbedder:
    """Basit embedding sınıfı."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer(model_name)
        else:
            self.model = None
            print("Uyarı: sentence-transformers yüklü değil, basit hash kullanılacak")

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Metinleri vektörlere dönüştür."""
        if self.model:
            return self.model.encode(texts).tolist()
        else:
            # Basit hash tabanlı embedding (sadece demo için)
            return [[float(ord(c) % 100) / 100 for c in text[:384].ljust(384)]
                    for text in texts]


class DocumentStore:
    """Belge deposu - ChromaDB ile vektör araması."""

    def __init__(self, collection_name: str = "documents", persist_dir: str = "./chroma_db"):
        if not CHROMA_AVAILABLE:
            raise ImportError("chromadb gerekli: pip install chromadb")

        self.embedder = SimpleEmbedder()
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: list[Document]):
        """Belgeleri depoya ekle."""
        if not documents:
            return

        ids = [doc.id for doc in documents]
        contents = [doc.content for doc in documents]
        metadatas = [{"source": doc.source, **doc.metadata} for doc in documents]

        # Embedding oluştur
        embeddings = self.embedder.embed(contents)

        # ChromaDB'ye ekle
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )

        print(f"{len(documents)} belge eklendi.")

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Sorguya en yakın belgeleri bul."""
        query_embedding = self.embedder.embed([query])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        search_results = []
        for i in range(len(results["ids"][0])):
            doc = Document(
                id=results["ids"][0][i],
                content=results["documents"][0][i],
                metadata=results["metadatas"][0][i],
                source=results["metadatas"][0][i].get("source", "unknown")
            )
            # Cosine distance -> similarity score
            score = 1 - results["distances"][0][i]
            search_results.append(SearchResult(document=doc, score=score))

        return search_results

    def count(self) -> int:
        """Toplam belge sayısını döndür."""
        return self.collection.count()


class TextSplitter:
    """Metinleri parçalara ayırır."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str, source: str = "unknown") -> list[Document]:
        """Metni parçalara ayır."""
        chunks = []
        start = 0
        chunk_num = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            # Kelime sınırında kes
            if end < len(text):
                last_space = chunk_text.rfind(' ')
                if last_space > self.chunk_size // 2:
                    chunk_text = chunk_text[:last_space]
                    end = start + last_space

            chunk_id = hashlib.md5(f"{source}:{chunk_num}".encode()).hexdigest()[:12]

            chunks.append(Document(
                id=chunk_id,
                content=chunk_text.strip(),
                metadata={"chunk_num": chunk_num},
                source=source
            ))

            chunk_num += 1
            start = end - self.chunk_overlap

        return chunks


class RAGSystem:
    """RAG sistemi - Retrieval Augmented Generation."""

    SYSTEM_PROMPT = """Sen yardımcı bir asistansın. Sana verilen bağlam bilgilerini kullanarak soruları yanıtla.

Kurallar:
1. SADECE verilen bağlamdaki bilgileri kullan
2. Bağlamda olmayan bilgileri uydurma
3. Cevabın hangi kaynaktan geldiğini belirt
4. Emin değilsen "Bu bilgi verilen belgelerde yok" de
5. Alıntı yaparken kaynak belirt

Bağlam:
{context}
"""

    def __init__(
        self,
        api_key: str = API_KEY,
        base_url: str = API_BASE_URL,
        collection_name: str = "rag_docs"
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.store = DocumentStore(collection_name=collection_name)
        self.splitter = TextSplitter()
        self.messages = []

    def add_text(self, text: str, source: str = "document"):
        """Metin ekle ve indeksle."""
        chunks = self.splitter.split(text, source)
        self.store.add_documents(chunks)
        return len(chunks)

    def add_file(self, filepath: str) -> int:
        """Dosyadan belge ekle."""
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")

        content = path.read_text(encoding="utf-8")
        return self.add_text(content, source=path.name)

    def add_directory(self, dirpath: str, extensions: list[str] = None) -> int:
        """Dizindeki dosyaları ekle."""
        extensions = extensions or [".txt", ".md", ".py", ".js", ".json"]
        path = Path(dirpath)
        total_chunks = 0

        for file in path.rglob("*"):
            if file.is_file() and file.suffix in extensions:
                try:
                    chunks = self.add_file(str(file))
                    total_chunks += chunks
                    print(f"  + {file.name}: {chunks} parça")
                except Exception as e:
                    print(f"  ! {file.name}: {e}")

        return total_chunks

    def _build_context(self, results: list[SearchResult]) -> str:
        """Arama sonuçlarından bağlam oluştur."""
        context_parts = []

        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Kaynak {i}: {result.document.source}]\n{result.document.content}"
            )

        return "\n\n---\n\n".join(context_parts)

    def query(self, question: str, top_k: int = 5) -> dict:
        """Soruyu yanıtla."""
        # İlgili belgeleri bul
        results = self.store.search(question, top_k=top_k)

        if not results:
            return {
                "answer": "Hiç ilgili belge bulunamadı.",
                "sources": [],
                "context": ""
            }

        # Bağlam oluştur
        context = self._build_context(results)

        # LLM'e sor
        system_prompt = self.SYSTEM_PROMPT.format(context=context)

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        answer = response.choices[0].message.content

        # Kaynakları topla
        sources = [
            {"source": r.document.source, "score": r.score}
            for r in results
        ]

        return {
            "answer": answer,
            "sources": sources,
            "context": context
        }

    def chat(self, message: str, top_k: int = 5) -> str:
        """Sohbet modunda soru sor."""
        result = self.query(message, top_k=top_k)

        # Kaynakları göster
        sources_text = "\n".join([
            f"  - {s['source']} (skor: {s['score']:.2f})"
            for s in result["sources"][:3]
        ])

        return f"{result['answer']}\n\n📚 Kaynaklar:\n{sources_text}"


def demo():
    """Demo: Örnek belgeler ile RAG sistemi."""
    print("=" * 60)
    print("MiniMax-M2 RAG Sistemi Demo")
    print("=" * 60)

    # Örnek belgeler
    sample_docs = [
        {
            "source": "python_temelleri.txt",
            "content": """
Python, Guido van Rossum tarafından 1991 yılında oluşturulmuş yüksek seviyeli bir
programlama dilidir. Python'un temel özellikleri şunlardır:

1. Okunabilir Sözdizimi: Python, İngilizce'ye benzer temiz bir sözdizimine sahiptir.
2. Dinamik Tipleme: Değişken tiplerini önceden belirtmenize gerek yoktur.
3. Geniş Standart Kütüphane: "Piller dahil" felsefesi ile birçok hazır modül sunar.
4. Çoklu Paradigma: Nesne yönelimli, fonksiyonel ve prosedürel programlamayı destekler.
5. Platform Bağımsız: Windows, Linux ve macOS'ta çalışır.

Python'un popüler kullanım alanları: Web geliştirme (Django, Flask), veri bilimi
(Pandas, NumPy), yapay zeka (TensorFlow, PyTorch), otomasyon ve scripting.
            """
        },
        {
            "source": "makine_ogrenmesi.txt",
            "content": """
Makine öğrenmesi, bilgisayarların açıkça programlanmadan verilerden öğrenmesini
sağlayan yapay zekanın bir alt dalıdır.

Makine Öğrenmesi Türleri:

1. Denetimli Öğrenme (Supervised Learning):
   - Etiketli veri ile eğitim yapılır
   - Örnekler: Sınıflandırma, regresyon
   - Algoritmalar: Linear Regression, Random Forest, SVM

2. Denetimsiz Öğrenme (Unsupervised Learning):
   - Etiketsiz veri ile örüntüler bulunur
   - Örnekler: Kümeleme, boyut indirgeme
   - Algoritmalar: K-Means, PCA, DBSCAN

3. Pekiştirmeli Öğrenme (Reinforcement Learning):
   - Ajan çevre ile etkileşerek öğrenir
   - Ödül/ceza mekanizması kullanılır
   - Örnekler: Oyun oynama, robot kontrolü

Popüler ML Kütüphaneleri: scikit-learn, TensorFlow, PyTorch, XGBoost
            """
        },
        {
            "source": "minimax_m2.txt",
            "content": """
MiniMax-M2, MiniMax AI tarafından geliştirilen açık kaynaklı bir dil modelidir.

Temel Özellikler:
- 230 milyar toplam parametre
- 10 milyar aktif parametre (çıkarım sırasında)
- Mixture of Experts (MoE) mimarisi
- Kod yazma ve agentic iş akışları için optimize edilmiş

Benchmark Performansı:
- SWE-bench Verified: %69.4
- Terminal-Bench: %46.3
- LiveCodeBench: %83
- AIME25: 78

MiniMax-M2'nin güçlü yönleri:
1. Çoklu dosya düzenleme
2. Kod-çalıştır-düzelt döngüleri
3. Karmaşık araç kullanımı
4. Hata kurtarma yeteneği
5. Düşük gecikme süresi

Dağıtım seçenekleri: SGLang, vLLM, MLX (Apple Silicon), HuggingFace
            """
        }
    ]

    # RAG sistemi oluştur
    rag = RAGSystem(collection_name="demo_docs")

    # Belgeleri ekle
    print("\n📄 Belgeler ekleniyor...")
    for doc in sample_docs:
        chunks = rag.add_text(doc["content"], source=doc["source"])
        print(f"  + {doc['source']}: {chunks} parça")

    print(f"\n📊 Toplam belge sayısı: {rag.store.count()}")

    # Örnek sorular
    questions = [
        "Python'un temel özellikleri nelerdir?",
        "Denetimli öğrenme nedir?",
        "MiniMax-M2'nin benchmark sonuçları nelerdir?",
    ]

    print("\n" + "=" * 60)
    print("Örnek Sorular")
    print("=" * 60)

    for q in questions:
        print(f"\n❓ Soru: {q}")
        print("-" * 40)
        response = rag.chat(q)
        print(response)

    # İnteraktif mod
    print("\n" + "=" * 60)
    print("İnteraktif Mod (çıkmak için 'q' yazın)")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n❓ Soru: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower() in ['q', 'quit', 'çık']:
            break

        if not user_input:
            continue

        response = rag.chat(user_input)
        print(f"\n{response}")

    print("\nGüle güle!")


def main():
    """Ana giriş noktası."""
    if not CHROMA_AVAILABLE:
        print("Hata: chromadb gerekli")
        print("Yüklemek için: pip install chromadb sentence-transformers")
        return

    demo()


if __name__ == "__main__":
    main()
