# 🤖 حالة النماذج

## النماذج المدربة

| النموذج | الملف | الدقة | F1-Score |
|---------|-------|-------|----------|
| SVM | `sentiment_svm.pkl` | 90% | 0.89 |
| Random Forest | `sentiment_rf.pkl` | 88% | 0.87 |
| Logistic Regression | `sentiment_lr.pkl` | 85% | 0.84 |

## Feature Extraction

```python
TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.8
)
```

## بيانات التدريب

- **المصدر**: مراجعات أمازون مصرية
- **الحجم**: 2000 مراجعة مصنفة
- **التصنيفات**: إيجابي، سلبي، محايد

## الاستخدام

```python
import joblib

model = joblib.load('models/sentiment_svm.pkl')
vectorizer = joblib.load('models/vectorizer.pkl')

text = "المنتج ده جامد"
features = vectorizer.transform([text])
prediction = model.predict(features)
```
