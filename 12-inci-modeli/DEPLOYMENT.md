# 🚀 12. İnci Modeli - Production Deployment Guide

Kapsamlı production deployment kılavuzu.

## 📋 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Platform Deployment](#cloud-platform-deployment)
5. [Security Best Practices](#security-best-practices)
6. [Monitoring & Logging](#monitoring--logging)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Genel Bakış

### System Requirements

**Minimum (Development):**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 10 GB

**Recommended (Production):**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50+ GB SSD
- Network: 100 Mbps+

### Architecture

```
┌─────────────────────────────────────────┐
│          Load Balancer / Ingress        │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐         ┌────▼───┐
│Frontend│         │   API  │
│ (Nginx)│         │(FastAPI│
└────────┘         │  x3)   │
                   └────┬───┘
                        │
              ┌─────────┴─────────┐
              │                   │
         ┌────▼────┐         ┌────▼────┐
         │  Redis  │         │  MiniMax│
         │  Cache  │         │   API   │
         └─────────┘         └─────────┘
```

---

## 🐳 Docker Deployment

### Single Container (Development)

```bash
# Build
docker build -t inci12-api:latest ./api

# Run
docker run -d \
  --name inci12-api \
  -p 8000:8000 \
  -e MINIMAX_API_KEY=your_key_here \
  inci12-api:latest
```

### Docker Compose (Recommended)

```bash
# 1. Configure
cp api/.env.example api/.env
nano api/.env  # Add your API keys

# 2. Start all services
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f api

# 5. Stop
docker-compose down
```

**Production docker-compose.yml adjustments:**

```yaml
# Add healthchecks
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s

# Add restart policy
restart: always

# Add resource limits
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
# https://kubernetes.io/docs/tasks/tools/

# Verify cluster connection
kubectl cluster-info
kubectl get nodes
```

### Deploy to Kubernetes

```bash
# 1. Create namespace
kubectl create namespace inci12

# 2. Create secrets
kubectl create secret generic inci12-secrets \
  --from-literal=minimax-api-key=YOUR_KEY \
  --from-literal=minimax-group-id=YOUR_GROUP \
  --from-literal=database-url=postgresql://... \
  -n inci12

# 3. Deploy all resources
kubectl apply -f k8s/ -n inci12

# 4. Check deployment
kubectl get all -n inci12

# 5. Get external IP
kubectl get svc inci12-api -n inci12
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment inci12-api --replicas=5 -n inci12

# Auto-scaling (HPA already configured)
kubectl get hpa -n inci12
```

### Updates (Rolling Update)

```bash
# Update image
kubectl set image deployment/inci12-api \
  api=inci12-api:v2 \
  -n inci12

# Check rollout status
kubectl rollout status deployment/inci12-api -n inci12

# Rollback if needed
kubectl rollout undo deployment/inci12-api -n inci12
```

---

## ☁️ Cloud Platform Deployment

### Heroku

```bash
# 1. Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create inci12-api

# 4. Add Procfile (already included)
# web: uvicorn main:app --host 0.0.0.0 --port $PORT

# 5. Set environment variables
heroku config:set MINIMAX_API_KEY=your_key

# 6. Deploy
git push heroku main

# 7. Open app
heroku open
```

### Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize
railway init

# 4. Add variables
railway variables set MINIMAX_API_KEY=your_key

# 5. Deploy
railway up
```

### Vercel (Frontend Only)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy frontend
cd frontend
vercel deploy --prod
```

### AWS ECS

```bash
# 1. Build and push to ECR
aws ecr create-repository --repository-name inci12-api

docker tag inci12-api:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/inci12-api:latest

docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/inci12-api:latest

# 2. Create ECS task definition
# 3. Create ECS service
# 4. Configure load balancer
```

---

## 🔐 Security Best Practices

### 1. Environment Variables

**Never commit secrets to git!**

```bash
# Use environment variables
export MINIMAX_API_KEY=xxx

# Or use secret management
# - AWS Secrets Manager
# - HashiCorp Vault
# - Kubernetes Secrets
```

### 2. HTTPS/TLS

```bash
# Let's Encrypt with cert-manager (K8s)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Configure ClusterIssuer
kubectl apply -f k8s/cert-issuer.yaml
```

### 3. Rate Limiting

```python
# Already implemented in main.py
# Adjust limits in config

RATE_LIMIT_PER_MINUTE = 60
MAX_MESSAGE_LENGTH = 5000
```

### 4. CORS Configuration

```python
# Production CORS
allow_origins=[
    "https://modulllm.com",
    "https://www.modulllm.com"
]
```

### 5. Input Validation

```python
# Already implemented
# - Message length limits
# - Input sanitization
# - XSS protection
```

---

## 📊 Monitoring & Logging

### Prometheus Metrics

```bash
# Metrics endpoint
curl http://localhost:8000/metrics

# Deploy Prometheus
kubectl apply -f k8s/prometheus.yaml

# Access Prometheus UI
kubectl port-forward svc/prometheus 9090:9090
```

### Grafana Dashboard

```bash
# Deploy Grafana
kubectl apply -f k8s/grafana.yaml

# Access Grafana
kubectl port-forward svc/grafana 3000:3000
# Login: admin/admin

# Import dashboard from k8s/grafana-dashboard.json
```

### Logging

**Structured logging:**

```python
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**ELK Stack:**

```bash
# Deploy Elasticsearch, Logstash, Kibana
kubectl apply -f k8s/elk-stack.yaml
```

---

## ⚡ Performance Optimization

### 1. Caching

```python
# Redis caching enabled
# Configure in .env
REDIS_URL=redis://localhost:6379/0

# Cache TTL
CACHE_TTL=3600  # 1 hour
```

### 2. Connection Pooling

```python
# Database connection pool
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# HTTP client session reuse
# Already implemented in minimax_client.py
```

### 3. Async Operations

```python
# Use async/await for I/O operations
# Already implemented throughout codebase
```

### 4. CDN for Frontend

```bash
# Use CloudFront, Cloudflare, or Fastly
# Configure in frontend deployment
```

### 5. Load Balancing

```yaml
# K8s service already configured
# For manual setup, use Nginx:

upstream inci12_api {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}
```

---

## 🐛 Troubleshooting

### API Not Responding

```bash
# Check API health
curl http://localhost:8000/health

# Check logs
docker-compose logs api
# or
kubectl logs -f deployment/inci12-api
```

### WebSocket Connection Failed

```bash
# Check WebSocket endpoint
wscat -c ws://localhost:8000/ws/emotion/realtime

# Verify proxy settings (Nginx/Ingress)
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;
```

### High Memory Usage

```bash
# Check metrics
docker stats

# Restart with memory limit
docker run -m 2g inci12-api:latest

# K8s resource limits already configured
```

### MiniMax API Errors

```bash
# Check API key
echo $MINIMAX_API_KEY

# Test API directly
curl -X POST https://api.minimax.chat/v1/... \
  -H "Authorization: Bearer $MINIMAX_API_KEY"

# Check rate limits
```

### Database Connection Issues

```bash
# Test connection
psql $DATABASE_URL

# Check K8s secret
kubectl get secret inci12-secrets -o yaml
```

---

## 📈 Scaling Guide

### Horizontal Scaling

```bash
# K8s: HPA already configured (3-10 replicas)
kubectl get hpa

# Manual scaling
kubectl scale deployment inci12-api --replicas=5
```

### Vertical Scaling

```yaml
# Increase resources in deployment.yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

---

## ✅ Production Checklist

- [ ] Environment variables configured
- [ ] HTTPS/TLS enabled
- [ ] Rate limiting active
- [ ] CORS configured
- [ ] Monitoring setup (Prometheus/Grafana)
- [ ] Logging configured
- [ ] Backups configured
- [ ] Auto-scaling enabled
- [ ] Health checks working
- [ ] Load testing completed
- [ ] Security audit done
- [ ] Documentation updated

---

## 🆘 Support

**Issues:** GitHub Issues
**Email:** support@modulllm.com
**Docs:** https://modulllm.com/docs

---

**💎 Powered by MiniMax-M2 | Ready for Production!**
