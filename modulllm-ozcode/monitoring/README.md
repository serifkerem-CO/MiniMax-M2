# 📊 MODULllm.com - Monitoring & Alerting

> **"Sistemini İzle, Problemleri Erkenden Yakala!"**

---

## 🎯 Overview

MODULllm.com için kapsamlı monitoring ve alerting sistemi:

- **Real-time Dashboard**: Canlı sistem izleme
- **Alert System**: Otomatik uyarı sistemi (Email, Slack, Webhook)
- **Health Checks**: Servis sağlık kontrolleri
- **Metrics Collection**: Metrik toplama ve analiz
- **Performance Tracking**: Performans takibi

---

## 🚀 Hızlı Başlangıç

### **1. Dependencies Kur**

```bash
pip install rich psutil httpx
```

### **2. Dashboard Başlat**

```bash
python monitoring/dashboard.py
```

**Beklenen Görüntü:**

```
╔══════════════════════════════════════════════════════════════╗
║   🌌 MODULllm.com - Real-Time Monitoring Dashboard          ║
║   Last Update: 2026-01-05 12:34:56                          ║
╚══════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────┐
│                    🚀 Services                               │
├──────────────┬──────────────┬───────────────┬───────────────┤
│ Service      │ Status       │ Response Time │ Details       │
├──────────────┼──────────────┼───────────────┼───────────────┤
│ PLATFORM     │ 🟢 UP        │ 123ms         │ ✅ OK         │
│ N8N          │ 🟢 UP        │ 45ms          │ ✅ OK         │
└──────────────┴──────────────┴───────────────┴───────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  💻 System Resources                         │
├──────────────┬──────────────┬───────────────┬───────────────┤
│ Resource     │ Status       │ Usage         │ Details       │
├──────────────┼──────────────┼───────────────┼───────────────┤
│ CPU          │ 🟢           │ 35%           │ 8 cores       │
│ Memory       │ 🟢           │ 62%           │ 5.0 / 8.0 GB  │
│ Disk         │ 🟢           │ 45%           │ 90 / 200 GB   │
│ Network      │ 🌐           │ -             │ ↑ 50 MB / ↓..│
└──────────────┴──────────────┴───────────────┴───────────────┘

╔══════════════════════════════════════════════════════════════╗
║  Öz Veritabanı: 1,234 items | Günlük Sorgu: 567 | ...      ║
╚══════════════════════════════════════════════════════════════╝
```

**İnteraktif:**
- Her 2 saniyede otomatik refresh
- Renk kodlu durum göstergeleri (🟢🟡🔴)
- Ctrl+C ile çık

---

## 📡 Dashboard Features

### **CLI Options**

```bash
# Farklı refresh interval
python monitoring/dashboard.py --interval 5

# Farklı URL'ler
python monitoring/dashboard.py \
  --platform-url http://production.modulllm.com \
  --n8n-url http://n8n.modulllm.com

# Yardım
python monitoring/dashboard.py --help
```

### **Metrikler**

#### **Services**
- Platform API (http://localhost:8000)
- n8n Workflow Automation (http://localhost:5678)
- Response time tracking
- Uptime monitoring

#### **System Resources**
- **CPU**: Usage %, core count
- **Memory**: Total, used, available (GB & %)
- **Disk**: Total, used, available (GB & %)
- **Network**: Sent/Received data (MB)

#### **Platform Stats**
- Öz Veritabanı item count
- Günlük sorgu sayısı
- Kullanıcı sayısı
- 111 Akıl sistem durumu

### **Status Colors**

- 🟢 **GREEN**: Healthy (<70% usage)
- 🟡 **YELLOW**: Warning (70-90% usage)
- 🔴 **RED**: Critical (>90% usage or service down)

---

## 🚨 Alert System

### **Configuration**

```python
# alert_config.py

ALERT_CONFIG = {
    "email": {
        "enabled": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender": "alerts@modulllm.com",
        "password": os.getenv("ALERT_EMAIL_PASSWORD"),
        "recipients": [
            "admin@modulllm.com",
            "devops@modulllm.com"
        ]
    },
    "slack": {
        "enabled": True,
        "webhook_url": os.getenv("SLACK_WEBHOOK_URL")
    },
    "webhook": {
        "enabled": False,
        "url": os.getenv("CUSTOM_WEBHOOK_URL")
    }
}
```

### **Thresholds**

```python
ALERT_THRESHOLDS = {
    "cpu_percent": 90,         # CPU > 90% = CRITICAL
    "memory_percent": 90,      # Memory > 90% = CRITICAL
    "disk_percent": 80,        # Disk > 80% = WARNING
    "response_time_ms": 5000,  # Response > 5s = WARNING
}
```

### **Usage**

```python
from monitoring.alert_system import MODULllmAlertSystem, AlertLevel

# Initialize
alert_system = MODULllmAlertSystem(config=ALERT_CONFIG)

# Manual alert
await alert_system.send_alert(
    subject="High CPU Usage",
    message="CPU usage has exceeded 90% for 5 minutes",
    level=AlertLevel.CRITICAL
)

# Automatic threshold monitoring
await alert_system.check_and_alert(
    metrics=current_metrics,
    thresholds=ALERT_THRESHOLDS
)
```

### **Alert Channels**

#### **1. Email**
- HTML formatted alerts
- Color-coded by severity
- Automatic timestamp
- Multiple recipients

#### **2. Slack**
- Rich formatting with emojis
- Threaded conversations
- @channel mentions for critical
- Interactive buttons (future)

#### **3. Custom Webhook**
- JSON payload
- Any external system
- Zapier, IFTTT, custom apps

#### **4. Logs**
- Always active
- JSON structured logs
- /var/log/modulllm/alerts.log

---

## 🏥 Automated Health Checks

### **health_monitor.py** (Continuous Monitoring)

```python
# monitoring/health_monitor.py

from monitoring.dashboard import MODULllmMonitor
from monitoring.alert_system import MODULllmAlertSystem

async def continuous_monitoring():
    """Background monitoring with alerts"""

    monitor = MODULllmMonitor()
    alerts = MODULllmAlertSystem(config=ALERT_CONFIG)

    while True:
        # Collect metrics
        metrics = await monitor.collect_all_metrics()

        # Check thresholds and alert
        await alerts.check_and_alert(metrics, ALERT_THRESHOLDS)

        # Wait 60 seconds
        await asyncio.sleep(60)

# Run as systemd service or Docker container
```

### **Systemd Service** (Production)

```ini
# /etc/systemd/system/modulllm-monitor.service

[Unit]
Description=MODULllm.com Monitoring Service
After=network.target

[Service]
Type=simple
User=modulllm
WorkingDirectory=/opt/modulllm
ExecStart=/usr/bin/python3 monitoring/health_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable modulllm-monitor
sudo systemctl start modulllm-monitor

# Check status
sudo systemctl status modulllm-monitor

# View logs
sudo journalctl -u modulllm-monitor -f
```

---

## 📈 Integration with Prometheus

### **Prometheus Config**

```yaml
# prometheus.yml

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'modulllm-platform'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### **Grafana Dashboard**

Import MODULllm.com dashboard template:

```json
{
  "dashboard": {
    "title": "MODULllm.com Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{
          "expr": "rate(modulllm_requests_total[5m])"
        }]
      },
      {
        "title": "Response Time (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, modulllm_request_duration_seconds)"
        }]
      }
    ]
  }
}
```

---

## 🔔 Alert Examples

### **Critical Alerts**

```
Subject: [CRITICAL] Platform Service Down
Message:
  PLATFORM is down: Connection refused
  Time: 2026-01-05T12:34:56Z

  Action Required:
  1. Check Docker containers: docker ps
  2. Check logs: docker logs modulllm-platform
  3. Restart if needed: docker-compose restart
