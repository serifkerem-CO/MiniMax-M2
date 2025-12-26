"""
MiniMax-M2 Değerlendirme ve Benchmark Şablonu
=============================================
Model performansını değerlendirmek için araçlar.

Özellikler:
- Özel test setleri ile değerlendirme
- Gecikme ve throughput ölçümü
- Doğruluk metrikleri
- Karşılaştırmalı analiz
- HTML/JSON rapor oluşturma

Gereksinimler:
    pip install openai pandas tqdm matplotlib

Kullanım:
    python main.py
"""

import os
import json
import time
import statistics
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")


# ============================================================================
# Veri Yapıları
# ============================================================================

@dataclass
class TestCase:
    """Bir test vakası."""
    id: str
    prompt: str
    expected: Optional[str] = None
    category: str = "general"
    metadata: dict = field(default_factory=dict)


@dataclass
class TestResult:
    """Test sonucu."""
    test_id: str
    prompt: str
    response: str
    expected: Optional[str]
    latency_ms: float
    tokens_input: int
    tokens_output: int
    success: bool
    score: Optional[float] = None
    error: Optional[str] = None


@dataclass
class BenchmarkReport:
    """Benchmark raporu."""
    model_name: str
    timestamp: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    avg_latency_ms: float
    p50_latency_ms: float
    p90_latency_ms: float
    p99_latency_ms: float
    total_tokens: int
    tokens_per_second: float
    accuracy: Optional[float] = None
    results: list = field(default_factory=list)


# ============================================================================
# Değerlendirme Metrikleri
# ============================================================================

def exact_match(response: str, expected: str) -> float:
    """Tam eşleşme kontrolü."""
    return 1.0 if response.strip().lower() == expected.strip().lower() else 0.0


def contains_match(response: str, expected: str) -> float:
    """İçerme kontrolü."""
    return 1.0 if expected.strip().lower() in response.strip().lower() else 0.0


def keyword_match(response: str, expected: str) -> float:
    """Anahtar kelime eşleşmesi."""
    keywords = expected.lower().split(",")
    response_lower = response.lower()
    matches = sum(1 for kw in keywords if kw.strip() in response_lower)
    return matches / len(keywords) if keywords else 0.0


def code_execution_match(response: str, expected: str) -> float:
    """Kod çalıştırma sonucu kontrolü (dikkatli kullanın)."""
    try:
        # Markdown kod bloğunu çıkar
        code = response
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0]
        elif "```" in response:
            code = response.split("```")[1].split("```")[0]

        # Güvenli olmayan - sadece kontrollü ortamda kullanın
        local_vars = {}
        exec(code, {"__builtins__": {}}, local_vars)

        result = str(local_vars.get("result", local_vars))
        return 1.0 if expected.strip() in result else 0.0
    except Exception:
        return 0.0


# Metrik registry
METRICS = {
    "exact": exact_match,
    "contains": contains_match,
    "keyword": keyword_match,
    "code_exec": code_execution_match,
}


# ============================================================================
# Benchmark Motoru
# ============================================================================

