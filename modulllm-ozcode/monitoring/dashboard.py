"""
MODULllm.com - Real-Time Monitoring Dashboard
Tüm sistemlerin durumunu izle, metrik topla, alert gönder
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, List
import psutil
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich import box


console = Console()


class MODULllmMonitor:
    """
    MODULllm.com Real-time System Monitor
    """

    def __init__(
        self,
        platform_url: str = "http://localhost:8000",
        n8n_url: str = "http://localhost:5678"
    ):
        self.platform_url = platform_url
        self.n8n_url = n8n_url
        self.metrics_history = []
        self.client = httpx.AsyncClient(timeout=10.0)

    async def check_platform_health(self) -> Dict[str, Any]:
        """Platform API health check"""
        try:
            response = await self.client.get(f"{self.platform_url}/health")

            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "🟢 UP",
                    "details": data,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "🟡 DEGRADED",
                    "error": f"HTTP {response.status_code}",
                    "response_time": 0
                }

        except httpx.ConnectError:
            return {
                "status": "🔴 DOWN",
                "error": "Connection refused",
                "response_time": 0
            }
        except Exception as e:
            return {
                "status": "🔴 ERROR",
                "error": str(e),
                "response_time": 0
            }

    async def check_n8n_health(self) -> Dict[str, Any]:
        """n8n health check"""
        try:
            response = await self.client.get(self.n8n_url)

            if response.status_code in [200, 401]:  # 401 = auth required (but n8n is up)
                return {
                    "status": "🟢 UP",
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "🟡 DEGRADED",
                    "error": f"HTTP {response.status_code}",
                    "response_time": 0
                }

        except httpx.ConnectError:
            return {
                "status": "🔴 DOWN",
                "error": "Connection refused",
                "response_time": 0
            }
        except Exception as e:
            return {
                "status": "🔴 ERROR",
                "error": str(e),
                "response_time": 0
            }

    async def get_platform_stats(self) -> Dict[str, Any]:
        """Platform istatistikleri"""
        try:
            response = await self.client.get(f"{self.platform_url}/api/stats")

            if response.status_code == 200:
                return response.json()
            else:
                return {}

        except:
            return {}

    def get_system_metrics(self) -> Dict[str, Any]:
        """Sistem metriklerini topla"""

        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory
        memory = psutil.virtual_memory()
        memory_total_gb = memory.total / (1024 ** 3)
        memory_used_gb = memory.used / (1024 ** 3)
        memory_percent = memory.percent

        # Disk
        disk = psutil.disk_usage('/')
        disk_total_gb = disk.total / (1024 ** 3)
        disk_used_gb = disk.used / (1024 ** 3)
        disk_percent = disk.percent

        # Network (if available)
        try:
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024 ** 2)
            network_recv_mb = network.bytes_recv / (1024 ** 2)
        except:
            network_sent_mb = 0
            network_recv_mb = 0

        return {
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "status": "🟢" if cpu_percent < 70 else ("🟡" if cpu_percent < 90 else "🔴")
            },
            "memory": {
                "total_gb": round(memory_total_gb, 2),
                "used_gb": round(memory_used_gb, 2),
                "percent": memory_percent,
                "status": "🟢" if memory_percent < 70 else ("🟡" if memory_percent < 90 else "🔴")
            },
            "disk": {
                "total_gb": round(disk_total_gb, 2),
                "used_gb": round(disk_used_gb, 2),
                "percent": disk_percent,
                "status": "🟢" if disk_percent < 70 else ("🟡" if disk_percent < 90 else "🔴")
            },
            "network": {
                "sent_mb": round(network_sent_mb, 2),
                "recv_mb": round(network_recv_mb, 2)
            }
        }

    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Tüm metrikleri topla"""

        # Paralel health checks
        platform_health, n8n_health = await asyncio.gather(
            self.check_platform_health(),
            self.check_n8n_health()
        )

        # Platform stats
        platform_stats = await self.get_platform_stats()

        # System metrics
        system_metrics = self.get_system_metrics()

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "platform": platform_health,
                "n8n": n8n_health
            },
            "platform_stats": platform_stats,
            "system": system_metrics
        }

        # Save to history (keep last 100)
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)

        return metrics

    def render_dashboard(self, metrics: Dict[str, Any]) -> Layout:
        """Rich dashboard render"""

        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )

        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        # Header
        header_text = f"""
        🌌 MODULllm.com - Real-Time Monitoring Dashboard
        Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        layout["header"].update(Panel(header_text.strip(), border_style="cyan"))

        # Services Table (Left)
        services_table = Table(title="🚀 Services", box=box.ROUNDED)
        services_table.add_column("Service", style="cyan")
        services_table.add_column("Status", style="bold")
        services_table.add_column("Response Time", justify="right")
        services_table.add_column("Details")

        for service_name, service_data in metrics["services"].items():
            status = service_data.get("status", "❓ UNKNOWN")
            response_time = f"{service_data.get('response_time', 0)*1000:.0f}ms"
            error = service_data.get("error", "")

            services_table.add_row(
                service_name.upper(),
                status,
                response_time,
                error if error else "✅ OK"
            )

        # System Metrics Table (Right)
        system_table = Table(title="💻 System Resources", box=box.ROUNDED)
        system_table.add_column("Resource", style="cyan")
        system_table.add_column("Status", style="bold")
        system_table.add_column("Usage", justify="right")
        system_table.add_column("Details")

        system = metrics["system"]

        # CPU
        system_table.add_row(
            "CPU",
            system["cpu"]["status"],
            f"{system['cpu']['percent']}%",
            f"{system['cpu']['count']} cores"
        )

        # Memory
        system_table.add_row(
            "Memory",
            system["memory"]["status"],
            f"{system['memory']['percent']}%",
            f"{system['memory']['used_gb']:.1f} / {system['memory']['total_gb']:.1f} GB"
        )

        # Disk
        system_table.add_row(
            "Disk",
            system["disk"]["status"],
            f"{system['disk']['percent']}%",
            f"{system['disk']['used_gb']:.1f} / {system['disk']['total_gb']:.1f} GB"
        )

        # Network
        system_table.add_row(
            "Network",
            "🌐",
            "-",
            f"↑ {system['network']['sent_mb']:.1f} MB / ↓ {system['network']['recv_mb']:.1f} MB"
        )

        layout["left"].update(Panel(services_table))
        layout["right"].update(Panel(system_table))

        # Platform Stats (Footer)
        stats = metrics.get("platform_stats", {})
        if stats:
            stats_text = f"""
            Öz Veritabanı: {stats.get('oz_veritabani', {}).get('toplam_icerik', 'N/A')} items |
            Günlük Sorgu: {stats.get('oz_veritabani', {}).get('gunluk_sorgu', 'N/A')} |
            Kullanıcılar: {stats.get('oz_veritabani', {}).get('kullanicilar', 'N/A')}
            """
        else:
            stats_text = "Platform stats unavailable"

        layout["footer"].update(Panel(stats_text.strip(), border_style="green"))

        return layout

    async def run_dashboard(self, interval: int = 2):
        """
        Canlı dashboard çalıştır

        Args:
            interval: Refresh interval (seconds)
        """

        console.clear()

        with Live(console=console, screen=True, auto_refresh=False) as live:
            while True:
                try:
                    # Collect metrics
                    metrics = await self.collect_all_metrics()

                    # Render dashboard
                    dashboard = self.render_dashboard(metrics)

                    # Update live display
                    live.update(dashboard, refresh=True)

                    # Wait
                    await asyncio.sleep(interval)

                except KeyboardInterrupt:
                    console.print("\n\n[yellow]Dashboard stopped by user[/yellow]")
                    break
                except Exception as e:
                    console.print(f"\n\n[red]Error: {e}[/red]")
                    await asyncio.sleep(interval)

    async def close(self):
        """Cleanup"""
        await self.client.aclose()


# CLI tool
async def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(description="MODULllm.com Monitoring Dashboard")
    parser.add_argument(
        "--interval",
        type=int,
        default=2,
        help="Refresh interval in seconds (default: 2)"
    )
    parser.add_argument(
        "--platform-url",
        type=str,
        default="http://localhost:8000",
        help="Platform API URL"
    )
    parser.add_argument(
        "--n8n-url",
        type=str,
        default="http://localhost:5678",
        help="n8n URL"
    )

    args = parser.parse_args()

    monitor = MODULllmMonitor(
        platform_url=args.platform_url,
        n8n_url=args.n8n_url
    )

    try:
        console.print("\n[cyan]🌌 MODULllm.com Monitoring Dashboard Starting...[/cyan]\n")
        console.print("[yellow]Press Ctrl+C to exit[/yellow]\n")
        await asyncio.sleep(1)

        await monitor.run_dashboard(interval=args.interval)

    finally:
        await monitor.close()


if __name__ == "__main__":
    # Requirements:
    # pip install rich psutil httpx

    asyncio.run(main())
