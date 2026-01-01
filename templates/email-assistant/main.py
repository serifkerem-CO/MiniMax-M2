"""
MiniMax-M2 Email Asistanı Şablonu
=================================
AI destekli email işleme ve yanıtlama.

Özellikler:
- Email sınıflandırma
- Otomatik yanıt önerileri
- Email özetleme
- Spam tespiti
- Duygu analizi

Gereksinimler:
    pip install openai imaplib2

Kullanım:
    python main.py --help
"""

import os
import re
import json
import email
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from openai import OpenAI

# Yapılandırma
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "your-email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-app-password")

API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)


# ============================================================================
# Veri Yapıları
# ============================================================================

@dataclass
class Email:
    """Email mesajı."""
    id: str
    sender: str
    recipient: str
    subject: str
    body: str
    date: str
    is_read: bool = False
    labels: list = field(default_factory=list)


@dataclass
class EmailAnalysis:
    """Email analiz sonucu."""
    category: str  # work, personal, marketing, spam, urgent
    sentiment: str  # positive, negative, neutral
    priority: str  # high, medium, low
    summary: str
    key_points: list
    suggested_actions: list
    requires_response: bool
    response_deadline: Optional[str] = None


# ============================================================================
# Email İşlemleri
# ============================================================================

class EmailClient:
    """Email istemcisi."""

    def __init__(self):
        self.imap = None
        self.smtp = None

    def connect_imap(self):
        """IMAP sunucusuna bağlan."""
        self.imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        self.imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print(f"✅ IMAP bağlantısı kuruldu: {EMAIL_ADDRESS}")

    def connect_smtp(self):
        """SMTP sunucusuna bağlan."""
        self.smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        self.smtp.starttls()
        self.smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print(f"✅ SMTP bağlantısı kuruldu")

    def disconnect(self):
        """Bağlantıları kapat."""
        if self.imap:
            self.imap.logout()
        if self.smtp:
            self.smtp.quit()

    def fetch_emails(self, folder: str = "INBOX", limit: int = 10) -> list[Email]:
        """Email'leri getir."""
        self.imap.select(folder)

        # Son email'leri al
        _, message_numbers = self.imap.search(None, "ALL")
        email_ids = message_numbers[0].split()[-limit:]

        emails = []
        for email_id in reversed(email_ids):
            _, msg_data = self.imap.fetch(email_id, "(RFC822)")
            email_body = msg_data[0][1]
            msg = email.message_from_bytes(email_body)

            # Body'yi al
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

            emails.append(Email(
                id=email_id.decode(),
                sender=msg["From"],
                recipient=msg["To"],
                subject=msg["Subject"] or "(Konu yok)",
                body=body[:2000],  # İlk 2000 karakter
                date=msg["Date"],
            ))

        return emails

    def send_email(self, to: str, subject: str, body: str):
        """Email gönder."""
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        self.smtp.send_message(msg)
        print(f"📧 Email gönderildi: {to}")


# ============================================================================
# AI Analiz
# ============================================================================

class EmailAssistant:
    """AI Email Asistanı."""

    def __init__(self):
        self.email_client = EmailClient()

    def analyze_email(self, email: Email) -> EmailAnalysis:
        """Email'i analiz et."""
        prompt = f"""Bu email'i analiz et:

Gönderen: {email.sender}
Konu: {email.subject}
Tarih: {email.date}

İçerik:
{email.body}

JSON formatında döndür:
{{
    "category": "work/personal/marketing/spam/urgent",
    "sentiment": "positive/negative/neutral",
    "priority": "high/medium/low",
    "summary": "Kısa özet",
    "key_points": ["nokta1", "nokta2"],
    "suggested_actions": ["aksiyon1", "aksiyon2"],
    "requires_response": true/false,
    "response_deadline": "tarih veya null"
}}"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Sen email analiz uzmanısın. JSON formatında analiz döndür."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        try:
            content = response.choices[0].message.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content

            data = json.loads(json_str)
            return EmailAnalysis(**data)
        except (json.JSONDecodeError, KeyError):
            return EmailAnalysis(
                category="unknown",
                sentiment="neutral",
                priority="medium",
                summary="Analiz yapılamadı",
                key_points=[],
                suggested_actions=[],
                requires_response=False,
            )

    def generate_reply(self, email: Email, tone: str = "professional") -> str:
        """Yanıt önerisi oluştur."""
        tone_prompts = {
            "professional": "Profesyonel ve resmi bir ton kullan.",
            "friendly": "Samimi ve sıcak bir ton kullan.",
            "brief": "Çok kısa ve öz yanıt ver.",
            "detailed": "Detaylı ve kapsamlı yanıt ver.",
        }

        prompt = f"""Bu email'e yanıt yaz:

Gönderen: {email.sender}
Konu: {email.subject}
İçerik:
{email.body}

{tone_prompts.get(tone, tone_prompts['professional'])}
Sadece yanıt metnini döndür."""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Sen profesyonel email yazarısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000,
        )

        return response.choices[0].message.content

    def summarize_inbox(self, emails: list[Email]) -> str:
        """Gelen kutusunu özetle."""
        email_summaries = []
        for e in emails[:10]:
            email_summaries.append(f"- {e.sender}: {e.subject}")

        prompt = f"""Bu email'leri özetle ve öncelikleri belirt:

{chr(10).join(email_summaries)}

Kısa bir özet ve önerilen aksiyonlar yaz."""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Sen email yönetimi uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500,
        )

        return response.choices[0].message.content

    def compose_email(self, description: str, recipient: str = "") -> dict:
        """Email taslağı oluştur."""
        prompt = f"""Bu açıklamaya göre email yaz:

{description}

Alıcı: {recipient or 'Belirtilmedi'}

JSON formatında döndür:
{{
    "subject": "Konu",
    "body": "Email içeriği"
}}"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Sen profesyonel email yazarısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000,
        )

        try:
            content = response.choices[0].message.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"subject": "Konu", "body": content}


# ============================================================================
# CLI
# ============================================================================

def demo():
    """Demo modu."""
    print("=" * 60)
    print("📧 MiniMax-M2 Email Asistanı Demo")
    print("=" * 60)

    assistant = EmailAssistant()

    # Örnek email
    sample_email = Email(
        id="1",
        sender="ahmet@example.com",
        recipient="ben@example.com",
        subject="Proje Toplantısı Hakkında",
        body="""Merhaba,

Yarın saat 14:00'te yapılacak proje toplantısı için hazırlıklarımı tamamladım.
Sunumum hazır ve size göndereceğim.

Toplantıda tartışmak istediğim konular:
1. Q1 hedeflerinin değerlendirmesi
2. Yeni özellikler için timeline
3. Bütçe revizyonu

Sizin de eklemek istediğiniz konular var mı?

Saygılarımla,
Ahmet""",
        date="Mon, 15 Jan 2024 10:30:00",
    )

    # Analiz
    print("\n📊 Email Analizi:")
    print("-" * 40)
    analysis = assistant.analyze_email(sample_email)
    print(f"Kategori: {analysis.category}")
    print(f"Duygu: {analysis.sentiment}")
    print(f"Öncelik: {analysis.priority}")
    print(f"Özet: {analysis.summary}")
    print(f"Yanıt gerekli: {'Evet' if analysis.requires_response else 'Hayır'}")

    # Yanıt önerisi
    print("\n✉️ Önerilen Yanıt:")
    print("-" * 40)
    reply = assistant.generate_reply(sample_email, tone="professional")
    print(reply)

    # Email oluşturma
    print("\n📝 Yeni Email Oluşturma:")
    print("-" * 40)
    new_email = assistant.compose_email(
        "Müşteriye proje gecikmesi hakkında özür emaili yaz",
        "musteri@example.com"
    )
    print(f"Konu: {new_email['subject']}")
    print(f"İçerik:\n{new_email['body']}")


def main():
    """Ana fonksiyon."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        print("Kullanım:")
        print("  python main.py --demo    Demo modu")
        print("\nGerçek email işlemleri için .env dosyasını yapılandırın.")


if __name__ == "__main__":
    main()