class BenchmarkEngine:
    """Model değerlendirme motoru."""

    def __init__(
        self,
        api_key: str = API_KEY,
        base_url: str = API_BASE_URL,
        model_name: str = MODEL_NAME
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
        self.results: list[TestResult] = []

    def run_single_test(
        self,
        test: TestCase,
        metric: str = "contains",
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> TestResult:
        """Tek bir test çalıştır."""
        start_time = time.time()
        error = None
        response_text = ""
        tokens_in = 0
        tokens_out = 0

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": test.prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            response_text = response.choices[0].message.content
            tokens_in = response.usage.prompt_tokens
            tokens_out = response.usage.completion_tokens
            success = True

        except Exception as e:
            error = str(e)
            success = False

        latency = (time.time() - start_time) * 1000

        # Skor hesapla
        score = None
        if success and test.expected and metric in METRICS:
            score = METRICS[metric](response_text, test.expected)

        return TestResult(
            test_id=test.id,
            prompt=test.prompt,
            response=response_text,
            expected=test.expected,
            latency_ms=latency,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            success=success,
            score=score,
            error=error,
        )

    def run_benchmark(
        self,
        tests: list[TestCase],
        metric: str = "contains",
        concurrent: int = 1,
        temperature: float = 0.1,
        max_tokens: int = 1024,
        progress: bool = True
    ) -> BenchmarkReport:
        """Benchmark çalıştır."""
        self.results = []

        if progress and TQDM_AVAILABLE:
            pbar = tqdm(total=len(tests), desc="Değerlendirme")
        else:
            pbar = None
            print(f"Değerlendirme başlıyor: {len(tests)} test")

        if concurrent > 1:
            # Paralel çalıştırma
            with ThreadPoolExecutor(max_workers=concurrent) as executor:
                futures = {
                    executor.submit(
                        self.run_single_test,
                        test, metric, temperature, max_tokens
                    ): test
                    for test in tests
                }

                for future in as_completed(futures):
                    result = future.result()
                    self.results.append(result)
                    if pbar:
                        pbar.update(1)
        else:
            # Sıralı çalıştırma
            for test in tests:
                result = self.run_single_test(test, metric, temperature, max_tokens)
                self.results.append(result)
                if pbar:
                    pbar.update(1)
                elif not progress:
                    print(f"  [{result.test_id}] {'✓' if result.success else '✗'}")

        if pbar:
            pbar.close()

        return self._generate_report()

    def _generate_report(self) -> BenchmarkReport:
        """Rapor oluştur."""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        latencies = [r.latency_ms for r in successful]
        scores = [r.score for r in successful if r.score is not None]

        # Latency istatistikleri
        if latencies:
            sorted_lat = sorted(latencies)
            avg_lat = statistics.mean(latencies)
            p50_lat = sorted_lat[len(sorted_lat) // 2]
            p90_lat = sorted_lat[int(len(sorted_lat) * 0.9)]
            p99_lat = sorted_lat[int(len(sorted_lat) * 0.99)]
        else:
            avg_lat = p50_lat = p90_lat = p99_lat = 0

        # Token istatistikleri
        total_tokens = sum(r.tokens_input + r.tokens_output for r in successful)
        total_time = sum(r.latency_ms for r in successful) / 1000  # saniye
        tps = total_tokens / total_time if total_time > 0 else 0

        # Doğruluk
        accuracy = statistics.mean(scores) if scores else None

        return BenchmarkReport(
            model_name=self.model_name,
            timestamp=datetime.now().isoformat(),
            total_tests=len(self.results),
            successful_tests=len(successful),
            failed_tests=len(failed),
            avg_latency_ms=avg_lat,
            p50_latency_ms=p50_lat,
            p90_latency_ms=p90_lat,
            p99_latency_ms=p99_lat,
            total_tokens=total_tokens,
            tokens_per_second=tps,
            accuracy=accuracy,
            results=[asdict(r) for r in self.results],
        )

    def save_report(self, report: BenchmarkReport, filepath: str):
        """Raporu JSON olarak kaydet."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False)
        print(f"📊 Rapor kaydedildi: {filepath}")

    def print_report(self, report: BenchmarkReport):
        """Raporu konsola yazdır."""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK RAPORU")
        print("=" * 60)
        print(f"Model: {report.model_name}")
        print(f"Tarih: {report.timestamp}")
        print("-" * 60)
        print(f"Toplam Test:      {report.total_tests}")
        print(f"Başarılı:         {report.successful_tests}")
        print(f"Başarısız:        {report.failed_tests}")
        print(f"Başarı Oranı:     {report.successful_tests/report.total_tests*100:.1f}%")
        print("-" * 60)
        print(f"Ortalama Gecikme: {report.avg_latency_ms:.0f}ms")
        print(f"P50 Gecikme:      {report.p50_latency_ms:.0f}ms")
        print(f"P90 Gecikme:      {report.p90_latency_ms:.0f}ms")
        print(f"P99 Gecikme:      {report.p99_latency_ms:.0f}ms")
        print("-" * 60)
        print(f"Toplam Token:     {report.total_tokens}")
        print(f"Token/Saniye:     {report.tokens_per_second:.1f}")

        if report.accuracy is not None:
            print("-" * 60)
            print(f"Doğruluk:         {report.accuracy*100:.1f}%")

        print("=" * 60)

    def plot_latencies(self, report: BenchmarkReport, save_path: Optional[str] = None):
        """Gecikme dağılımı grafiği."""
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib gerekli: pip install matplotlib")
            return

        latencies = [r["latency_ms"] for r in report.results if r["success"]]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        # Histogram
        ax1.hist(latencies, bins=30, edgecolor="black")
        ax1.set_xlabel("Gecikme (ms)")
        ax1.set_ylabel("Frekans")
        ax1.set_title("Gecikme Dağılımı")
        ax1.axvline(report.avg_latency_ms, color="red", linestyle="--", label=f"Ort: {report.avg_latency_ms:.0f}ms")
        ax1.legend()

        # Box plot
        ax2.boxplot(latencies)
        ax2.set_ylabel("Gecikme (ms)")
        ax2.set_title("Gecikme Box Plot")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
            print(f"📈 Grafik kaydedildi: {save_path}")
        else:
            plt.show()


# ============================================================================
# Örnek Test Setleri
# ============================================================================

def get_sample_tests() -> list[TestCase]:
    """Örnek test seti."""
    return [
        TestCase(
            id="math_1",
            prompt="25 + 37 kaçtır? Sadece sayıyı yaz.",
            expected="62",
            category="math"
        ),
        TestCase(
            id="math_2",
            prompt="144'ün karekökü kaçtır? Sadece sayıyı yaz.",
            expected="12",
            category="math"
        ),
        TestCase(
            id="fact_1",
            prompt="Python hangi yıl oluşturuldu? Sadece yılı yaz.",
            expected="1991",
            category="facts"
        ),
        TestCase(
            id="fact_2",
            prompt="Türkiye'nin başkenti neresidir?",
            expected="Ankara",
            category="facts"
        ),
        TestCase(
            id="code_1",
            prompt="Python'da 'hello world' yazdıran tek satır kod yaz.",
            expected="print",
            category="code"
        ),
        TestCase(
            id="code_2",
            prompt="Python'da bir listenin uzunluğunu bulmak için hangi fonksiyon kullanılır?",
            expected="len",
            category="code"
        ),
        TestCase(
            id="reason_1",
            prompt="Bir çiftçinin 17 koyunu var. 9'u hariç hepsi öldü. Kaç koyun kaldı?",
            expected="9",
            category="reasoning"
        ),
        TestCase(
            id="reason_2",
            prompt="Ali'nin 3 elması var. 2 tane daha aldı. Kaç elması oldu?",
            expected="5",
            category="reasoning"
        ),
        TestCase(
            id="lang_1",
            prompt="'Merhaba dünya' cümlesini İngilizce'ye çevir.",
            expected="hello world",
            category="translation"
        ),
        TestCase(
            id="lang_2",
            prompt="'Thank you' ne demek? Türkçe karşılığını yaz.",
            expected="teşekkür",
            category="translation"
        ),
    ]


def get_coding_tests() -> list[TestCase]:
    """Kod odaklı test seti."""
    return [
        TestCase(
            id="py_1",
            prompt="Python'da 1'den 10'a kadar sayıları yazdıran for döngüsü yaz.",
            expected="for,range,print",
            category="python"
        ),
        TestCase(
            id="py_2",
            prompt="Python'da bir sayının çift olup olmadığını kontrol eden fonksiyon yaz.",
            expected="def,%,2,return",
            category="python"
        ),
        TestCase(
            id="py_3",
            prompt="Python'da bir listeyi ters çeviren kod yaz.",
            expected="reverse,[::-1]",
            category="python"
        ),
        TestCase(
            id="js_1",
            prompt="JavaScript'te 'hello' yazdıran kod yaz.",
            expected="console.log",
            category="javascript"
        ),
        TestCase(
            id="algo_1",
            prompt="Binary search algoritmasını açıkla. Zaman karmaşıklığı nedir?",
            expected="O(log n)",
            category="algorithms"
        ),
    ]


# ============================================================================
# Ana Fonksiyon
# ============================================================================

def main():
    """Demo benchmark çalıştır."""
    print("=" * 60)
    print("MiniMax-M2 Değerlendirme Demo")
    print("=" * 60)

    # Motor oluştur
    engine = BenchmarkEngine()

    # Test seti seç
    print("\nTest Setleri:")
    print("  1. Genel Test Seti (10 test)")
    print("  2. Kod Test Seti (5 test)")
    print("  3. Tümü (15 test)")

    choice = input("\nSeçiminiz (1-3): ").strip()

    if choice == "1":
        tests = get_sample_tests()
    elif choice == "2":
        tests = get_coding_tests()
    else:
        tests = get_sample_tests() + get_coding_tests()

    print(f"\n{len(tests)} test çalıştırılacak...")

    # Benchmark çalıştır
    report = engine.run_benchmark(
        tests,
        metric="contains",
        concurrent=1,
        temperature=0.1,
    )

    # Raporu yazdır
    engine.print_report(report)

    # Raporu kaydet
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    engine.save_report(report, str(output_dir / f"benchmark_{timestamp}.json"))

    # Grafik (opsiyonel)
    if MATPLOTLIB_AVAILABLE:
        engine.plot_latencies(report, str(output_dir / f"latency_{timestamp}.png"))


if __name__ == "__main__":
    main()