```

### **Warning Alerts**

```
Subject: [WARNING] High Memory Usage
Message:
  Memory usage is 92% (threshold: 90%)
  Used: 7.4 / 8.0 GB

  Recommendation:
  - Investigate memory leaks
  - Consider scaling up
  - Review application logs
```

---

## 📊 Metrics Reference

### **Service Metrics**

| Metric | Type | Description |
|--------|------|-------------|
| `modulllm_requests_total` | Counter | Total HTTP requests |
| `modulllm_request_duration_seconds` | Histogram | Request latency |
| `modulllm_akil_query_duration_seconds` | Histogram | 11 Akıl query time |
| `modulllm_oz_veritabani_total_icerik` | Gauge | Öz DB total items |

### **System Metrics**

| Metric | Type | Description |
|--------|------|-------------|
| `cpu_percent` | Gauge | CPU usage % |
| `memory_percent` | Gauge | Memory usage % |
| `disk_percent` | Gauge | Disk usage % |
| `network_bytes_sent` | Counter | Network sent (bytes) |
| `network_bytes_recv` | Counter | Network received (bytes) |

---

## 🛠️ Troubleshooting

### **Dashboard Won't Start**

```bash
# Check dependencies
pip install rich psutil httpx

# Check platform is running
curl http://localhost:8000/health

# Check permissions
ls -la monitoring/dashboard.py
```

### **Alerts Not Sending**

```bash
# Test email config
python monitoring/alert_system.py

# Check environment variables
echo $ALERT_EMAIL_PASSWORD
echo $SLACK_WEBHOOK_URL

# Verify SMTP connectivity
telnet smtp.gmail.com 587
```

### **High Resource Usage**

```bash
# Check top processes
htop

# Docker stats
docker stats

# Kill resource-heavy processes
docker-compose restart
```

---

## 🚀 Production Deployment

### **Docker Compose Integration**

```yaml
# docker-compose.master.yml

  monitoring:
    build:
      context: .
      dockerfile: monitoring/Dockerfile
    container_name: modulllm-monitoring
    environment:
      - ALERT_EMAIL_PASSWORD=${ALERT_EMAIL_PASSWORD}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
    volumes:
      - ./monitoring:/app/monitoring
    depends_on:
      - modulllm-api
      - n8n
    restart: unless-stopped
```

### **Kubernetes Deployment**

```yaml
# k8s/monitoring-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: modulllm-monitoring
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: monitoring
        image: modulllm/monitoring:latest
        env:
        - name: ALERT_EMAIL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: alert-secrets
              key: email-password
```

---

## 📚 Next Steps

1. **Custom Dashboards**: Create Grafana dashboards for specific metrics
2. **PagerDuty Integration**: Add PagerDuty for on-call rotation
3. **Anomaly Detection**: ML-based anomaly detection (Prometheus Anomaly Detector)
4. **Log Aggregation**: ELK stack integration
5. **Distributed Tracing**: Jaeger or Zipkin for request tracing

---

**🌌 MODULllm.com - Her Şey Kontrol Altında!**

**Monitoring × Alerting × Performance = ∞ Güvenilirlik** ⚡
