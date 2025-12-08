"""
معالجة النصوص قبل التدريب
Text Preprocessing Module
"""

import re
import sys
import os
from typing import List, Tuple, Dict
import pandas as pd
import numpy as np

# إضافة مجلد utils إلى المسار
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.egyptian_stopwords import get_egyptian_stopwords
from utils.egyptian_slang import normalize_egyptian_slang

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.stem import ISRIStemmer
    
    # تحميل البيانات المطلوبة
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('tokenizers/arabic')
    except LookupError:
        pass  # قد لا يكون متوفراً
    
except ImportError:
    print("تحذير: nltk غير مثبت. بعض الوظائف قد لا تعمل")
    word_tokenize = None
    ISRIStemmer = None

class TextPreprocessor:
    """فئة لمعالجة النصوص"""
    
    def __init__(self, remove_stopwords: bool = True, stem: bool = False):
        """
        Args:
            remove_stopwords: إزالة Stopwords
            stem: استخدام Stemming
        """
        self.remove_stopwords = remove_stopwords
        self.stem = stem
        self.stopwords = get_egyptian_stopwords() if remove_stopwords else set()
        self.stemmer = ISRIStemmer() if stem and ISRIStemmer else None
    
    def tokenize(self, text: str) -> List[str]:
        """
        تقسيم النص إلى كلمات
        
        Args:
            text: النص المراد تقسيمه
        
        Returns:
            List[str]: قائمة الكلمات
        """
        if word_tokenize:
            try:
                tokens = word_tokenize(text)
            except:
                # Fallback إلى تقسيم بسيط
                tokens = text.split()
        else:
            # تقسيم بسيط
            tokens = text.split()
        
        return tokens
    
    def remove_stopwords_func(self, tokens: List[str]) -> List[str]:
        """
        إزالة Stopwords
        
        Args:
            tokens: قائمة الكلمات
        
        Returns:
            List[str]: قائمة الكلمات بعد إزالة Stopwords
        """
        if not self.remove_stopwords:
            return tokens
        
        return [token for token in tokens if token.lower() not in self.stopwords]
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        تطبيق Stemming
        
        Args:
            tokens: قائمة الكلمات
        
        Returns:
            List[str]: قائمة الكلمات بعد Stemming
        """
        if not self.stem or not self.stemmer:
            return tokens
        
        return [self.stemmer.stem(token) for token in tokens]
    
    def normalize_slang(self, tokens: List[str]) -> List[str]:
        """
        توحيد الكلمات العامية
        
        Args:
            tokens: قائمة الكلمات
        
        Returns:
            List[str]: قائمة الكلمات الموحدة
        """
        return [normalize_egyptian_slang(token) for token in tokens]
    
    def preprocess_text(self, text: str) -> str:
        """
        معالجة نص واحد
        
        Args:
            text: النص المراد معالجته
        
        Returns:
            str: النص المعالج
        """
        if not text or len(text.strip()) == 0:
            return ""
        
        # Tokenization
        tokens = self.tokenize(text)
        
        # Normalize slang
        tokens = self.normalize_slang(tokens)
        
        # Remove stopwords
        tokens = self.remove_stopwords_func(tokens)
        
        # Stemming (optional)
        if self.stem:
            tokens = self.stem_tokens(tokens)
        
        # إرجاع النص المعالج
        return ' '.join(tokens)
    
    def preprocess_dataset(self, data: List[Dict], text_column: str = 'text') -> List[Dict]:
        """
        معالجة مجموعة بيانات
        
        Args:
            data: قائمة البيانات
            text_column: اسم عمود النص
        
        Returns:
            List[Dict]: البيانات المعالجة
        """
        processed_data = []
        
        for item in data:
            processed_item = item.copy()
            original_text = item.get(text_column, '')
            processed_text = self.preprocess_text(original_text)
            processed_item['processed_text'] = processed_text
            processed_item['original_text'] = original_text
            processed_data.append(processed_item)
        
        return processed_data

def prepare_training_data(input_file: str, output_file: str = None):
    """
    تحضير البيانات للتدريب
    
    Args:
        input_file: مسار ملف البيانات المصنفة
        output_file: مسار ملف البيانات المحضرة (اختياري)
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
    
    # معالجة البيانات
    preprocessor = TextPreprocessor(remove_stopwords=True, stem=False)
    processed_data = preprocessor.preprocess_dataset(data)
    
    # حفظ البيانات المحضرة
    if output_file is None:
        base_name = os.path.basename(input_file)
        name, ext = os.path.splitext(base_name)
        output_file = f"data/processed/{name}_processed{ext}"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if output_file.endswith('.json'):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
    elif output_file.endswith('.csv'):
        df_processed = pd.DataFrame(processed_data)
        df_processed.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"تم تحضير {len(processed_data)} مراجعة للتدريب")
    print(f"تم حفظ البيانات في: {output_file}")
    
    return processed_data

if __name__ == "__main__":
    # اختبار المعالجة
    preprocessor = TextPreprocessor(remove_stopwords=True, stem=False)
    
    test_text = "المنتج ده جامد أوي والجودة قوية خالص، أنصح بيه"
    processed = preprocessor.preprocess_text(test_text)
    
    print(f"النص الأصلي: {test_text}")
    print(f"النص المعالج: {processed}")
    
    # معالجة ملف إذا كان موجود
    sample_file = "data/annotated/sample_reviews_cleaned_annotated.json"
    if os.path.exists(sample_file):
        prepare_training_data(sample_file)

