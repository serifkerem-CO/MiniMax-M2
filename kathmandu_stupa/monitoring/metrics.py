"""
📊 METRICS - Tapınak Metrikleri
===============================

Performans ve kullanım metrikleri toplama.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from collections import defaultdict
import statistics


@dataclass
class MetricPoint:
    """Tek metrik noktası"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class StupaMetrics:
    """Stupa metrikleri özeti"""
    # Sayaçlar
    total_pilgrimages: int = 0
    total_folds: int = 0
    total_nirvanas: int = 0
    total_council_decisions: int = 0
    total_tokens_processed: int = 0

    # Oranlar
    avg_fold_latency_ms: float = 0.0
    avg_consensus_score: float = 0.0
    avg_confidence: float = 0.0

    # Durumlar
    active_monks: int = 0
    errors_count: int = 0
    uptime_seconds: float = 0.0

    # Frekanslar
    frequency_distribution: Dict[int, int] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "counters": {
                "pilgrimages": self.total_pilgrimages,
                "folds": self.total_folds,
                "nirvanas": self.total_nirvanas,
                "councils": self.total_council_decisions,
                "tokens": self.total_tokens_processed,
            },
            "rates": {
                "avg_fold_latency_ms": self.avg_fold_latency_ms,
                "avg_consensus": self.avg_consensus_score,
                "avg_confidence": self.avg_confidence,
            },
            "status": {
                "active_monks": self.active_monks,
                "errors": self.errors_count,
                "uptime_seconds": self.uptime_seconds,
            },
            "frequencies": self.frequency_distribution,
        }


