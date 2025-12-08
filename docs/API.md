# 🔌 API Documentation

## Base URL
```
http://localhost:3000/api
```

## Endpoints

### 1. Health Check
```http
GET /api/health
```
```json
{"status": "healthy", "python": "available"}
```

### 2. Analyze Single Review
```http
POST /api/sentiment/analyze
Content-Type: application/json

{"text": "المنتج ده جامد أوي"}
```
```json
{
  "success": true,
  "data": {
    "sentiment": "positive",
    "confidence": 0.85
  }
}
```

### 3. Analyze Product
```http
POST /api/product/analyze
Content-Type: application/json

{"url": "https://www.amazon.eg/dp/B0CHX1W1XY"}
```
```json
{
  "success": true,
  "data": {
    "product": {"title": "...", "asin": "..."},
    "reviews": [...],
    "dashboard": {
      "total_reviews": 8,
      "sentiment_distribution": {...}
    }
  }
}
```

### 4. Get Product Info (Price & Specs)
```http
POST /api/product/info
Content-Type: application/json

{"url": "https://www.amazon.eg/dp/B0CHX1W1XY"}
```
```json
{
  "success": true,
  "data": {
    "title": "Apple iPhone 15...",
    "price": {"current": 40000, "currency": "EGP"},
    "rating": {"score": 4.5, "count": 2679},
    "specs": {...},
    "images": [...]
  }
}
```

## Error Responses

```json
{
  "error": "رسالة الخطأ",
  "message": "تفاصيل إضافية"
}
```

| Status | الوصف |
|--------|-------|
| 400 | رابط غير صالح |
| 500 | خطأ في الخادم |
| 503 | أمازون تمنع الوصول |
| 504 | انتهت مهلة الطلب |
