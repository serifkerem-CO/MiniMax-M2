"""
⚙️ CONFIG - Tapınak Konfigürasyonu
==================================

Merkezi konfigürasyon yönetimi.
Çevre değişkenleri, dosya ve varsayılanlar.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import json


@dataclass
class LLMProviderConfig:
    """LLM sağlayıcı konfigürasyonu"""
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: str = ""
    enabled: bool = True
    weight: float = 1.0
    timeout: int = 30
    max_retries: int = 3


@dataclass
class StorageConfig:
    """Storage konfigürasyonu"""
    backend: str = "json"  # json veya sqlite
    base_path: str = "./stupa_data"
    max_cache_size: int = 1000
    auto_backup: bool = True
    backup_interval_hours: int = 24


@dataclass
class DashboardConfig:
    """Dashboard konfigürasyonu"""
    host: str = "0.0.0.0"
    port: int = 8888
    websocket_enabled: bool = True
    refresh_interval_ms: int = 2000
    theme: str = "mandala"


@dataclass
class APIConfig:
    """API server konfigürasyonu"""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    api_key: Optional[str] = None
    rate_limit: int = 100  # per minute
    docs_enabled: bool = True


@dataclass
class StupaConfig:
    """Ana Stupa konfigürasyonu"""
    # Katman ayarları
    max_fold_depth: int = 7
    default_num_folds: int = 3
    sacred_frequency: int = 963

    # LLM ayarları
    mock_mode: bool = True  # True = sahte yanıtlar kullan
    parallel_monks: int = 3  # Aynı anda kaç rahip çalışsın
    voting_method: str = "weighted"  # majority, weighted, best

    # Performans
    batch_size: int = 10
    timeout_seconds: int = 60

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Alt konfigürasyonlar
    storage: StorageConfig = field(default_factory=StorageConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    api: APIConfig = field(default_factory=APIConfig)
    providers: Dict[str, LLMProviderConfig] = field(default_factory=dict)

    def __post_init__(self):
        """Varsayılan provider'ları kur"""
        if not self.providers:
            self.providers = self._default_providers()

    def _default_providers(self) -> Dict[str, LLMProviderConfig]:
        """Varsayılan LLM provider'ları"""
        return {
            "claude": LLMProviderConfig(
                name="Claude",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                default_model="claude-3-opus-20240229",
                weight=1.2,
            ),
            "gpt": LLMProviderConfig(
                name="GPT",
                api_key=os.getenv("OPENAI_API_KEY"),
                default_model="gpt-4-turbo",
                weight=0.9,
            ),
            "minimax": LLMProviderConfig(
                name="MiniMax",
                api_key=os.getenv("MINIMAX_API_KEY"),
                base_url="https://api.minimax.chat/v1/text/chatcompletion_v2",
                default_model="MiniMax-M2",
                weight=1.1,
            ),
            "mistral": LLMProviderConfig(
                name="Mistral",
                api_key=os.getenv("MISTRAL_API_KEY"),
                default_model="mistral-large-latest",
                weight=1.0,
            ),
            "deepseek": LLMProviderConfig(
                name="DeepSeek",
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                default_model="deepseek-chat",
                weight=1.5,
            ),
            "gemini": LLMProviderConfig(
                name="Gemini",
                api_key=os.getenv("GOOGLE_API_KEY"),
                default_model="gemini-pro",
                weight=1.3,
            ),
            "llama": LLMProviderConfig(
                name="Llama",
                base_url="http://localhost:11434",
                default_model="llama3",
                weight=1.4,
            ),
        }


