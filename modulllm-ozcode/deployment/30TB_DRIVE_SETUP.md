# 💾 30 TB DRIVE SETUP - ÖZ VERİTABANI OKYANUSU

> **MODULllm.com Knowledge Ocean - 30 Terabyte Bilgi Deposu**

---

## 🎯 **AMAÇ**

30 TB Drive = **Öz Veritabanımızın fiziksel evi**

**İçerik:**
- Kullanıcı soruları & cevaplar
- 111 Akıl sentezleri
- B1Z KODLAB ders içerikleri
- Kullanıcı kodları
- MAYA içerik sentezleri
- Podcast kayıtları
- Vector embeddings
- Model fine-tuning datasets
- Backup & snapshots

---

## 📊 **DEPOLAMA STRATEJİSİ (30 TB Bölümleme)**

```yaml
TOTAL: 30 TB

DISTRIBUTION:
  oz_veritabani: 10 TB          # Öz veritabanı ana depo
    - soru_cevap: 3 TB          # Kullanıcı Q&A
    - ders_icerigi: 2 TB        # B1Z KODLAB + EDU
    - sentezler: 2 TB           # 111 Akıl sentezleri
    - kullanici_kodu: 2 TB      # User code repository
    - topluluk: 1 TB            # Community content

  vector_embeddings: 5 TB       # Semantic search vectors
    - text_embeddings: 2 TB     # Text vectors
    - code_embeddings: 1.5 TB   # Code vectors
    - multimodal: 1.5 TB        # Image/Audio/Video vectors

  media_content: 8 TB           # Medya içerikleri
    - images: 2 TB              # AI-generated images
    - audio: 2 TB               # Podcasts, voice
    - video: 3 TB               # Video content
    - 3d_models: 1 TB           # 3D assets (games)

  training_datasets: 4 TB       # Model training
    - fine_tuning: 2 TB         # Fine-tuning data
    - eval_datasets: 1 TB       # Evaluation sets
    - synthetic_data: 1 TB      # AI-generated training data

  backups: 2 TB                 # Yedeklemeler
    - daily_snapshots: 1 TB
    - weekly_full: 1 TB

  cache: 1 TB                   # Hızlı erişim cache
    - hot_data: 500 GB          # Sık kullanılan
    - cdn_mirror: 500 GB        # CDN mirror
```

---

## 🔧 **ADIM 1: DRIVE TERCİHLERİ**

### **Option A: Google Drive (30 TB)**

```bash
# Google Workspace Enterprise Plus
# 30 TB depolama sağlar

# Pricing: ~$20/user/month (Workspace Enterprise)
# Toplam: ~$20/ay (tek user yeterli)

# Avantajlar:
✅ Kolay entegrasyon
✅ API erişimi
✅ Otomatik backup
✅ Google AI entegrasyonu
✅ Güvenilir

# Setup:
1. Google Workspace Enterprise Plus al
2. Google Drive API aktif et
3. Service Account oluştur
4. JSON key indir
```

### **Option B: AWS S3 (30 TB)**

```bash
# Amazon S3 - Scalable object storage

# Pricing: ~$23/TB/month
# 30 TB × $23 = ~$690/ay

# Avantajlar:
✅ Sınırsız scale
✅ Yüksek hız
✅ Programatik erişim
✅ Lambda entegrasyonu
✅ Global CDN (CloudFront)

# Setup:
aws s3api create-bucket \
  --bucket modulllm-ozcode-30tb \
  --region us-east-1
```

### **Option C: Hetzner Storage Box (30 TB)**

```bash
# Hetzner Storage Box - Ekonomik

# Pricing: ~$30/month (20 TB)
#         ~$45/month (30 TB) (özel paket)

# Avantajlar:
✅ Çok ucuz
✅ Güvenilir
✅ FTP/SFTP/WebDAV
✅ Snapshot support

# Setup:
# Hetzner hesabı > Storage Boxes
# 30 TB package seç
```

### **🏆 ÖNERİ: Google Drive (Başlangıç) + AWS S3 (Production)**

