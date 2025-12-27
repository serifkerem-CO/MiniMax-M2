"""
📝 LOGGER - Tapınak Günlüğü
===========================

Yapılandırılmış logging sistemi.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import json


class StupaFormatter(logging.Formatter):
    """Özel log formatı"""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m',
    }

    LAYER_ICONS = {
        'TOPRAK': '🪨',
        'SU': '🌊',
        'ATES': '🔥',
        'HAVA': '🌬️',
        'ETER': '🌌',
        'STUPA': '🛕',
        'COUNCIL': '🎭',
        'MANTRA': '📿',
    }

    def __init__(self, use_colors: bool = True, use_icons: bool = True):
        super().__init__()
        self.use_colors = use_colors
        self.use_icons = use_icons

    def format(self, record: logging.LogRecord) -> str:
        # Zaman
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]

        # Seviye
        level = record.levelname
        if self.use_colors:
            color = self.COLORS.get(level, '')
            reset = self.COLORS['RESET']
            level_str = f"{color}{level:8}{reset}"
        else:
            level_str = f"{level:8}"

        # İkon
        icon = ''
        if self.use_icons and hasattr(record, 'layer'):
            icon = self.LAYER_ICONS.get(record.layer, '') + ' '

        # Mesaj
        message = record.getMessage()

        # Extra data
        extra = ''
        if hasattr(record, 'extra_data') and record.extra_data:
            extra = f" | {json.dumps(record.extra_data, ensure_ascii=False)}"

        return f"[{timestamp}] {level_str} {icon}{message}{extra}"


class StupaLogger:
    """
    📝 Stupa Logger

    Katman-aware, yapılandırılmış logging.
    """

    def __init__(
        self,
        name: str = "stupa",
        level: str = "INFO",
        log_file: Optional[str] = None,
        use_colors: bool = True
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers = []  # Clear existing

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StupaFormatter(use_colors=use_colors))
        self.logger.addHandler(console_handler)

        # File handler (opsiyonel)
        if log_file:
            file_path = Path(log_file)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(StupaFormatter(use_colors=False, use_icons=False))
            self.logger.addHandler(file_handler)

    def _log(
        self,
        level: int,
        message: str,
        layer: Optional[str] = None,
        extra_data: Optional[Dict] = None
    ):
        """Log yaz"""
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "",
            0,
            message,
            None,
            None,
        )
        if layer:
            record.layer = layer
        if extra_data:
            record.extra_data = extra_data

        self.logger.handle(record)

    def debug(self, message: str, layer: str = None, **kwargs):
        self._log(logging.DEBUG, message, layer, kwargs if kwargs else None)

    def info(self, message: str, layer: str = None, **kwargs):
        self._log(logging.INFO, message, layer, kwargs if kwargs else None)

    def warning(self, message: str, layer: str = None, **kwargs):
        self._log(logging.WARNING, message, layer, kwargs if kwargs else None)

    def error(self, message: str, layer: str = None, **kwargs):
        self._log(logging.ERROR, message, layer, kwargs if kwargs else None)

    def critical(self, message: str, layer: str = None, **kwargs):
        self._log(logging.CRITICAL, message, layer, kwargs if kwargs else None)

    # Katman kısayolları
    def toprak(self, message: str, **kwargs):
        self.info(message, layer="TOPRAK", **kwargs)

    def su(self, message: str, **kwargs):
        self.info(message, layer="SU", **kwargs)

    def ates(self, message: str, **kwargs):
        self.info(message, layer="ATES", **kwargs)

    def hava(self, message: str, **kwargs):
        self.info(message, layer="HAVA", **kwargs)

    def eter(self, message: str, **kwargs):
        self.info(message, layer="ETER", **kwargs)

    def stupa(self, message: str, **kwargs):
        self.info(message, layer="STUPA", **kwargs)

    def council(self, message: str, **kwargs):
        self.info(message, layer="COUNCIL", **kwargs)

    def mantra(self, message: str, **kwargs):
        self.info(message, layer="MANTRA", **kwargs)


# Factory
def create_logger(
    name: str = "stupa",
    level: str = "INFO",
    log_file: Optional[str] = None
) -> StupaLogger:
    """Logger oluştur"""
    return StupaLogger(name=name, level=level, log_file=log_file)


# Global instance
_logger: Optional[StupaLogger] = None


def get_logger() -> StupaLogger:
    """Global logger"""
    global _logger
    if not _logger:
        _logger = create_logger()
    return _logger


# Demo
if __name__ == "__main__":
    log = get_logger()

    log.stupa("Tapınak başlatılıyor...")
    log.toprak("Veri toplama başladı", packets=10)
    log.su("Arınma akışı aktif", tokens_cleaned=150)
    log.ates("Simya ocağı ısınıyor", monks=7)
    log.hava("Rüzgar bayrakları hazır")
    log.eter("Nirvana ulaşıldı", frequency=963, confidence=0.95)
    log.council("Konsey karar verdi", winner="claude", consensus=0.88)
    log.warning("Düşük konsensüs", layer="COUNCIL", score=0.45)
    log.error("API bağlantı hatası", layer="STUPA", provider="mistral")
