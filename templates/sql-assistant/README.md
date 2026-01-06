# MiniMax-M2 SQL Asistan Şablonu

AI destekli SQL sorgu üretici ve analiz aracı.

## Özellikler

- **Doğal Dil → SQL**: Türkçe/İngilizce sorgulardan SQL üretimi
- **SQL Açıklama**: Karmaşık sorguları anlaşılır açıkla
- **Optimizasyon**: Performans analizi ve index önerileri
- **Şema Üretimi**: Açıklamadan veritabanı şeması oluştur

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
# Doğal dil → SQL
python main.py query "son 30 gündeki siparişleri getir"

# SQL açıklama
python main.py explain "SELECT u.name, COUNT(*) FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.id"

# SQL optimizasyon
python main.py optimize "SELECT * FROM orders WHERE DATE(created_at) = '2024-01-15'"

# Şema üretimi
python main.py schema "e-ticaret sitesi için kullanıcı, ürün ve sipariş tabloları"

# SQL formatlama
python main.py format "select * from users where id=1"

# Demo
python main.py demo
```

## Örnek Şemalar

Yerleşik `ecommerce` şeması:
- users (id, name, email, created_at)
- products (id, name, price, category_id, stock)
- orders (id, user_id, total, status, created_at)
- order_items (id, order_id, product_id, quantity, price)
- categories (id, name, parent_id)

## Örnek

```bash
$ python main.py query "en çok sipariş veren 5 müşteriyi getir"

💾 Üretilen SQL
SELECT u.name, COUNT(o.id) as order_count
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name
ORDER BY order_count DESC
LIMIT 5;
```
