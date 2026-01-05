# 🌐 HOSTINGER AGENCY - 100 SİTE KURULUM REHBERİ

> **MODULllm.com Ecosystem - 100 Node Deployment**

---

## 📋 **GEREKSINIMLER**

1. **Hostinger Agency Hesabı** (100 website capacity)
2. **Hostinger Game Dev Pro** (oyun hosting)
3. **Domain**: modulllm.com (ve alt domainler)
4. **SSL Sertifikaları** (otomatik Let's Encrypt)

---

## 🎯 **ADIM 1: ANA DOMAIN KURULUMU**

### **1.1. modulllm.com Setup:**

```bash
# Hostinger hPanel'e giriş yap
https://hpanel.hostinger.com

# Websites > Add Website
# Choose: Create a new website
# Domain: modulllm.com
# Package: Agency Plan
```

### **1.2. SSL Aktifleştir:**

```bash
# SSL/TLS > Manage SSL
# Let's Encrypt SSL > Enable
# Auto-renewal: ON
```

### **1.3. FTP/SFTP Bilgileri:**

```
Host: ftp.modulllm.com
Username: u123456789
Password: [güvenli şifre]
Port: 21 (FTP) veya 22 (SFTP)
```

---

## 🏗️ **ADIM 2: 100 SİTE STRATEJİSİ**

### **2.1. Ana Kategorizasyon:**

```yaml
CORE (1 site):
  - modulllm.com: Ana platform

B1Z_FAMILY (11 sites):
  - b1z-kodlab.modulllm.com
  - b1z-maya.modulllm.com
  - b1z-podcast.modulllm.com
  - b1z-data.modulllm.com
  - b1z-games.modulllm.com
  - b1z-nft.modulllm.com
  - b1z-defi.modulllm.com
  - b1z-edu.modulllm.com
  - b1z-ai.modulllm.com
  - b1z-community.modulllm.com
  - b1z-api.modulllm.com

LANGUAGE_NODES (30 sites):
  # Ana diller
  - tr.modulllm.com      # Türkçe
  - en.modulllm.com      # English
  - ar.modulllm.com      # العربية
  - zh.modulllm.com      # 中文
  - ru.modulllm.com      # Русский
  - es.modulllm.com      # Español
  - fr.modulllm.com      # Français
  - de.modulllm.com      # Deutsch
  - ja.modulllm.com      # 日本語
  - ko.modulllm.com      # 한국어
  - hi.modulllm.com      # हिन्दी

  # Bölgesel diller
  - pt.modulllm.com      # Português
  - it.modulllm.com      # Italiano
  - nl.modulllm.com      # Nederlands
  - pl.modulllm.com      # Polski
  - sv.modulllm.com      # Svenska
  - no.modulllm.com      # Norsk
  - da.modulllm.com      # Dansk
  - fi.modulllm.com      # Suomi
  - cs.modulllm.com      # Čeština

  # MENA & Asia
  - fa.modulllm.com      # فارسی
  - ur.modulllm.com      # اردو
  - bn.modulllm.com      # বাংলা
  - vi.modulllm.com      # Tiếng Việt
  - th.modulllm.com      # ไทย
  - id.modulllm.com      # Bahasa Indonesia
  - ms.modulllm.com      # Bahasa Melayu
  - tl.modulllm.com      # Tagalog
  - he.modulllm.com      # עברית
  - el.modulllm.com      # Ελληνικά

SPECIALIZED_NODES (20 sites):
  - code.modulllm.com        # Code generation
  - design.modulllm.com      # Design tools
  - music.modulllm.com       # Music AI
  - video.modulllm.com       # Video tools
  - image.modulllm.com       # Image generation
  - voice.modulllm.com       # Voice synthesis
  - translate.modulllm.com   # Translation
  - write.modulllm.com       # Writing assistant
  - research.modulllm.com    # Research tools
  - business.modulllm.com    # Business AI
  - legal.modulllm.com       # Legal AI
  - medical.modulllm.com     # Medical AI (informational)
  - finance.modulllm.com     # Finance tools
  - marketing.modulllm.com   # Marketing AI
  - sales.modulllm.com       # Sales automation
  - hr.modulllm.com          # HR tools
  - learn.modulllm.com       # Learning platform
  - kids.modulllm.com        # Kids education
  - senior.modulllm.com      # Senior-friendly
  - accessibility.modulllm.com # Accessibility tools

REGIONAL_NODES (20 sites):
  # Geographic hubs
  - turkey.modulllm.com      # Türkiye
  - mena.modulllm.com        # Middle East & North Africa
  - gcc.modulllm.com         # Gulf Cooperation Council
  - europe.modulllm.com      # Europe
  - asia.modulllm.com        # Asia Pacific
  - americas.modulllm.com    # Americas
  - africa.modulllm.com      # Africa
  - oceania.modulllm.com     # Oceania

  # Major cities
  - istanbul.modulllm.com
  - dubai.modulllm.com
  - riyadh.modulllm.com
  - cairo.modulllm.com
  - london.modulllm.com
  - paris.modulllm.com
  - berlin.modulllm.com
  - tokyo.modulllm.com
  - singapore.modulllm.com
  - newyork.modulllm.com
  - losangeles.modulllm.com
  - sydney.modulllm.com

PARTNER_ECOSYSTEM (18 sites):
  # Universities
  - uni-1.modulllm.com
  - uni-2.modulllm.com
  - uni-3.modulllm.com
  - uni-4.modulllm.com
  - uni-5.modulllm.com

  # Enterprises
  - enterprise-1.modulllm.com
  - enterprise-2.modulllm.com
  - enterprise-3.modulllm.com
  - enterprise-4.modulllm.com
  - enterprise-5.modulllm.com

  # Government (pilot)
  - gov-pilot-1.modulllm.com
  - gov-pilot-2.modulllm.com
  - gov-pilot-3.modulllm.com

  # NGOs
  - ngo-1.modulllm.com
  - ngo-2.modulllm.com
  - ngo-3.modulllm.com
  - ngo-4.modulllm.com
  - ngo-5.modulllm.com
```

---

## 🚀 **ADIM 3: TOPLU KURULUM SCRIPT**

### **3.1. Subdomain Oluşturma (Otomatik):**

```bash
#!/bin/bash
# create_subdomains.sh

# Hostinger API credentials (API varsa)
HOSTINGER_API_KEY="your_api_key"
MAIN_DOMAIN="modulllm.com"

# B1Z Family subdomains
B1Z_SUBDOMAINS=(
  "b1z-kodlab"
  "b1z-maya"
  "b1z-podcast"
  "b1z-data"
  "b1z-games"
  "b1z-nft"
  "b1z-defi"
  "b1z-edu"
  "b1z-ai"
  "b1z-community"
  "b1z-api"
)

# Language subdomains
LANG_SUBDOMAINS=(
  "tr" "en" "ar" "zh" "ru" "es" "fr" "de" "ja" "ko" "hi"
  "pt" "it" "nl" "pl" "sv" "no" "da" "fi" "cs"
  "fa" "ur" "bn" "vi" "th" "id" "ms" "tl" "he" "el"
)

# Create subdomains
create_subdomain() {
  local subdomain=$1
  echo "Creating ${subdomain}.${MAIN_DOMAIN}..."

  # Hostinger hPanel'de manuel oluştur veya API kullan
  # API yoksa manuel:
  # hPanel > Domains > Subdomains > Create Subdomain
  # Subdomain: ${subdomain}
  # Document Root: public_html/${subdomain}
}

# B1Z Family
for sub in "${B1Z_SUBDOMAINS[@]}"; do
  create_subdomain "$sub"
done

# Languages
for sub in "${LANG_SUBDOMAINS[@]}"; do
  create_subdomain "$sub"
done

echo "✅ Tüm subdomainler oluşturuldu!"
```

### **3.2. Toplu FTP Upload:**

```bash
#!/bin/bash
# upload_to_all_sites.sh

FTP_USER="u123456789"
FTP_PASS="your_password"
FTP_HOST="ftp.modulllm.com"

# Her subdomain için dosyaları yükle
SUBDOMAINS=("tr" "en" "ar" "zh" "ru")  # Örnek

for sub in "${SUBDOMAINS[@]}"; do
  echo "Uploading to ${sub}.modulllm.com..."

  lftp -u "$FTP_USER,$FTP_PASS" "$FTP_HOST" <<EOF
    cd public_html/${sub}
    mirror -R ./build ./
    bye
EOF

  echo "✅ ${sub} uploaded!"
done
```

---

## 🎮 **ADIM 4: GAME DEV PRO SETUP**

### **4.1. B1Z GAMES Hosting:**

```bash
# Hostinger Game Dev Pro özellikler:
- Node.js support
- WebSocket support
- High-bandwidth
- Low-latency
- GPU-accelerated (bazı planlar)

# Setup:
1. hPanel > Websites > b1z-games.modulllm.com
2. Advanced > Node.js
3. Enable Node.js
4. Version: 18 LTS
5. Application root: /public_html/b1z-games
6. Application startup file: server.js
```

### **4.2. Game Server Konfigürasyonu:**

```javascript
// server.js (B1Z GAMES)
const express = require('express');
const WebSocket = require('ws');
const app = express();

const PORT = process.env.PORT || 3000;

// Static files
app.use(express.static('public'));

// WebSocket server (multiplayer games)
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('New game client connected');

  ws.on('message', (message) => {
    // Game logic
    console.log('Game event:', message);
  });
});

// API routes
app.get('/api/games', (req, res) => {
  res.json({
    games: [
      { id: 1, name: 'B1Z Code Challenge', players: 1111 },
      { id: 2, name: 'AI Battle Arena', players: 555 },
    ]
  });
});

app.listen(PORT, () => {
  console.log(`🎮 B1Z GAMES server running on port ${PORT}`);
});
```

---

## 📊 **ADIM 5: MONITORING & MANAGEMENT**

### **5.1. Site Durumu İzleme:**

```python
# monitoring/check_all_sites.py
import asyncio
import httpx

SITES = [
    "https://modulllm.com",
    "https://b1z-kodlab.modulllm.com",
    "https://tr.modulllm.com",
    # ... tüm 100 site
]

async def check_site(url):
    """Site durumunu kontrol et"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            status = "✅ UP" if response.status_code == 200 else f"⚠️ {response.status_code}"
            return {"url": url, "status": status}
    except Exception as e:
        return {"url": url, "status": f"❌ DOWN: {e}"}

async def monitor_all():
    """Tüm siteleri kontrol et"""
    tasks = [check_site(site) for site in SITES]
    results = await asyncio.gather(*tasks)

    print("\n📊 MODULllm.com Ecosystem Status:\n")
    for result in results:
        print(f"{result['status']}: {result['url']}")

if __name__ == "__main__":
    asyncio.run(monitor_all())
```

---

## 🔐 **ADIM 6: GÜVENLİK**

### **6.1. Cloudflare Entegrasyonu (Önerilen):**

```bash
# Cloudflare ile tüm siteleri koruma:

1. Cloudflare hesabı oluştur
2. modulllm.com domaini ekle
3. Nameserver'ları güncelle:
   - NS1: xxxxx.ns.cloudflare.com
   - NS2: yyyyy.ns.cloudflare.com

4. Cloudflare Dashboard > DNS
5. Tüm subdomainleri ekle (wildcard OK: *.modulllm.com)

6. SSL/TLS: Full (strict)
7. Firewall: Enable
8. DDoS Protection: Auto
9. Caching: Optimize
10. CDN: Global distribution
```

---

## 📈 **ADIM 7: ANALYTİCS**

### **7.1. Google Analytics 4:**

```html
<!-- Her site'e ekle -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

---

## ✅ **KURULUM CHECKLİSTİ**

```
□ Ana domain (modulllm.com) kuruldu
□ SSL aktif (Let's Encrypt)
□ 11 B1Z Family subdomain oluşturuldu
□ 30 Language subdomain oluşturuldu
□ 20 Specialized subdomain oluşturuldu
□ 20 Regional subdomain oluşturuldu
□ 18 Partner subdomain oluşturuldu
□ Game Dev Pro aktif (b1z-games)
□ FTP/SFTP erişim test edildi
□ Cloudflare entegrasyonu (opsiyonel)
□ Monitoring script çalışıyor
□ Analytics kuruldu
□ Backup stratejisi oluşturuldu
```

---

## 🚀 **HIZLI BAŞLATMA KOMUTU**

```bash
# Tüm siteleri bir komutla deploy et!
./deploy_all.sh
```

**Sonraki:** 30 TB Drive Setup! →