class ConfigManager:
    """
    ⚙️ Konfigürasyon Yöneticisi

    Öncelik sırası:
    1. Çevre değişkenleri
    2. Konfigürasyon dosyası
    3. Varsayılanlar
    """

    DEFAULT_CONFIG_PATH = Path("./stupa_config.json")
    ENV_PREFIX = "STUPA_"

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: Optional[StupaConfig] = None

    def load(self) -> StupaConfig:
        """Konfigürasyonu yükle"""
        if self._config:
            return self._config

        # Varsayılanlarla başla
        config_dict: Dict[str, Any] = {}

        # Dosyadan oku
        if self.config_path.exists():
            with open(self.config_path) as f:
                file_config = json.load(f)
                config_dict.update(file_config)

        # Çevre değişkenlerini uygula
        config_dict = self._apply_env_vars(config_dict)

        # StupaConfig oluştur
        self._config = self._dict_to_config(config_dict)
        return self._config

    def _apply_env_vars(self, config: Dict) -> Dict:
        """Çevre değişkenlerini uygula"""
        env_mapping = {
            f"{self.ENV_PREFIX}MOCK_MODE": ("mock_mode", lambda x: x.lower() == "true"),
            f"{self.ENV_PREFIX}LOG_LEVEL": ("log_level", str),
            f"{self.ENV_PREFIX}SACRED_FREQUENCY": ("sacred_frequency", int),
            f"{self.ENV_PREFIX}MAX_FOLD_DEPTH": ("max_fold_depth", int),
            f"{self.ENV_PREFIX}STORAGE_BACKEND": ("storage.backend", str),
            f"{self.ENV_PREFIX}API_PORT": ("api.port", int),
            f"{self.ENV_PREFIX}DASHBOARD_PORT": ("dashboard.port", int),
        }

        for env_key, (config_key, converter) in env_mapping.items():
            if env_key in os.environ:
                value = converter(os.environ[env_key])
                self._set_nested(config, config_key, value)

        return config

    def _set_nested(self, d: Dict, key: str, value: Any):
        """İç içe dict'e değer ata"""
        keys = key.split(".")
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def _dict_to_config(self, d: Dict) -> StupaConfig:
        """Dict'ten StupaConfig oluştur"""
        # Alt konfigürasyonları oluştur
        storage = StorageConfig(**d.get("storage", {}))
        dashboard = DashboardConfig(**d.get("dashboard", {}))
        api = APIConfig(**d.get("api", {}))

        # Provider'ları oluştur
        providers = {}
        for name, pconfig in d.get("providers", {}).items():
            providers[name] = LLMProviderConfig(**pconfig)

        # Ana konfigürasyon
        main_keys = ["max_fold_depth", "default_num_folds", "sacred_frequency",
                     "mock_mode", "parallel_monks", "voting_method",
                     "batch_size", "timeout_seconds", "log_level", "log_file"]

        main_config = {k: d[k] for k in main_keys if k in d}

        return StupaConfig(
            **main_config,
            storage=storage,
            dashboard=dashboard,
            api=api,
            providers=providers if providers else None,
        )

    def save(self, config: StupaConfig):
        """Konfigürasyonu kaydet"""
        config_dict = {
            "max_fold_depth": config.max_fold_depth,
            "default_num_folds": config.default_num_folds,
            "sacred_frequency": config.sacred_frequency,
            "mock_mode": config.mock_mode,
            "parallel_monks": config.parallel_monks,
            "voting_method": config.voting_method,
            "batch_size": config.batch_size,
            "timeout_seconds": config.timeout_seconds,
            "log_level": config.log_level,
            "log_file": config.log_file,
            "storage": {
                "backend": config.storage.backend,
                "base_path": config.storage.base_path,
                "max_cache_size": config.storage.max_cache_size,
                "auto_backup": config.storage.auto_backup,
            },
            "dashboard": {
                "host": config.dashboard.host,
                "port": config.dashboard.port,
                "theme": config.dashboard.theme,
            },
            "api": {
                "host": config.api.host,
                "port": config.api.port,
                "rate_limit": config.api.rate_limit,
            },
        }

        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

        self._config = config

    def get(self) -> StupaConfig:
        """Mevcut konfigürasyonu al (lazy load)"""
        if not self._config:
            return self.load()
        return self._config

    def reset(self):
        """Varsayılanlara sıfırla"""
        self._config = StupaConfig()
        self.save(self._config)


# Global instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> StupaConfig:
    """Global konfigürasyonu al"""
    global _config_manager
    if not _config_manager:
        _config_manager = ConfigManager()
    return _config_manager.get()


def init_config(config_path: Optional[str] = None) -> StupaConfig:
    """Konfigürasyonu başlat"""
    global _config_manager
    path = Path(config_path) if config_path else None
    _config_manager = ConfigManager(path)
    return _config_manager.load()


# Demo
if __name__ == "__main__":
    config = get_config()
    print("⚙️ Stupa Konfigürasyonu")
    print("=" * 50)
    print(f"Mock Mode: {config.mock_mode}")
    print(f"Sacred Frequency: {config.sacred_frequency} Hz")
    print(f"Max Fold Depth: {config.max_fold_depth}")
    print(f"Storage Backend: {config.storage.backend}")
    print(f"API Port: {config.api.port}")
    print(f"Dashboard Port: {config.dashboard.port}")
    print(f"\nProviders:")
    for name, provider in config.providers.items():
        status = "✅" if provider.api_key else "⚠️ (no key)"
        print(f"  - {name}: {provider.default_model} {status}")
