"""
MiniMax-M2 Data Pipeline Şablonu
================================
AI destekli veri işleme pipeline'ı.

Özellikler:
- ETL (Extract, Transform, Load) işlemleri
- AI ile veri temizleme ve zenginleştirme
- Paralel işleme
- Checkpoint mekanizması
- Çeşitli veri kaynakları desteği

Gereksinimler:
    pip install openai pandas pyarrow duckdb

Kullanım:
    python main.py --input data.csv --output processed.parquet --transform "temizle ve normalize et"
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Any, Callable, Iterator
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from abc import ABC, abstractmethod

import pandas as pd
from openai import OpenAI

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# Pipeline ayarları
BATCH_SIZE = int(os.getenv("PIPELINE_BATCH_SIZE", "100"))
MAX_WORKERS = int(os.getenv("PIPELINE_MAX_WORKERS", "4"))
CHECKPOINT_DIR = os.getenv("PIPELINE_CHECKPOINT_DIR", ".checkpoints")

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)


# ============================================================================
# Veri Yapıları
# ============================================================================

@dataclass
class PipelineConfig:
    """Pipeline yapılandırması."""
    batch_size: int = BATCH_SIZE
    max_workers: int = MAX_WORKERS
    checkpoint_enabled: bool = True
    checkpoint_dir: str = CHECKPOINT_DIR
    retry_count: int = 3
    retry_delay: float = 1.0


@dataclass
class PipelineStats:
    """Pipeline istatistikleri."""
    total_records: int = 0
    processed_records: int = 0
    failed_records: int = 0
    start_time: float = 0
    end_time: float = 0
    errors: list = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time if self.end_time else 0

    @property
    def success_rate(self) -> float:
        if self.total_records == 0:
            return 0
        return (self.processed_records / self.total_records) * 100


# ============================================================================
# Veri Kaynakları (Extract)
# ============================================================================

class DataSource(ABC):
    """Veri kaynağı arayüzü."""

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """Veriyi oku."""
        pass

    @abstractmethod
    def write(self, df: pd.DataFrame) -> None:
        """Veriyi yaz."""
        pass


class CSVSource(DataSource):
    """CSV veri kaynağı."""

    def __init__(self, path: str, **kwargs):
        self.path = path
        self.kwargs = kwargs

    def read(self) -> pd.DataFrame:
        return pd.read_csv(self.path, **self.kwargs)

    def write(self, df: pd.DataFrame) -> None:
        df.to_csv(self.path, index=False, **self.kwargs)


class JSONSource(DataSource):
    """JSON veri kaynağı."""

    def __init__(self, path: str, **kwargs):
        self.path = path
        self.kwargs = kwargs

    def read(self) -> pd.DataFrame:
        return pd.read_json(self.path, **self.kwargs)

    def write(self, df: pd.DataFrame) -> None:
        df.to_json(self.path, orient="records", indent=2, force_ascii=False)


class ParquetSource(DataSource):
    """Parquet veri kaynağı."""

    def __init__(self, path: str, **kwargs):
        self.path = path
        self.kwargs = kwargs

    def read(self) -> pd.DataFrame:
        return pd.read_parquet(self.path, **self.kwargs)

    def write(self, df: pd.DataFrame) -> None:
        df.to_parquet(self.path, index=False, **self.kwargs)


class ExcelSource(DataSource):
    """Excel veri kaynağı."""

    def __init__(self, path: str, **kwargs):
        self.path = path
        self.kwargs = kwargs

    def read(self) -> pd.DataFrame:
        return pd.read_excel(self.path, **self.kwargs)

    def write(self, df: pd.DataFrame) -> None:
        df.to_excel(self.path, index=False, **self.kwargs)


class DuckDBSource(DataSource):
    """DuckDB veri kaynağı."""

    def __init__(self, path: str, table: str = "data", **kwargs):
        self.path = path
        self.table = table
        self.kwargs = kwargs

    def read(self) -> pd.DataFrame:
        import duckdb
        conn = duckdb.connect(self.path)
        df = conn.execute(f"SELECT * FROM {self.table}").fetchdf()
        conn.close()
        return df

    def write(self, df: pd.DataFrame) -> None:
        import duckdb
        conn = duckdb.connect(self.path)
        conn.execute(f"CREATE OR REPLACE TABLE {self.table} AS SELECT * FROM df")
        conn.close()


def get_source(path: str, **kwargs) -> DataSource:
    """Dosya uzantısına göre kaynak döndür."""
    ext = Path(path).suffix.lower()
    sources = {
        ".csv": CSVSource,
        ".json": JSONSource,
        ".parquet": ParquetSource,
        ".xlsx": ExcelSource,
        ".xls": ExcelSource,
        ".duckdb": DuckDBSource,
        ".db": DuckDBSource,
    }
    source_class = sources.get(ext)
    if not source_class:
        raise ValueError(f"Desteklenmeyen dosya formatı: {ext}")
    return source_class(path, **kwargs)


# ============================================================================
# Dönüşümler (Transform)
# ============================================================================

class Transformer(ABC):
    """Dönüşüm arayüzü."""

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Veriyi dönüştür."""
        pass