class MetricsCollector:
    """
    📊 Metrik Toplayıcı

    Tüm Stupa aktivitelerinin metriklerini toplar.
    """

    def __init__(self, retention_hours: int = 24):
        self.retention = timedelta(hours=retention_hours)
        self.start_time = datetime.now()

        # Metrik depoları
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timeseries: List[MetricPoint] = []

        # Özel izleyiciler
        self._fold_latencies: List[float] = []
        self._consensus_scores: List[float] = []
        self._confidences: List[float] = []
        self._frequency_counts: Dict[int, int] = defaultdict(int)

    def increment(self, name: str, value: int = 1, tags: Optional[Dict] = None):
        """Sayacı artır"""
        self._counters[name] += value
        self._record_point(name, float(value), tags)

    def gauge(self, name: str, value: float, tags: Optional[Dict] = None):
        """Gauge değeri ayarla"""
        self._gauges[name] = value
        self._record_point(name, value, tags)

    def histogram(self, name: str, value: float, tags: Optional[Dict] = None):
        """Histogram'a değer ekle"""
        self._histograms[name].append(value)
        self._record_point(name, value, tags)

    def timing(self, name: str, duration_ms: float, tags: Optional[Dict] = None):
        """Zamanlama metriği"""
        self.histogram(f"{name}_ms", duration_ms, tags)

    def _record_point(self, name: str, value: float, tags: Optional[Dict] = None):
        """Zaman serisi noktası kaydet"""
        point = MetricPoint(name=name, value=value, tags=tags or {})
        self._timeseries.append(point)
        self._cleanup_old_points()

    def _cleanup_old_points(self):
        """Eski noktaları temizle"""
        cutoff = datetime.now() - self.retention
        self._timeseries = [p for p in self._timeseries if p.timestamp > cutoff]

    # ===== STUPA-SPESİFİK METRİKLER =====

    def record_pilgrimage(self, duration_seconds: float, packets: int, nirvanas: int):
        """Hac yolculuğu metriği"""
        self.increment("pilgrimages_total")
        self.histogram("pilgrimage_duration", duration_seconds)
        self.histogram("packets_per_pilgrimage", packets)
        self.increment("nirvanas_total", nirvanas)

    def record_fold(self, latency_ms: float, monk: str, consensus: float):
        """Katlama metriği"""
        self.increment("folds_total")
        self._fold_latencies.append(latency_ms)
        self._consensus_scores.append(consensus)
        self.timing("fold_latency", latency_ms, {"monk": monk})

    def record_council_decision(self, consensus: float, monks_count: int):
        """Konsey kararı metriği"""
        self.increment("council_decisions_total")
        self._consensus_scores.append(consensus)
        self.gauge("active_monks", monks_count)

    def record_nirvana(self, frequency_hz: int, confidence: float):
        """Nirvana metriği"""
        self.increment("nirvanas_achieved")
        self._frequency_counts[frequency_hz] += 1
        self._confidences.append(confidence)

    def record_tokens(self, count: int):
        """Token sayısı"""
        self.increment("tokens_processed", count)

    def record_error(self, error_type: str):
        """Hata metriği"""
        self.increment("errors_total")
        self.increment(f"errors_{error_type}")

    # ===== SORGULAMA =====

    def get_counter(self, name: str) -> int:
        """Sayaç değeri al"""
        return self._counters.get(name, 0)

    def get_gauge(self, name: str) -> Optional[float]:
        """Gauge değeri al"""
        return self._gauges.get(name)

    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Histogram istatistikleri"""
        values = self._histograms.get(name, [])
        if not values:
            return {"count": 0}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "p95": self._percentile(values, 95),
            "p99": self._percentile(values, 99),
        }

    def _percentile(self, values: List[float], p: int) -> float:
        """Percentile hesapla"""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        idx = int(len(sorted_vals) * p / 100)
        return sorted_vals[min(idx, len(sorted_vals) - 1)]

    def get_summary(self) -> StupaMetrics:
        """Tüm metriklerin özeti"""
        uptime = (datetime.now() - self.start_time).total_seconds()

        return StupaMetrics(
            total_pilgrimages=self._counters.get("pilgrimages_total", 0),
            total_folds=self._counters.get("folds_total", 0),
            total_nirvanas=self._counters.get("nirvanas_achieved", 0),
            total_council_decisions=self._counters.get("council_decisions_total", 0),
            total_tokens_processed=self._counters.get("tokens_processed", 0),
            avg_fold_latency_ms=statistics.mean(self._fold_latencies) if self._fold_latencies else 0,
            avg_consensus_score=statistics.mean(self._consensus_scores) if self._consensus_scores else 0,
            avg_confidence=statistics.mean(self._confidences) if self._confidences else 0,
            active_monks=int(self._gauges.get("active_monks", 0)),
            errors_count=self._counters.get("errors_total", 0),
            uptime_seconds=uptime,
            frequency_distribution=dict(self._frequency_counts),
        )

    def get_timeseries(
        self,
        name: str,
        since: Optional[datetime] = None
    ) -> List[MetricPoint]:
        """Zaman serisi verileri"""
        points = [p for p in self._timeseries if p.name == name]

        if since:
            points = [p for p in points if p.timestamp >= since]

        return points

    def reset(self):
        """Tüm metrikleri sıfırla"""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timeseries.clear()
        self._fold_latencies.clear()
        self._consensus_scores.clear()
        self._confidences.clear()
        self._frequency_counts.clear()
        self.start_time = datetime.now()


# Global instance
_metrics: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Global metrics collector"""
    global _metrics
    if not _metrics:
        _metrics = MetricsCollector()
    return _metrics


# Demo
if __name__ == "__main__":
    metrics = get_metrics()

    # Örnek metrikler
    metrics.record_pilgrimage(45.2, 10, 8)
    metrics.record_fold(150.5, "claude", 0.92)
    metrics.record_fold(180.2, "gpt", 0.88)
    metrics.record_nirvana(963, 0.95)
    metrics.record_tokens(5000)

    summary = metrics.get_summary()
    print("📊 Stupa Metrikleri")
    print("=" * 50)
    print(summary.to_dict())
