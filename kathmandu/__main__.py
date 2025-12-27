"""
🛕 Kathmandu Engine - Modül giriş noktası

Kullanım:
    python -m kathmandu [komut]

Örnekler:
    python -m kathmandu ritual "veri"
    python -m kathmandu enlighten "soru"
    python -m kathmandu serve
"""

from .cli import main

if __name__ == "__main__":
    main()
