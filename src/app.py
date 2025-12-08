"""
واجهة تطبيق تحليل المشاعر
Sentiment Analysis Application Interface
"""

import os
import sys
import pickle
import numpy as np
from typing import Dict, Optional

# إضافة المسارات المطلوبة
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("تحذير: Streamlit غير مثبت. سيتم استخدام واجهة CLI")

from src.data_cleaning import DataCleaner
from src.preprocessing import TextPreprocessor
from src.feature_extraction import FeatureExtractor
from src.training import ModelTrainer

class SentimentAnalyzer:
    """فئة لتحليل المشاعر"""
    
    def __init__(self, model_path: str, vectorizer_path: str = None):
        """
        Args:
            model_path: مسار النموذج المدرب
            vectorizer_path: مسار الـ Vectorizer (لـ TF-IDF/BOW)
        """
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.model = None
        self.vectorizer = None
        self.cleaner = DataCleaner()
        self.preprocessor = TextPreprocessor(remove_stopwords=True, stem=False)
        self.load_model()
    
    def load_model(self):
        """تحميل النموذج"""
        try:
            # تحديد نوع النموذج من اسم الملف
            model_name = os.path.basename(self.model_path)
            if 'lstm' in model_name:
                model_type = 'lstm'
            elif 'svm' in model_name:
                model_type = 'svm'
            elif 'rf' in model_name:
                model_type = 'rf'
            else:
                model_type = 'lr'
            
            # تحميل النموذج
            trainer = ModelTrainer(model_type=model_type)
            trainer.load(self.model_path)
            self.model = trainer
            
            # تحميل Vectorizer إذا كان موجود
            if self.vectorizer_path and os.path.exists(self.vectorizer_path):
                extractor = FeatureExtractor(method='tfidf')
                extractor.load(self.vectorizer_path)
                self.vectorizer = extractor.vectorizer
            
        except Exception as e:
            print(f"خطأ في تحميل النموذج: {e}")
            raise
    
    def analyze(self, text: str) -> Dict:
        """
        تحليل نص واحد
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            Dict: نتائج التحليل
        """
        if not text or len(text.strip()) == 0:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'label': 0
            }
        
        # تنظيف النص
        cleaned_text = self.cleaner.clean_text(text)
        
        # معالجة النص
        processed_text = self.preprocessor.preprocess_text(cleaned_text)
        
        # استخراج الخصائص
        if self.vectorizer:
            features = self.vectorizer.transform([processed_text]).toarray()
        else:
            # إذا لم يكن هناك vectorizer، نحتاج لاستخراج الخصائص مباشرة
            extractor = FeatureExtractor(method='tfidf')
            features = extractor.fit_transform([processed_text])
        
        # التنبؤ
        prediction = self.model.predict(features)[0]
        
        # الاحتمالات
        try:
            probabilities = self.model.predict_proba(features)[0]
        except:
            probabilities = None
        
        # تحويل التصنيف
        label_map = {-1: 'negative', 0: 'neutral', 1: 'positive'}
        sentiment = label_map.get(prediction, 'neutral')
        
        # حساب الثقة
        if probabilities is not None:
            confidence = float(max(probabilities))
        else:
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'label': int(prediction),
            'probabilities': probabilities.tolist() if probabilities is not None else None,
            'original_text': text,
            'cleaned_text': cleaned_text,
            'processed_text': processed_text
        }

def cli_interface():
    """واجهة سطر الأوامر"""
    print("="*60)
    print("تحليل مشاعر مراجعات منتجات أمازون باللهجة المصرية")
    print("="*60)
    print()
    
    # البحث عن النماذج المتاحة
    models_dir = "models"
    if not os.path.exists(models_dir):
        print("خطأ: مجلد النماذج غير موجود. يرجى تدريب النماذج أولاً")
        return
    
    model_files = [f for f in os.listdir(models_dir) if f.endswith('_model.pkl')]
    if not model_files:
        print("خطأ: لم يتم العثور على أي نماذج مدربة")
        return
    
    # اختيار النموذج
    print("النماذج المتاحة:")
    for i, model_file in enumerate(model_files, 1):
        print(f"  {i}. {model_file}")
    
    try:
        choice = int(input("\nاختر رقم النموذج: ")) - 1
        selected_model = model_files[choice]
    except (ValueError, IndexError):
        print("اختيار غير صحيح. استخدام النموذج الأول")
        selected_model = model_files[0]
    
    model_path = os.path.join(models_dir, selected_model)
    
    # البحث عن Vectorizer
    vectorizer_path = model_path.replace('_model.pkl', '_vectorizer.pkl')
    if not os.path.exists(vectorizer_path):
        vectorizer_path = None
    
    # تحميل المحلل
    try:
        analyzer = SentimentAnalyzer(model_path, vectorizer_path)
        print(f"\nتم تحميل النموذج: {selected_model}")
    except Exception as e:
        print(f"خطأ في تحميل النموذج: {e}")
        return
    
    # حلقة التحليل
    print("\n" + "="*60)
    print("أدخل النص المراد تحليله (أدخل 'exit' للخروج)")
    print("="*60)
    
    while True:
        text = input("\nالنص: ").strip()
        
        if text.lower() in ['exit', 'خروج', 'quit']:
            print("شكراً لاستخدامك التطبيق!")
            break
        
        if not text:
            continue
        
        try:
            result = analyzer.analyze(text)
            
            print(f"\n{'='*60}")
            print("نتائج التحليل:")
            print(f"{'='*60}")
            print(f"النص الأصلي: {result['original_text']}")
            print(f"المشاعر: {result['sentiment'].upper()}")
            print(f"نسبة الثقة: {result['confidence']:.2%}")
            print(f"التصنيف: {result['label']}")
            
            if result['probabilities']:
                print(f"\nالاحتمالات:")
                labels = ['Negative', 'Neutral', 'Positive']
                for label, prob in zip(labels, result['probabilities']):
                    print(f"  {label}: {prob:.2%}")
            
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"خطأ في التحليل: {e}")

