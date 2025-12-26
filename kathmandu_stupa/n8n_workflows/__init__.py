"""
⚙️ N8N WORKFLOWS - Dua Çarkları Otomasyonu
==========================================

N8N entegrasyonu için workflow tanımları.
Her workflow bir "Dua Çarkı" temsil eder.
"""

from .prayer_wheels import PrayerWheelWorkflow, create_forge_workflow
from .webhooks import WebhookConfig, setup_stupa_webhooks

__all__ = [
    "PrayerWheelWorkflow",
    "create_forge_workflow",
    "WebhookConfig",
    "setup_stupa_webhooks",
]
