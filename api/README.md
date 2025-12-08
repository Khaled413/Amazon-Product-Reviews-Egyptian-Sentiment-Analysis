# Egyptian Sentiment Analysis API

API built with TypeScript and Express for analyzing Egyptian Arabic sentiment.

## 🚀 Quick Start

### Installation

```bash
cd api
npm install
```

### Development

```bash
npm run dev
```

### Build

```bash
npm run build
npm start
```

## 📡 API Endpoints

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "python": "available",
  "service": "Egyptian Sentiment Analysis API"
}
```

### Analyze Sentiment

```http
POST /api/sentiment/analyze
Content-Type: application/json

{
  "text": "المنتج ده جامد أوي والجودة قوية"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "text": "المنتج ده جامد أوي والجودة قوية",
    "sentiment": "positive",
    "confidence": 0.85,
    "label": 1,
    "processed_text": "المنتج جامد الجودة قوية"
  }
}
```

### Batch Analysis

```http
POST /api/sentiment/batch
Content-Type: application/json

{
  "texts": [
    "المنتج ده جامد أوي",
    "مش حلو خالص",
    "المنتج عادي"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "text": "المنتج ده جامد أوي",
      "sentiment": "positive",
      "confidence": 0.85,
      "label": 1
    },
    {
      "text": "مش حلو خالص",
      "sentiment": "negative",
      "confidence": 0.92,
      "label": -1
    },
    {
      "text": "المنتج عادي",
      "sentiment": "neutral",
      "confidence": 0.78,
      "label": 0
    }
  ]
}
```

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```env
PORT=3000
NODE_ENV=development
PYTHON_PATH=python
MODEL_PATH=models/lr_model.pkl
VECTORIZER_PATH=models/lr_vectorizer.pkl
```

## 📦 Requirements

- Node.js >= 16
- Python 3.8+
- Trained model files in `models/` directory

## 🐳 Docker (Optional)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 📝 Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (validation errors)
- `500` - Internal Server Error

## 🔒 Security

- Helmet.js for security headers
- CORS enabled
- Input validation with express-validator

## 📚 Example Usage

### cURL

```bash
curl -X POST http://localhost:3000/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "المنتج ده جامد أوي"}'
```

### JavaScript/TypeScript

```typescript
const response = await fetch('http://localhost:3000/api/sentiment/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'المنتج ده جامد أوي'
  })
});

const result = await response.json();
console.log(result.data.sentiment); // positive
```

### Python

```python
import requests

response = requests.post(
    'http://localhost:3000/api/sentiment/analyze',
    json={'text': 'المنتج ده جامد أوي'}
)

result = response.json()
print(result['data']['sentiment'])  # positive
```