class DropNullTransformer(Transformer):
    """Null değerleri temizle."""

    def __init__(self, columns: list = None, how: str = "any"):
        self.columns = columns
        self.how = how

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.columns:
            return df.dropna(subset=self.columns, how=self.how)
        return df.dropna(how=self.how)


class FillNullTransformer(Transformer):
    """Null değerleri doldur."""

    def __init__(self, value: Any = None, method: str = None, column_values: dict = None):
        self.value = value
        self.method = method
        self.column_values = column_values or {}

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.column_values:
            return df.fillna(self.column_values)
        elif self.method:
            return df.fillna(method=self.method)
        return df.fillna(self.value)


class RenameTransformer(Transformer):
    """Sütun adlarını değiştir."""

    def __init__(self, columns: dict):
        self.columns = columns

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns=self.columns)


class SelectTransformer(Transformer):
    """Belirli sütunları seç."""

    def __init__(self, columns: list):
        self.columns = columns

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.columns]


class FilterTransformer(Transformer):
    """Satırları filtrele."""

    def __init__(self, condition: Callable[[pd.DataFrame], pd.Series]):
        self.condition = condition

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.condition(df)]


class TypeTransformer(Transformer):
    """Veri tiplerini dönüştür."""

    def __init__(self, dtypes: dict):
        self.dtypes = dtypes

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.astype(self.dtypes)


class DeduplicateTransformer(Transformer):
    """Tekrar eden satırları kaldır."""

    def __init__(self, columns: list = None, keep: str = "first"):
        self.columns = columns
        self.keep = keep

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.drop_duplicates(subset=self.columns, keep=self.keep)


class SortTransformer(Transformer):
    """Sırala."""

    def __init__(self, columns: list, ascending: bool = True):
        self.columns = columns
        self.ascending = ascending

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.sort_values(by=self.columns, ascending=self.ascending)


class LambdaTransformer(Transformer):
    """Özel fonksiyon uygula."""

    def __init__(self, func: Callable[[pd.DataFrame], pd.DataFrame]):
        self.func = func

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.func(df)


# ============================================================================
# AI Dönüşümler
# ============================================================================

class AITransformer(Transformer):
    """AI destekli dönüşüm."""

    def __init__(self, instruction: str, columns: list = None, batch_size: int = 10):
        self.instruction = instruction
        self.columns = columns
        self.batch_size = batch_size

    def _transform_batch(self, batch: pd.DataFrame) -> list[dict]:
        """Batch'i AI ile dönüştür."""
        # Veriyi JSON olarak hazırla
        if self.columns:
            data = batch[self.columns].to_dict(orient="records")
        else:
            data = batch.to_dict(orient="records")

        prompt = f"""Bu veriyi aşağıdaki kurallara göre dönüştür:

KURAL: {self.instruction}

VERİ:
{json.dumps(data, ensure_ascii=False, indent=2)}

Dönüştürülmüş veriyi JSON array olarak döndür. Sadece JSON döndür, başka bir şey yazma."""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Sen veri dönüştürme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000,
        )

        try:
            content = response.choices[0].message.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            return json.loads(json_str)
        except json.JSONDecodeError:
            return data

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tüm veriyi AI ile dönüştür."""
        results = []

        for i in range(0, len(df), self.batch_size):
            batch = df.iloc[i:i + self.batch_size]
            print(f"  🤖 AI dönüşümü: {i}/{len(df)}")
            transformed = self._transform_batch(batch)
            results.extend(transformed)

        return pd.DataFrame(results)


class AIEnricher(Transformer):
    """AI ile veri zenginleştirme."""

    def __init__(self, instruction: str, new_column: str, source_columns: list):
        self.instruction = instruction
        self.new_column = new_column
        self.source_columns = source_columns

    def _enrich_row(self, row: dict) -> str:
        """Tek satırı zenginleştir."""
        source_data = {k: row[k] for k in self.source_columns if k in row}

        prompt = f"""Bu veriyi kullanarak şunu üret: {self.instruction}

