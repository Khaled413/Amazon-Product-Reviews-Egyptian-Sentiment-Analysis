"""
فلترة البيانات للهجة المصرية فقط
Dialect Filtering Module
"""

import os
import json
import pandas as pd
from typing import List, Dict, Tuple
import sys

# إضافة مجلد utils إلى المسار
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.dialect_detector import detect_egyptian_dialect, filter_egyptian_texts

class DialectFilter:
    """فئة لفلترة البيانات للهجة المصرية فقط"""
    
    def __init__(self, threshold: float = 0.3):
        """
        Args:
            threshold: الحد الأدنى لنسبة الثقة (افتراضي 0.3)
        """
        self.threshold = threshold
    
    def filter_text(self, text: str) -> Tuple[bool, float]:
        """
        فحص نص واحد إذا كان باللهجة المصرية
        
        Args:
            text: النص المراد فحصه
        
        Returns:
            tuple[bool, float]: (هل النص مصري, نسبة الثقة)
        """
        return detect_egyptian_dialect(text, self.threshold)
    
    def filter_dataset(self, input_file: str, output_file: str = None):
        """
        فلترة ملف بيانات كامل
        
        Args:
            input_file: مسار ملف البيانات المدخل
            output_file: مسار ملف البيانات المفلترة (اختياري)
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
        
        # فلترة البيانات
        filtered_data = []
        egyptian_count = 0
        non_egyptian_count = 0
        
        for item in data:
            text = item.get('text', '')
            is_egyptian, confidence = self.filter_text(text)
            
            if is_egyptian:
                filtered_item = item.copy()
                filtered_item['dialect_confidence'] = confidence
                filtered_item['is_egyptian'] = True
                filtered_data.append(filtered_item)
                egyptian_count += 1
            else:
                non_egyptian_count += 1
        
        # حفظ البيانات المفلترة
        if output_file is None:
            base_name = os.path.basename(input_file)
            name, ext = os.path.splitext(base_name)
            output_file = f"data/cleaned/{name}_egyptian_only{ext}"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        if output_file.endswith('.json'):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        elif output_file.endswith('.csv'):
            df_filtered = pd.DataFrame(filtered_data)
            df_filtered.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"\nنتائج الفلترة:")
        print(f"إجمالي المراجعات: {len(data)}")
        print(f"مراجعات مصرية: {egyptian_count} ({egyptian_count/len(data)*100:.2f}%)")
        print(f"مراجعات غير مصرية: {non_egyptian_count} ({non_egyptian_count/len(data)*100:.2f}%)")
        print(f"تم حفظ البيانات المفلترة في: {output_file}")
        
        return filtered_data
    
    def get_statistics(self, data: List[Dict]) -> Dict:
        """إرجاع إحصائيات عن البيانات المفلترة"""
        if not data:
            return {
                'total': 0,
                'egyptian': 0,
                'non_egyptian': 0,
                'avg_confidence': 0.0
            }
        
        egyptian_count = 0
        total_confidence = 0.0
        
        for item in data:
            is_egyptian = item.get('is_egyptian', False)
            if is_egyptian:
                egyptian_count += 1
                total_confidence += item.get('dialect_confidence', 0.0)
        
        return {
            'total': len(data),
            'egyptian': egyptian_count,
            'non_egyptian': len(data) - egyptian_count,
            'avg_confidence': total_confidence / egyptian_count if egyptian_count > 0 else 0.0
        }

if __name__ == "__main__":
    # اختبار الفلترة
    filter_tool = DialectFilter(threshold=0.3)
    
    # أمثلة للاختبار
    test_texts = [
        "المنتج ده جامد أوي والجودة قوية خالص",
        "This product is very good and high quality",
        "المنتج حلو والخدمة ممتازة",
        "المنتج جميل والخدمة ممتازة",  # فصحى
        "كده كويس يعني، مش وحش",
    ]
    
    print("نتائج فحص اللهجة المصرية:\n")
    for text in test_texts:
        is_egyptian, confidence = filter_tool.filter_text(text)
        status = "مصري ✓" if is_egyptian else "غير مصري ✗"
        print(f"{status} ({confidence:.2f}): {text}")
    
    # فلترة ملف إذا كان موجود
    sample_file = "data/cleaned/sample_reviews_cleaned.json"
    if os.path.exists(sample_file):
        filter_tool.filter_dataset(sample_file)

