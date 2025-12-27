"""
🌐 API - Tapınak REST API
=========================

FastAPI tabanlı REST API server.
Tüm Stupa fonksiyonlarına HTTP erişimi.
"""

from .server import create_app, run_server

__all__ = ["create_app", "run_server"]