VERİ: {json.dumps(source_data, ensure_ascii=False)}

Sadece sonucu döndür, açıklama yazma."""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )

        return response.choices[0].message.content.strip()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Veriyi zenginleştir."""
        df = df.copy()
        enriched = []

        for i, row in df.iterrows():
            if i % 10 == 0:
                print(f"  ✨ Zenginleştirme: {i}/{len(df)}")
            enriched.append(self._enrich_row(row.to_dict()))

        df[self.new_column] = enriched
        return df


class AICleaner(Transformer):
    """AI ile veri temizleme."""

    def __init__(self, columns: list):
        self.columns = columns

    def _clean_value(self, value: str) -> str:
        """Değeri temizle."""
        if pd.isna(value) or not isinstance(value, str):
            return value

        prompt = f"""Bu değeri temizle ve normalize et. Yazım hatalarını düzelt, gereksiz boşlukları kaldır, tutarlı formata getir.

DEĞİŞTİRİLECEK: {value}

Sadece temizlenmiş değeri döndür."""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200,
        )

        return response.choices[0].message.content.strip()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sütunları temizle."""
        df = df.copy()

        for col in self.columns:
            if col not in df.columns:
                continue
            print(f"  🧹 Temizleniyor: {col}")
            df[col] = df[col].apply(self._clean_value)

        return df


# ============================================================================
# Checkpoint Manager
# ============================================================================

class CheckpointManager:
    """Checkpoint yöneticisi."""

    def __init__(self, checkpoint_dir: str = CHECKPOINT_DIR):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)

    def _get_hash(self, pipeline_id: str) -> str:
        """Pipeline hash'i oluştur."""
        return hashlib.md5(pipeline_id.encode()).hexdigest()[:8]

    def save(self, pipeline_id: str, step: int, df: pd.DataFrame) -> None:
        """Checkpoint kaydet."""
        hash_id = self._get_hash(pipeline_id)
        path = self.checkpoint_dir / f"{hash_id}_step{step}.parquet"
        df.to_parquet(path, index=False)
        print(f"  💾 Checkpoint kaydedildi: {path.name}")

    def load(self, pipeline_id: str, step: int) -> Optional[pd.DataFrame]:
        """Checkpoint yükle."""
        hash_id = self._get_hash(pipeline_id)
        path = self.checkpoint_dir / f"{hash_id}_step{step}.parquet"
        if path.exists():
            print(f"  📂 Checkpoint yüklendi: {path.name}")
            return pd.read_parquet(path)
        return None

    def get_last_step(self, pipeline_id: str) -> int:
        """Son checkpoint adımını bul."""
        hash_id = self._get_hash(pipeline_id)
        steps = []
        for path in self.checkpoint_dir.glob(f"{hash_id}_step*.parquet"):
            try:
                step = int(path.stem.split("_step")[1])
                steps.append(step)
            except (IndexError, ValueError):
                pass
        return max(steps) if steps else -1

    def clear(self, pipeline_id: str) -> None:
        """Checkpoint'leri temizle."""
        hash_id = self._get_hash(pipeline_id)
        for path in self.checkpoint_dir.glob(f"{hash_id}_*.parquet"):
            path.unlink()
        print(f"  🗑️ Checkpoint'ler temizlendi")


# ============================================================================
# Pipeline
# ============================================================================

