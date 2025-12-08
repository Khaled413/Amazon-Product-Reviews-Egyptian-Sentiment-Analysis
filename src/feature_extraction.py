"""
استخراج الخصائص من النصوص
Feature Extraction Module
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("تحذير: transformers غير مثبت. لن تكون نماذج BERT متاحة")

class FeatureExtractor:
    """فئة لاستخراج الخصائص"""
    
    def __init__(self, method: str = 'tfidf', max_features: int = 5000):
        """
        Args:
            method: طريقة الاستخراج ('tfidf', 'bow', 'bert', 'marbert')
            max_features: الحد الأقصى للخصائص (لـ TF-IDF و BOW)
        """
        self.method = method.lower()
        self.max_features = max_features
        self.vectorizer = None
        self.tokenizer = None
        self.model = None
        
        if self.method == 'tfidf':
            self.vectorizer = TfidfVectorizer(
                max_features=max_features,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )
        elif self.method == 'bow':
            self.vectorizer = CountVectorizer(
                max_features=max_features,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )
        elif self.method in ['bert', 'marbert', 'arabert']:
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("transformers غير مثبت. يرجى تثبيته: pip install transformers torch")
            self._load_transformer_model()
    
    def _load_transformer_model(self):
        """تحميل نموذج Transformer"""
        model_name = {
            'bert': 'bert-base-multilingual-cased',
            'marbert': 'UBC-NLP/MARBERT',
            'arabert': 'aubmindlab/bert-base-arabertv02'
        }.get(self.method, 'UBC-NLP/MARBERT')
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.eval()
            print(f"تم تحميل النموذج: {model_name}")
        except Exception as e:
            print(f"خطأ في تحميل النموذج {model_name}: {e}")
            print("استخدام TF-IDF كبديل")
            self.method = 'tfidf'
            self.vectorizer = TfidfVectorizer(max_features=self.max_features)
    
    def extract_features_transformer(self, texts: List[str]) -> np.ndarray:
        """
        استخراج الخصائص باستخدام Transformer
        
        Args:
            texts: قائمة النصوص
        
        Returns:
            np.ndarray: مصفوفة الخصائص
        """
        if not self.tokenizer or not self.model:
            raise ValueError("النموذج غير محمل")
        
        features = []
        
        with torch.no_grad():
            for text in texts:
                # Tokenization
                inputs = self.tokenizer(
                    text,
                    return_tensors='pt',
                    truncation=True,
                    padding=True,
                    max_length=128
                )
                
                # استخراج الخصائص
                outputs = self.model(**inputs)
                # استخدام [CLS] token كتمثيل للنص
                text_features = outputs.last_hidden_state[:, 0, :].numpy()
                features.append(text_features[0])
        
        return np.array(features)
    
    def fit(self, texts: List[str]):
        """
        تدريب الـ Vectorizer على البيانات
        
        Args:
            texts: قائمة النصوص للتدريب
        """
        if self.method in ['tfidf', 'bow']:
            self.vectorizer.fit(texts)
        # Transformer models لا تحتاج fit
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """
        تحويل النصوص إلى خصائص
        
        Args:
            texts: قائمة النصوص
        
        Returns:
            np.ndarray: مصفوفة الخصائص
        """
        if self.method in ['tfidf', 'bow']:
            if self.vectorizer is None:
                raise ValueError("يجب استدعاء fit() أولاً")
            return self.vectorizer.transform(texts).toarray()
        elif self.method in ['bert', 'marbert', 'arabert']:
            return self.extract_features_transformer(texts)
        else:
            raise ValueError(f"طريقة غير معروفة: {self.method}")
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """
        تدريب وتحويل في خطوة واحدة
        
        Args:
            texts: قائمة النصوص
        
        Returns:
            np.ndarray: مصفوفة الخصائص
        """
        if self.method in ['tfidf', 'bow']:
            return self.vectorizer.fit_transform(texts).toarray()
        elif self.method in ['bert', 'marbert', 'arabert']:
            return self.extract_features_transformer(texts)
        else:
            raise ValueError(f"طريقة غير معروفة: {self.method}")
    
    def save(self, filepath: str):
        """حفظ الـ Vectorizer"""
        if self.method in ['tfidf', 'bow']:
            with open(filepath, 'wb') as f:
                pickle.dump(self.vectorizer, f)
        else:
            print("حفظ نماذج Transformer غير مدعوم حالياً")
    
    def load(self, filepath: str):
        """تحميل الـ Vectorizer"""
        if self.method in ['tfidf', 'bow']:
            with open(filepath, 'rb') as f:
                self.vectorizer = pickle.load(f)
        else:
            print("تحميل نماذج Transformer غير مدعوم حالياً")

def extract_features_from_file(input_file: str, 
                               output_file: str = None,
                               method: str = 'tfidf',
                               text_column: str = 'processed_text'):
    """
    استخراج الخصائص من ملف بيانات
    
    Args:
        input_file: مسار ملف البيانات
        output_file: مسار ملف الخصائص (اختياري)
        method: طريقة الاستخراج
        text_column: اسم عمود النص
    """
    import json
    
    # قراءة البيانات
    if input_file.endswith('.json'):
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif input_file.endswith('.csv'):
        df = pd.read_csv(input_file)
        data = df.to_dict('records')
    else:
        raise ValueError("نوع الملف غير مدعوم")
    
    # استخراج النصوص
    texts = [item.get(text_column, item.get('text', '')) for item in data]
    
    # استخراج الخصائص
    extractor = FeatureExtractor(method=method)
    features = extractor.fit_transform(texts)
    
    # حفظ الخصائص
    if output_file is None:
        base_name = os.path.basename(input_file)
        name, ext = os.path.splitext(base_name)
        output_file = f"data/processed/{name}_features_{method}.pkl"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # حفظ الخصائص والـ vectorizer
    result = {
        'features': features.tolist(),
        'labels': [item.get('label', item.get('sentiment', '')) for item in data],
        'texts': texts
    }
    
    with open(output_file, 'wb') as f:
        pickle.dump(result, f)
    
    # حفظ الـ vectorizer
    vectorizer_file = output_file.replace('.pkl', '_vectorizer.pkl')
    extractor.save(vectorizer_file)
    
    print(f"تم استخراج {features.shape[0]} عينة مع {features.shape[1]} خاصية")
    print(f"تم حفظ الخصائص في: {output_file}")
    
    return features, extractor

if __name__ == "__main__":
    # اختبار استخراج الخصائص
    sample_file = "data/processed/sample_reviews_cleaned_annotated_processed.json"
    
    if os.path.exists(sample_file):
        print("استخراج الخصائص باستخدام TF-IDF...")
        features, extractor = extract_features_from_file(sample_file, method='tfidf')
        print(f"شكل المصفوفة: {features.shape}")
    else:
        print("ملف البيانات غير موجود. يرجى تشغيل preprocessing.py أولاً")