def streamlit_interface():
    """واجهة Streamlit"""
    st.set_page_config(
        page_title="تحليل مشاعر المراجعات المصرية",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 تحليل مشاعر مراجعات منتجات أمازون باللهجة المصرية")
    st.markdown("---")
    
    # البحث عن النماذج
    models_dir = "models"
    if not os.path.exists(models_dir):
        st.error("❌ مجلد النماذج غير موجود. يرجى تدريب النماذج أولاً")
        return
    
    model_files = [f for f in os.listdir(models_dir) if f.endswith('_model.pkl')]
    if not model_files:
        st.error("❌ لم يتم العثور على أي نماذج مدربة")
        return
    
    # اختيار النموذج
    selected_model = st.selectbox("اختر النموذج:", model_files)
    model_path = os.path.join(models_dir, selected_model)
    
    # البحث عن Vectorizer
    vectorizer_path = model_path.replace('_model.pkl', '_vectorizer.pkl')
    if not os.path.exists(vectorizer_path):
        vectorizer_path = None
        st.warning("⚠️ Vectorizer غير موجود. قد لا يعمل التحليل بشكل صحيح")
    
    # تحميل المحلل
    @st.cache_resource
    def load_analyzer(model_path, vectorizer_path):
        return SentimentAnalyzer(model_path, vectorizer_path)
    
    try:
        analyzer = load_analyzer(model_path, vectorizer_path)
        st.success(f"✅ تم تحميل النموذج: {selected_model}")
    except Exception as e:
        st.error(f"❌ خطأ في تحميل النموذج: {e}")
        return
    
    st.markdown("---")
    
    # إدخال النص
    st.subheader("أدخل النص المراد تحليله:")
    text_input = st.text_area("", height=150, placeholder="أدخل مراجعة المنتج هنا...")
    
    if st.button("تحليل المشاعر", type="primary"):
        if text_input:
            with st.spinner("جاري التحليل..."):
                result = analyzer.analyze(text_input)
            
            st.markdown("---")
            st.subheader("نتائج التحليل:")
            
            # عرض المشاعر
            sentiment = result['sentiment']
            confidence = result['confidence']
            
            col1, col2 = st.columns(2)
            
            with col1:
                if sentiment == 'positive':
                    st.success(f"✅ المشاعر: إيجابي")
                elif sentiment == 'negative':
                    st.error(f"❌ المشاعر: سلبي")
                else:
                    st.info(f"⚪ المشاعر: محايد")
            
            with col2:
                st.metric("نسبة الثقة", f"{confidence:.2%}")
            
            # عرض الاحتمالات
            if result['probabilities']:
                st.subheader("الاحتمالات:")
                labels = ['Negative', 'Neutral', 'Positive']
                probs = result['probabilities']
                
                for label, prob in zip(labels, probs):
                    st.progress(prob, text=f"{label}: {prob:.2%}")
            
            # عرض النص المعالج
            with st.expander("عرض النص المعالج"):
                st.write("**النص الأصلي:**")
                st.write(result['original_text'])
                st.write("**النص النظيف:**")
                st.write(result['cleaned_text'])
                st.write("**النص المعالج:**")
                st.write(result['processed_text'])
        else:
            st.warning("⚠️ يرجى إدخال نص للتحليل")

if __name__ == "__main__":
    if STREAMLIT_AVAILABLE:
        # استخدام Streamlit إذا كان متاحاً
        streamlit_interface()
    else:
        # استخدام CLI
        cli_interface()


