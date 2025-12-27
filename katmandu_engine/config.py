"""
KATMANDU CONFIG - Yapilandirma Yonetimi
========================================
Environment degiskenleri ve yapilandirma yonetimi.

Kullanim:
    from katmandu_engine.config import config

    # API key'leri kontrol et
    if config.claude.is_configured:
        print("Claude hazir!")

    # Tum yapılandırmayi goster
    print(config.to_dict())
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class ProviderConfig:
    """Tek bir provider'in yapilandirmasi"""
    name: str
    api_key: str = ""
    base_url: Optional[str] = None
    model_id: Optional[str] = None
    enabled: bool = True

    @property
    def is_configured(self) -> bool:
        """API key mevcut ve gecerli mi?"""
        return bool(self.api_key and len(self.api_key) > 10)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "configured": self.is_configured,
            "has_custom_url": self.base_url is not None,
            "model": self.model_id,
            "enabled": self.enabled
        }


@dataclass
class KatmanduConfig:
    """
    Katmandu Engine Ana Yapilandirmasi

    Environment degiskenlerinden otomatik yukler.
    """

    # Server ayarlari
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Layer ayarlari
    use_real_api: bool = True
    default_intensity: int = 5
    parallel_processing: bool = True

    # Provider yapılandırmaları
    claude: ProviderConfig = field(default_factory=lambda: ProviderConfig("claude"))
    openai: ProviderConfig = field(default_factory=lambda: ProviderConfig("openai"))
    gemini: ProviderConfig = field(default_factory=lambda: ProviderConfig("gemini"))
    mistral: ProviderConfig = field(default_factory=lambda: ProviderConfig("mistral"))
    deepseek: ProviderConfig = field(default_factory=lambda: ProviderConfig("deepseek"))
    llama: ProviderConfig = field(default_factory=lambda: ProviderConfig("llama"))
    minimax: ProviderConfig = field(default_factory=lambda: ProviderConfig("minimax"))

    # N8N ayarlari
    n8n_host: str = "http://localhost:5678"
    n8n_api_key: str = ""

    def __post_init__(self):
        """Environment'tan yukle"""
        self._load_from_env()

    def _load_from_env(self):
        """Environment degiskenlerinden yukle"""
        # Server
        self.host = os.environ.get("KATMANDU_HOST", self.host)
        self.port = int(os.environ.get("KATMANDU_PORT", self.port))
        self.debug = os.environ.get("KATMANDU_DEBUG", "").lower() == "true"

        # Layer
        self.use_real_api = os.environ.get("USE_REAL_API", "true").lower() == "true"
        self.default_intensity = int(os.environ.get("DEFAULT_INTENSITY", self.default_intensity))

        # Claude
        self.claude.api_key = os.environ.get("CLAUDE_API_KEY", "")
        self.claude.base_url = os.environ.get("CLAUDE_BASE_URL")
        self.claude.model_id = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")

        # OpenAI
        self.openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.openai.base_url = os.environ.get("OPENAI_BASE_URL")
        self.openai.model_id = os.environ.get("OPENAI_MODEL", "gpt-4o")

        # Gemini
        self.gemini.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.gemini.base_url = os.environ.get("GEMINI_BASE_URL")
        self.gemini.model_id = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

        # Mistral
        self.mistral.api_key = os.environ.get("MISTRAL_API_KEY", "")
        self.mistral.base_url = os.environ.get("MISTRAL_BASE_URL")
        self.mistral.model_id = os.environ.get("MISTRAL_MODEL", "mistral-large-latest")

        # DeepSeek
        self.deepseek.api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.deepseek.base_url = os.environ.get("DEEPSEEK_BASE_URL")
        self.deepseek.model_id = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

        # Llama (Together AI veya Groq)
        self.llama.api_key = os.environ.get("LLAMA_API_KEY", "") or os.environ.get("TOGETHER_API_KEY", "")
        self.llama.base_url = os.environ.get("LLAMA_BASE_URL")
        self.llama.model_id = os.environ.get("LLAMA_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo")

        # MiniMax
        self.minimax.api_key = os.environ.get("MINIMAX_API_KEY", "")
        self.minimax.base_url = os.environ.get("MINIMAX_BASE_URL")
        self.minimax.model_id = os.environ.get("MINIMAX_MODEL", "MiniMax-Text-01")

        # N8N
        self.n8n_host = os.environ.get("N8N_HOST", self.n8n_host)
        self.n8n_api_key = os.environ.get("N8N_API_KEY", "")

    def get_configured_providers(self) -> list[str]:
        """Yapilandirilmis provider listesi"""
        providers = []
        for name in ["claude", "openai", "gemini", "mistral", "deepseek", "llama", "minimax"]:
            provider = getattr(self, name)
            if provider.is_configured and provider.enabled:
                providers.append(name)
        return providers

    def get_provider_summary(self) -> dict:
        """Tum provider durumlarini ozetle"""
        return {
            "claude": self.claude.to_dict(),
            "openai": self.openai.to_dict(),
            "gemini": self.gemini.to_dict(),
            "mistral": self.mistral.to_dict(),
            "deepseek": self.deepseek.to_dict(),
            "llama": self.llama.to_dict(),
            "minimax": self.minimax.to_dict()
        }

    def to_dict(self) -> dict:
        """Tum yapilandirmayi dict olarak dondur"""
        return {
            "server": {
                "host": self.host,
                "port": self.port,
                "debug": self.debug
            },
            "layers": {
                "use_real_api": self.use_real_api,
                "default_intensity": self.default_intensity,
                "parallel_processing": self.parallel_processing
            },
            "providers": self.get_provider_summary(),
            "configured_providers": self.get_configured_providers(),
            "n8n": {
                "host": self.n8n_host,
                "configured": bool(self.n8n_api_key)
            }
        }

    def print_status(self):
        """Yapilandirma durumunu yazdir"""
        print("\n" + "=" * 50)
        print("   KATMANDU ENGINE - YAPILANDIRMA DURUMU")
        print("=" * 50)

        configured = self.get_configured_providers()
        print(f"\n   Yapilandirilmis Provider'lar ({len(configured)}/7):")

        for name in ["claude", "openai", "gemini", "mistral", "deepseek", "llama", "minimax"]:
            provider = getattr(self, name)
            status = "aktif" if provider.is_configured else "yapilandirilmamis"
            emoji = "V" if provider.is_configured else "X"
            print(f"   [{emoji}] {name.upper()}: {status}")

        print(f"\n   API Modu: {'GERCEK' if self.use_real_api else 'MOCK'}")
        print(f"   Varsayilan Yogunluk: {self.default_intensity} rahip")
        print("=" * 50 + "\n")


# Global config instance
config = KatmanduConfig()


def load_dotenv(env_path: Optional[str] = None):
    """
    .env dosyasindan yukle

    Args:
        env_path: .env dosya yolu (None = otomatik bul)
    """
    if env_path is None:
        # Proje kokunde ara
        possible_paths = [
            Path(".env"),
            Path(__file__).parent / ".env",
            Path(__file__).parent.parent / ".env"
        ]
        for path in possible_paths:
            if path.exists():
                env_path = str(path)
                break

    if env_path and Path(env_path).exists():
        print(f"   .env yukleniyor: {env_path}")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value

        # Config'i yeniden yukle
        config._load_from_env()
        print("   .env yuklendi!")
    else:
        print("   .env dosyasi bulunamadi, environment degiskenleri kullaniliyor")


# Kullanim kolayligi icin
def get_config() -> KatmanduConfig:
    """Global config'i dondur"""
    return config