class Pipeline:
    """Veri işleme pipeline'ı."""

    def __init__(self, name: str, config: PipelineConfig = None):
        self.name = name
        self.config = config or PipelineConfig()
        self.transformers: list[tuple[str, Transformer]] = []
        self.checkpoint_manager = CheckpointManager(self.config.checkpoint_dir)
        self.stats = PipelineStats()

    def add_step(self, name: str, transformer: Transformer) -> "Pipeline":
        """Adım ekle."""
        self.transformers.append((name, transformer))
        return self

    def run(self, source: DataSource, target: DataSource = None, resume: bool = True) -> pd.DataFrame:
        """Pipeline'ı çalıştır."""
        print(f"\n{'='*60}")
        print(f"🚀 Pipeline: {self.name}")
        print(f"{'='*60}")

        self.stats = PipelineStats()
        self.stats.start_time = time.time()

        # Veriyi oku veya checkpoint'ten devam et
        start_step = -1
        if resume and self.config.checkpoint_enabled:
            start_step = self.checkpoint_manager.get_last_step(self.name)
            if start_step >= 0:
                df = self.checkpoint_manager.load(self.name, start_step)
                print(f"\n▶️ Checkpoint'ten devam ediliyor: adım {start_step}")
            else:
                print("\n📖 Veri okunuyor...")
                df = source.read()
        else:
            print("\n📖 Veri okunuyor...")
            df = source.read()

        self.stats.total_records = len(df)
        print(f"   {len(df)} kayıt yüklendi")

        # Dönüşümleri uygula
        for i, (step_name, transformer) in enumerate(self.transformers):
            if i <= start_step:
                continue

            print(f"\n📍 Adım {i + 1}/{len(self.transformers)}: {step_name}")

            try:
                df = transformer.transform(df)
                print(f"   ✅ {len(df)} kayıt")

                # Checkpoint kaydet
                if self.config.checkpoint_enabled:
                    self.checkpoint_manager.save(self.name, i, df)

            except Exception as e:
                self.stats.errors.append({"step": step_name, "error": str(e)})
                print(f"   ❌ Hata: {e}")
                raise

        self.stats.processed_records = len(df)
        self.stats.end_time = time.time()

        # Sonucu yaz
        if target:
            print(f"\n💾 Sonuç yazılıyor...")
            target.write(df)
            print(f"   ✅ Kaydedildi")

        # Checkpoint'leri temizle
        if self.config.checkpoint_enabled:
            self.checkpoint_manager.clear(self.name)

        # İstatistikler
        print(f"\n{'='*60}")
        print(f"📊 Pipeline Tamamlandı")
        print(f"   Süre: {self.stats.duration:.2f}s")
        print(f"   Kayıt: {self.stats.processed_records}/{self.stats.total_records}")
        print(f"   Başarı: %{self.stats.success_rate:.1f}")
        print(f"{'='*60}\n")

        return df


# ============================================================================
# Pipeline Builder
# ============================================================================

class PipelineBuilder:
    """Pipeline oluşturucu."""

    def __init__(self, name: str):
        self.pipeline = Pipeline(name)

    def config(self, **kwargs) -> "PipelineBuilder":
        """Yapılandırma ayarla."""
        for key, value in kwargs.items():
            if hasattr(self.pipeline.config, key):
                setattr(self.pipeline.config, key, value)
        return self

    def drop_null(self, columns: list = None, how: str = "any") -> "PipelineBuilder":
        """Null temizleme ekle."""
        self.pipeline.add_step("Null Temizleme", DropNullTransformer(columns, how))
        return self

    def fill_null(self, value: Any = None, **column_values) -> "PipelineBuilder":
        """Null doldurma ekle."""
        self.pipeline.add_step("Null Doldurma", FillNullTransformer(value, column_values=column_values))
        return self

    def rename(self, **columns) -> "PipelineBuilder":
        """Yeniden adlandırma ekle."""
        self.pipeline.add_step("Yeniden Adlandırma", RenameTransformer(columns))
        return self

    def select(self, *columns) -> "PipelineBuilder":
        """Sütun seçimi ekle."""
        self.pipeline.add_step("Sütun Seçimi", SelectTransformer(list(columns)))
        return self

    def filter(self, condition: Callable) -> "PipelineBuilder":
        """Filtreleme ekle."""
        self.pipeline.add_step("Filtreleme", FilterTransformer(condition))
        return self

    def cast(self, **dtypes) -> "PipelineBuilder":
        """Tip dönüşümü ekle."""
        self.pipeline.add_step("Tip Dönüşümü", TypeTransformer(dtypes))
        return self

    def deduplicate(self, columns: list = None, keep: str = "first") -> "PipelineBuilder":
        """Tekrar temizleme ekle."""
        self.pipeline.add_step("Tekrar Temizleme", DeduplicateTransformer(columns, keep))
        return self

    def sort(self, *columns, ascending: bool = True) -> "PipelineBuilder":
        """Sıralama ekle."""
        self.pipeline.add_step("Sıralama", SortTransformer(list(columns), ascending))
        return self

    def transform(self, func: Callable) -> "PipelineBuilder":
        """Özel dönüşüm ekle."""
        self.pipeline.add_step("Özel Dönüşüm", LambdaTransformer(func))
        return self

    def ai_transform(self, instruction: str, columns: list = None) -> "PipelineBuilder":
        """AI dönüşümü ekle."""
        self.pipeline.add_step("AI Dönüşümü", AITransformer(instruction, columns))
        return self

    def ai_enrich(self, instruction: str, new_column: str, source_columns: list) -> "PipelineBuilder":
        """AI zenginleştirme ekle."""
        self.pipeline.add_step("AI Zenginleştirme", AIEnricher(instruction, new_column, source_columns))
        return self

    def ai_clean(self, *columns) -> "PipelineBuilder":
        """AI temizleme ekle."""
        self.pipeline.add_step("AI Temizleme", AICleaner(list(columns)))
        return self

    def build(self) -> Pipeline:
        """Pipeline'ı döndür."""
        return self.pipeline