```
Phase 1 (MVP): Google Drive 30 TB
  - Hızlı başlangıç
  - Kolay kullanım
  - $20/ay

Phase 2 (Scale): AWS S3
  - Production-ready
  - Unlimited scale
  - Global CDN
```

---

## 🚀 **ADIM 2: GOOGLE DRIVE SETUP (Başlangıç)**

### **2.1. Google Workspace Enterprise Aktivasyonu:**

```bash
# 1. Google Workspace Enterprise Plus sat\ın al:
https://workspace.google.com/pricing

# 2. Admin Console > APIs > Google Drive API
# Enable API

# 3. Service Account oluştur:
https://console.cloud.google.com/iam-admin/serviceaccounts

# Service Account Name: modulllm-drive-access
# Role: Storage Admin
# Key: JSON (indir)
```

### **2.2. Python Entegrasyonu:**

```python
# storage/google_drive_client.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io

class ModulLLmDrive:
    """
    MODULllm.com 30 TB Google Drive Client
    """

    def __init__(self, credentials_file: str):
        """
        Args:
            credentials_file: Service account JSON dosyası yolu
        """
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/drive']
        )

        self.service = build('drive', 'v3', credentials=self.credentials)

        # Klasör yapısı
        self.folders = self._create_folder_structure()

    def _create_folder_structure(self):
        """30 TB klasör yapısını oluştur"""
        folders = {
            "oz_veritabani": None,
            "soru_cevap": None,
            "ders_icerigi": None,
            "sentezler": None,
            "vector_embeddings": None,
            "media_content": None,
            "backups": None,
        }

        # Ana klasörler oluştur
        for folder_name in folders.keys():
            folder_id = self._create_folder(folder_name)
            folders[folder_name] = folder_id

        return folders

    def _create_folder(self, name: str, parent_id: str = None):
        """Klasör oluştur"""
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent_id:
            file_metadata['parents'] = [parent_id]

        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()

        return folder.get('id')

    def upload_file(
        self,
        file_path: str,
        folder_name: str = "oz_veritabani"
    ):
        """Dosya yükle"""
        folder_id = self.folders.get(folder_name)

        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id] if folder_id else []
        }

        media = MediaFileUpload(file_path, resumable=True)

        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, size'
        ).execute()

        print(f"✅ Uploaded: {file.get('name')} ({file.get('size')} bytes)")

        return file.get('id')

    def download_file(self, file_id: str, destination: str):
        """Dosya indir"""
        request = self.service.files().get_media(fileId=file_id)

        fh = io.FileIO(destination, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")

        print(f"✅ Downloaded: {destination}")

    def search_files(self, query: str):
        """Dosya ara"""
        results = self.service.files().list(
            q=query,
            pageSize=100,
            fields="files(id, name, size, modifiedTime)"
        ).execute()

        return results.get('files', [])

    def get_storage_usage(self):
        """Depolama kullanımı"""
        about = self.service.about().get(
            fields="storageQuota"
        ).execute()

        quota = about['storageQuota']

        usage_gb = int(quota.get('usage', 0)) / (1024**3)
        limit_gb = int(quota.get('limit', 0)) / (1024**3)

        print(f"📊 Storage Usage:")
        print(f"   Used: {usage_gb:.2f} GB")
        print(f"   Total: {limit_gb:.2f} GB ({limit_gb / 1024:.2f} TB)")
        print(f"   Free: {limit_gb - usage_gb:.2f} GB")

        return {
            "used_gb": usage_gb,
            "total_gb": limit_gb,
            "free_gb": limit_gb - usage_gb
        }

# Kullanım
if __name__ == "__main__":
    # Service account JSON
    drive = ModulLLmDrive("credentials/service-account.json")

    # Depolama durumu
    drive.get_storage_usage()

    # Dosya yükle
    drive.upload_file("data/test.txt", folder_name="oz_veritabani")

    # Ara
    files = drive.search_files("name contains 'modulllm'")
    print(f"\nFound {len(files)} files")
```

---

## 💾 **ADIM 3: VEKTÖMODATABASE ENTEGRASYONU**

