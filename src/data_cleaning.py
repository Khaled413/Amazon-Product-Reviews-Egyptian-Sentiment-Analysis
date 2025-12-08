"""
تنظيف البيانات من الضوضاء
Data Cleaning Module
"""

import os
import json
import re
import emoji
import pandas as pd
from typing import List, Dict, Optional

class DataCleaner:
    """فئة لتنظيف البيانات"""
    
    def __init__(self):
        self.cleaned_data = []
    
    def remove_emojis(self, text: str) -> str:
        """إزالة الإيموجيز أو تحويلها لنص"""
        # إزالة الإيموجيز
        text = emoji.demojize(text)
        # إزالة أي نص متبقي من الإيموجيز
        text = re.sub(r':[a-z_]+:', '', text)
        return text.strip()
    
    def remove_urls(self, text: str) -> str:
        """إزالة الروابط"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        text = re.sub(url_pattern, '', text)
        return text.strip()
    
    def remove_mentions(self, text: str) -> str:
        """إزالة الإشارات @"""
        text = re.sub(r'@\w+', '', text)
        return text.strip()
    
    def remove_hashtags(self, text: str) -> str:
        """إزالة الهاشتاج"""
        text = re.sub(r'#\w+', '', text)
        return text.strip()
    
    def remove_elongated_chars(self, text: str) -> str:
        """تقليل الحروف المكررة (مثل: حلوووو -> حلو)"""
        # تقليل أي حرف مكرر أكثر من مرتين إلى حرفين
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        return text
    
    def remove_numbers(self, text: str, keep_arabic_numbers: bool = False) -> str:
        """إزالة الأرقام"""
        if keep_arabic_numbers:
            # إزالة الأرقام الإنجليزية فقط
            text = re.sub(r'[0-9]', '', text)
        else:
            # إزالة جميع الأرقام
            text = re.sub(r'[0-9٠-٩]', '', text)
        return text.strip()
    
    def normalize_arabic_chars(self, text: str) -> str:
        """توحيد أشكال الحروف العربية (ا، أ، إ)"""
        # توحيد الألف
        text = text.replace('أ', 'ا')
        text = text.replace('إ', 'ا')
        text = text.replace('آ', 'ا')
        
        # توحيد التاء المربوطة
        text = text.replace('ة', 'ه')
        
        # توحيد الياء
        text = text.replace('ى', 'ي')
        
        return text
    
    def remove_extra_spaces(self, text: str) -> str:
        """إزالة المسافات الزائدة"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def remove_special_chars(self, text: str, keep_arabic_punctuation: bool = True) -> str:
        """إزالة الأحرف الخاصة"""
        if keep_arabic_punctuation:
            # الاحتفاظ بعلامات الترقيم العربية
            arabic_punct = '،؛؟'
            text = re.sub(r'[^\w\s' + re.escape(arabic_punct) + ']', '', text)
        else:
            # إزالة جميع الأحرف الخاصة
            text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def clean_text(self, text: str, 
                   remove_emojis_flag: bool = True,
                   remove_urls_flag: bool = True,
                   remove_mentions_flag: bool = True,
                   remove_hashtags_flag: bool = True,
                   remove_elongated_flag: bool = True,
                   remove_numbers_flag: bool = True,
                   normalize_arabic_flag: bool = True,
                   remove_special_chars_flag: bool = True) -> str:
        """
        تنظيف نص واحد
        
        Args:
            text: النص المراد تنظيفه
            remove_emojis_flag: إزالة الإيموجيز
            remove_urls_flag: إزالة الروابط
            remove_mentions_flag: إزالة الإشارات
            remove_hashtags_flag: إزالة الهاشتاج
            remove_elongated_flag: إزالة الحروف المكررة
            remove_numbers_flag: إزالة الأرقام
            normalize_arabic_flag: توحيد الحروف العربية
            remove_special_chars_flag: إزالة الأحرف الخاصة
        
        Returns:
            str: النص النظيف
        """
        if not text or len(text.strip()) == 0:
            return ""
        
        cleaned = text
        
        if remove_emojis_flag:
            cleaned = self.remove_emojis(cleaned)
        
        if remove_urls_flag:
            cleaned = self.remove_urls(cleaned)
        
        if remove_mentions_flag:
            cleaned = self.remove_mentions(cleaned)
        
        if remove_hashtags_flag:
            cleaned = self.remove_hashtags(cleaned)
        
        if remove_elongated_flag:
            cleaned = self.remove_elongated_chars(cleaned)
        
        if normalize_arabic_flag:
            cleaned = self.normalize_arabic_chars(cleaned)
        
        if remove_numbers_flag:
            cleaned = self.remove_numbers(cleaned)
        
        if remove_special_chars_flag:
            cleaned = self.remove_special_chars(cleaned)
        
        cleaned = self.remove_extra_spaces(cleaned)
        
        return cleaned
    
    def clean_dataset(self, input_file: str, output_file: str = None):
        """
        تنظيف ملف بيانات كامل
        
        Args:
            input_file: مسار ملف البيانات المدخل
            output_file: مسار ملف البيانات النظيف (اختياري)
        """
        # قراءة البيانات
        if input_file.endswith('.json'):
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
            data = df.to_dict('records')
        else:
            raise ValueError("نوع الملف غير مدعوم. استخدم JSON أو CSV")
        
        # تنظيف البيانات
        cleaned_data = []
        for item in data:
            original_text = item.get('text', '')
            cleaned_text = self.clean_text(original_text)
            
            if cleaned_text and len(cleaned_text.strip()) > 0:
                cleaned_item = item.copy()
                cleaned_item['text'] = cleaned_text
                cleaned_item['original_text'] = original_text
                cleaned_item['cleaned'] = True
                cleaned_data.append(cleaned_item)
        
        # حفظ البيانات النظيفة
        if output_file is None:
            base_name = os.path.basename(input_file)
            name, ext = os.path.splitext(base_name)
            output_file = f"data/cleaned/{name}_cleaned{ext}"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        if output_file.endswith('.json'):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        elif output_file.endswith('.csv'):
            df_cleaned = pd.DataFrame(cleaned_data)
            df_cleaned.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"تم تنظيف {len(cleaned_data)} مراجعة من أصل {len(data)}")
        print(f"تم حفظ البيانات النظيفة في: {output_file}")
        
        return cleaned_data

if __name__ == "__main__":
    # اختبار التنظيف
    cleaner = DataCleaner()
    
    # مثال على نص يحتاج تنظيف
    test_text = "المنتج ده حلوووووووووو 🎉🎉🎉 @user123 #review http://example.com"
    cleaned = cleaner.clean_text(test_text)
    
    print(f"النص الأصلي: {test_text}")
    print(f"النص النظيف: {cleaned}")
    
    # تنظيف ملف إذا كان موجود
    sample_file = "data/raw/sample_reviews.json"
    if os.path.exists(sample_file):
        cleaner.clean_dataset(sample_file)