# ============================================================================
# CLI
# ============================================================================

def main():
    """Ana fonksiyon."""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax-M2 Data Pipeline")
    parser.add_argument("--input", "-i", help="Girdi dosyası")
    parser.add_argument("--output", "-o", help="Çıktı dosyası")
    parser.add_argument("--transform", "-t", help="AI dönüşüm komutu")
    parser.add_argument("--enrich", "-e", help="AI zenginleştirme komutu")
    parser.add_argument("--clean", "-c", nargs="+", help="Temizlenecek sütunlar")
    parser.add_argument("--drop-null", action="store_true", help="Null değerleri kaldır")
    parser.add_argument("--dedupe", nargs="*", help="Tekrar eden satırları kaldır")
    parser.add_argument("--demo", action="store_true", help="Demo modu")

    args = parser.parse_args()

    if args.demo:
        # Demo
        print("=" * 60)
        print("🔄 MiniMax-M2 Data Pipeline Demo")
        print("=" * 60)

        # Örnek veri
        data = {
            "ad": ["  Ali   ", "Ayşe", "Mehmet", "ali", None, "Fatma"],
            "sehir": ["İstanbul", "istanbul", "Ankara", "İstanbul", "İzmir", "ankara"],
            "yas": [25, 30, None, 25, 45, 28],
            "email": ["ali@test.com", "ayse@test.com", "mehmet@test.com", "ali@test.com", "can@test.com", "fatma@test.com"],
        }
        df = pd.DataFrame(data)

        print("\n📊 Örnek Veri:")
        print(df.to_string())

        # Pipeline oluştur
        pipeline = (
            PipelineBuilder("demo-pipeline")
            .config(checkpoint_enabled=False)
            .drop_null()
            .deduplicate(["email"])
            .transform(lambda d: d.assign(ad=d["ad"].str.strip().str.title()))
            .transform(lambda d: d.assign(sehir=d["sehir"].str.title()))
            .sort("ad")
            .build()
        )

        # Pipeline'ı çalıştır
        class InMemorySource(DataSource):
            def __init__(self, df):
                self.df = df

            def read(self):
                return self.df

            def write(self, df):
                self.df = df

        source = InMemorySource(df)
        result = pipeline.run(source)

        print("\n📊 Sonuç:")
        print(result.to_string())

        return

    if not args.input:
        parser.print_help()
        return

    # Pipeline oluştur
    builder = PipelineBuilder("cli-pipeline")

    if args.drop_null:
        builder.drop_null()

    if args.dedupe is not None:
        cols = args.dedupe if args.dedupe else None
        builder.deduplicate(cols)

    if args.clean:
        builder.ai_clean(*args.clean)

    if args.transform:
        builder.ai_transform(args.transform)

    if args.enrich:
        # Format: "yeni_sütun:kaynak_sütun1,kaynak_sütun2:komut"
        parts = args.enrich.split(":", 2)
        if len(parts) == 3:
            new_col, sources, instruction = parts
            builder.ai_enrich(instruction, new_col, sources.split(","))

    # Pipeline'ı çalıştır
    source = get_source(args.input)
    target = get_source(args.output) if args.output else None

    pipeline = builder.build()
    result = pipeline.run(source, target)

    if not args.output:
        print("\n📊 Sonuç (ilk 10 satır):")
        print(result.head(10).to_string())


if __name__ == "__main__":
    main()