### **3.1. Vector DB Seçimi:**

```python
# Option 1: Pinecone (Managed)
PINECONE_API_KEY = "your_pinecone_key"
PINECONE_ENVIRONMENT = "us-east1-gcp"
PINECONE_INDEX = "modulllm-vectors"

# Option 2: Weaviate (Self-hosted)
WEAVIATE_URL = "http://localhost:8080"

# Option 3: ChromaDB (Simple, local)
# Basit ve hızlı başlangıç için
```

### **3.2. Embedding + Storage:**

```python
# storage/vector_storage.py
import chromadb
from sentence_transformers import SentenceTransformer

class ModulLLmVectorDB:
    """
    30 TB içindeki 5 TB vector embeddings
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="modulllm_oz_veritabani"
        )

        # Embedding model
        self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

    def add_documents(self, documents: list, metadatas: list):
        """Dökümanları embedding ile ekle"""
        # Generate embeddings
        embeddings = self.model.encode(documents).tolist()

        # Add to vector DB
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=[f"doc_{i}" for i in range(len(documents))]
        )

        print(f"✅ Added {len(documents)} documents to vector DB")

    def search(self, query: str, n_results: int = 11):
        """Semantik arama"""
        query_embedding = self.model.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )

        return results

# Kullanım
vector_db = ModulLLmVectorDB()

# Öz veritabanından içerikleri ekle
documents = ["MODULllm.com öz kodundan doğan bir platformdur..."]
metadatas = [{"type": "soru_cevap", "date": "2026-01-04"}]

vector_db.add_documents(documents, metadatas)

# Ara
results = vector_db.search("MODULllm nedir?", n_results=5)
print(results)
```

---

## 📈 **ADIM 4: OTOMATK BACKUP STRATEJİSİ**

### **4.1. Günlük Yedekleme:**

```bash
#!/bin/bash
# backup_daily.sh

# Source
SOURCE_DIR="/app/data"

# Destination (Google Drive veya S3)
DEST_DIR="backups/daily/$(date +%Y-%m-%d)"

# Rsync ile backup
rsync -avz --progress \
  $SOURCE_DIR \
  $DEST_DIR

# 7 günden eski backupları sil
find backups/daily -type d -mtime +7 -exec rm -rf {} +

echo "✅ Daily backup completed: $DEST_DIR"
```

### **4.2. Haftalık Full Backup:**

```python
# backup/weekly_backup.py
import os
import tarfile
from datetime import datetime

def create_full_backup():
    """Haftalık full backup oluştur"""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    backup_file = f"backups/weekly/modulllm-full-{timestamp}.tar.gz"

    print(f"🔄 Creating full backup: {backup_file}")

    with tarfile.open(backup_file, "w:gz") as tar:
        tar.add("./data", arcname="data")
        tar.add("./chroma_db", arcname="vectors")

    # Upload to 30 TB drive
    # drive.upload_file(backup_file, folder_name="backups")

    print(f"✅ Full backup completed!")

if __name__ == "__main__":
    create_full_backup()
```

---

## ✅ **30 TB DRIVE KURULUM CHECKLİSTİ**

```
□ Google Drive Enterprise Plus aktif (30 TB)
□ Service Account oluşturuldu
□ API credentials indirildi
□ Klasör yapısı oluşturuldu:
  □ oz_veritabani/
  □ vector_embeddings/
  □ media_content/
  □ training_datasets/
  □ backups/
□ Python client test edildi
□ Vector DB setup (ChromaDB/Pinecone)
□ Embedding model kuruldu
□ Otomatik backup script çalışıyor
□ Storage monitoring aktif
```

---

## 🚀 **HIZLI TEST**

```bash
# Test 30 TB drive
python storage/google_drive_client.py

# Expected output:
# 📊 Storage Usage:
#    Used: 0.05 GB
#    Total: 30720.00 GB (30.00 TB)
#    Free: 30719.95 GB
# ✅ 30 TB Drive ready!
```

---

**Sonraki:** Tüm sistemi birleştir ve deploy et! 🚀
