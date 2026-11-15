# 🤖 حالة النماذج

## النماذج المدربة

| النموذج | الملف | الدقة (Accuracy) | F1-Score |
|---------|-------|------------------|----------|
| SVM | `svm_model.pkl` / `sentiment_svm.pkl` | 94.1% | 0.937 |
| Random Forest | `rf_model.pkl` / `sentiment_rf.pkl` | 94.1% | 0.937 |
| Logistic Regression | `lr_model.pkl` / `sentiment_lr.pkl` | 94.1% | 0.937 |

## Feature Extraction

```python
TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.8
)
```

ملفات استخراج الخصائص المتاحة: `vectorizer.pkl`, `svm_vectorizer.pkl`, `rf_vectorizer.pkl`, `lr_vectorizer.pkl`.

## بيانات الاختبار والتقييم

- **المصدر**: مراجعات أمازون مصرية موسومة
- **مجموعة الاختبار**: 34 مراجعة اختبار فعلية (18 سلبية، 10 محايدة، 6 إيجابية)
- **التصنيفات**: إيجابي (1)، سلبي (-1)، محايد (0)
- **ملاحظة**: دقة 94.12% مبنية على تقييم مجموعة الاختبار الحالية (`reports/svm_evaluation_report.txt`).

## الاستخدام

```python
import joblib

model = joblib.load('models/svm_model.pkl')
vectorizer = joblib.load('models/vectorizer.pkl')

text = "المنتج ده جامد"
features = vectorizer.transform([text])
prediction = model.predict(features)
```
