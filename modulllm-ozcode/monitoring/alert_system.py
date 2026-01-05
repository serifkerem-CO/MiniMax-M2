"""
MODULllm.com - Alert System
Kritik durumlarında otomatik alert gönder
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


class AlertLevel:
    """Alert seviyeleri"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertChannel:
    """Alert kanalları"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    LOG = "log"


class MODULllmAlertSystem:
    """
    MODULllm.com Alert Sistemi

    Kritik durumları tespit edip alert gönderir
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.alert_history = []
        self.client = httpx.AsyncClient(timeout=10.0)

    async def send_email_alert(
        self,
        subject: str,
        body: str,
        level: str = AlertLevel.WARNING
    ):
        """Email alert gönder"""

        email_config = self.config.get("email", {})

        if not email_config.get("enabled"):
            print(f"⚠️  Email alerts disabled")
            return

        smtp_server = email_config.get("smtp_server", "smtp.gmail.com")
        smtp_port = email_config.get("smtp_port", 587)
        sender = email_config.get("sender")
        password = email_config.get("password")
        recipients = email_config.get("recipients", [])

        if not sender or not password or not recipients:
            print(f"❌ Email configuration incomplete")
            return

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"[{level}] MODULllm.com Alert: {subject}"

        # HTML body
        html_body = f"""
        <html>
        <body>
            <h2 style="color: {'red' if level == AlertLevel.CRITICAL else 'orange'};">
                🚨 MODULllm.com Alert
            </h2>
            <p><strong>Level:</strong> {level}</p>
            <p><strong>Time:</strong> {datetime.utcnow().isoformat()}</p>
            <hr>
            <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
                {body.replace('\n', '<br>')}
            </div>
            <hr>
            <p style="color: #888; font-size: 12px;">
                MODULllm.com Automated Alert System
            </p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, 'html'))

        # Send
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)

            print(f"✅ Email alert sent: {subject}")

        except Exception as e:
            print(f"❌ Failed to send email: {e}")

    async def send_slack_alert(
        self,
        message: str,
        level: str = AlertLevel.WARNING
    ):
        """Slack alert gönder"""

        slack_config = self.config.get("slack", {})

        if not slack_config.get("enabled"):
            print(f"⚠️  Slack alerts disabled")
            return

        webhook_url = slack_config.get("webhook_url")

        if not webhook_url:
            print(f"❌ Slack webhook URL not configured")
            return

        # Emoji based on level
        emoji_map = {
            AlertLevel.INFO: ":information_source:",
            AlertLevel.WARNING: ":warning:",
            AlertLevel.CRITICAL: ":rotating_light:"
        }

        emoji = emoji_map.get(level, ":question:")

        # Slack message format
        payload = {
            "text": f"{emoji} *MODULllm.com Alert*",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} MODULllm.com Alert - {level}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Time: {datetime.utcnow().isoformat()}"
                        }
                    ]
                }
            ]
        }

        try:
            response = await self.client.post(webhook_url, json=payload)

            if response.status_code == 200:
                print(f"✅ Slack alert sent: {level}")
            else:
                print(f"❌ Slack alert failed: HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ Failed to send Slack alert: {e}")

    async def send_webhook_alert(
        self,
        data: Dict[str, Any],
        level: str = AlertLevel.WARNING
    ):
        """Custom webhook alert gönder"""

        webhook_config = self.config.get("webhook", {})

        if not webhook_config.get("enabled"):
            return

        webhook_url = webhook_config.get("url")

        if not webhook_url:
            print(f"❌ Webhook URL not configured")
            return

        payload = {
            "platform": "MODULllm.com",
            "level": level,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        try:
            response = await self.client.post(webhook_url, json=payload)

            if response.status_code == 200:
                print(f"✅ Webhook alert sent: {level}")
            else:
                print(f"❌ Webhook alert failed: HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ Failed to send webhook alert: {e}")

    async def check_and_alert(
        self,
        metrics: Dict[str, Any],
        thresholds: Dict[str, Any] = None
    ):
        """
        Metrikleri kontrol et, threshold aşımlarında alert gönder

        Args:
            metrics: System metrics
            thresholds: Alert thresholds
        """

        if thresholds is None:
            thresholds = {
                "cpu_percent": 90,
                "memory_percent": 90,
                "disk_percent": 80,
                "response_time_ms": 5000,
            }

        alerts = []

        # CPU check
        cpu_percent = metrics.get("system", {}).get("cpu", {}).get("percent", 0)
        if cpu_percent > thresholds["cpu_percent"]:
            alerts.append({
                "level": AlertLevel.CRITICAL,
                "subject": "High CPU Usage",
                "message": f"CPU usage is {cpu_percent}% (threshold: {thresholds['cpu_percent']}%)"
            })

        # Memory check
        memory_percent = metrics.get("system", {}).get("memory", {}).get("percent", 0)
        if memory_percent > thresholds["memory_percent"]:
            alerts.append({
                "level": AlertLevel.CRITICAL,
                "subject": "High Memory Usage",
                "message": f"Memory usage is {memory_percent}% (threshold: {thresholds['memory_percent']}%)"
            })

        # Disk check
        disk_percent = metrics.get("system", {}).get("disk", {}).get("percent", 0)
        if disk_percent > thresholds["disk_percent"]:
            alerts.append({
                "level": AlertLevel.WARNING,
                "subject": "High Disk Usage",
                "message": f"Disk usage is {disk_percent}% (threshold: {thresholds['disk_percent']}%)"
            })

        # Service down check
        for service_name, service_data in metrics.get("services", {}).items():
            status = service_data.get("status", "")
            if "🔴" in status:
                alerts.append({
                    "level": AlertLevel.CRITICAL,
                    "subject": f"{service_name.upper()} Service Down",
                    "message": f"{service_name.upper()} is down: {service_data.get('error', 'Unknown error')}"
                })

        # Response time check
        platform_response_time = metrics.get("services", {}).get("platform", {}).get("response_time", 0)
        if platform_response_time * 1000 > thresholds["response_time_ms"]:
            alerts.append({
                "level": AlertLevel.WARNING,
                "subject": "Slow Response Time",
                "message": f"Platform response time: {platform_response_time*1000:.0f}ms (threshold: {thresholds['response_time_ms']}ms)"
            })

        # Send alerts
        for alert in alerts:
            # Check if we already alerted recently (prevent spam)
            if self._should_send_alert(alert):
                await self.send_alert(
                    subject=alert["subject"],
                    message=alert["message"],
                    level=alert["level"]
                )

                # Save to history
                self.alert_history.append({
                    **alert,
                    "timestamp": datetime.utcnow().isoformat()
                })

    def _should_send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Alert spam prevention
        Aynı alert'i 5 dakika içinde tekrar gönderme
        """

        from datetime import timedelta

        # Check last 5 minutes
        now = datetime.utcnow()
        recent_alerts = [
            a for a in self.alert_history
            if datetime.fromisoformat(a["timestamp"]) > now - timedelta(minutes=5)
        ]

        # Check if same alert exists
        for recent in recent_alerts:
            if recent["subject"] == alert["subject"]:
                return False

        return True

    async def send_alert(
        self,
        subject: str,
        message: str,
        level: str = AlertLevel.WARNING
    ):
        """
        Tüm aktif kanallara alert gönder
        """

        # Email
        if self.config.get("email", {}).get("enabled"):
            await self.send_email_alert(subject, message, level)

        # Slack
        if self.config.get("slack", {}).get("enabled"):
            slack_message = f"*{subject}*\n\n{message}"
            await self.send_slack_alert(slack_message, level)

        # Webhook
        if self.config.get("webhook", {}).get("enabled"):
            await self.send_webhook_alert(
                data={"subject": subject, "message": message},
                level=level
            )

        # Log (always)
        log_message = f"[{level}] {subject}: {message}"
        print(f"{datetime.utcnow().isoformat()} - {log_message}")

    async def close(self):
        """Cleanup"""
        await self.client.aclose()


# Test
async def test_alert_system():
    """Alert system test"""

    config = {
        "email": {
            "enabled": False,  # Set to True and configure for production
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender": "alerts@modulllm.com",
            "password": os.getenv("ALERT_EMAIL_PASSWORD"),
            "recipients": ["admin@modulllm.com"]
        },
        "slack": {
            "enabled": False,  # Set to True and configure for production
            "webhook_url": os.getenv("SLACK_WEBHOOK_URL")
        },
        "webhook": {
            "enabled": False,  # Set to True and configure for production
            "url": os.getenv("CUSTOM_WEBHOOK_URL")
        }
    }

    alert_system = MODULllmAlertSystem(config)

    print("\n🧪 Testing Alert System...\n")

    # Test alerts
    await alert_system.send_alert(
        subject="Test Alert",
        message="This is a test alert from MODULllm.com",
        level=AlertLevel.INFO
    )

    await alert_system.send_alert(
        subject="High CPU Usage",
        message="CPU usage has exceeded 90% for 5 minutes",
        level=AlertLevel.CRITICAL
    )

    await alert_system.close()

    print("\n✅ Alert system test complete!\n")


if __name__ == "__main__":
    asyncio.run(test_alert_system())
