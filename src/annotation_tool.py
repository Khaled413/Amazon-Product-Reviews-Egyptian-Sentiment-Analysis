"""
أداة تصنيف المشاعر (Annotation Tool)
Sentiment Annotation Tool
"""

import os
import json
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime

class AnnotationTool:
    """فئة لتصنيف المشاعر"""
    
    SENTIMENT_LABELS = {
        'positive': 1,
        'negative': -1,
        'neutral': 0
    }
    
    LABEL_NAMES = {
        1: 'positive',
        -1: 'negative',
        0: 'neutral'
    }
    
    def __init__(self, data_file: str):
        """
        Args:
            data_file: مسار ملف البيانات المراد تصنيفها
        """
        self.data_file = data_file
        self.annotations = []
        self.load_data()
    
    def load_data(self):
        """تحميل البيانات"""
        if self.data_file.endswith('.json'):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        elif self.data_file.endswith('.csv'):
            df = pd.read_csv(self.data_file)
            self.data = df.to_dict('records')
        else:
            raise ValueError("نوع الملف غير مدعوم")
    
    def annotate_review(self, review_id: int, sentiment: str, annotator_name: str = "annotator1"):
        """
        تصنيف مراجعة واحدة
        
        Args:
            review_id: رقم المراجعة
            sentiment: المشاعر ('positive', 'negative', 'neutral')
            annotator_name: اسم المصنف
        """
        if sentiment.lower() not in self.SENTIMENT_LABELS:
            raise ValueError(f"المشاعر يجب أن تكون: {list(self.SENTIMENT_LABELS.keys())}")
        
        annotation = {
            'review_id': review_id,
            'text': self.data[review_id].get('text', ''),
            'sentiment': sentiment.lower(),
            'label': self.SENTIMENT_LABELS[sentiment.lower()],
            'annotator': annotator_name,
            'date': datetime.now().isoformat()
        }
        
        self.annotations.append(annotation)
        return annotation
    
    def resolve_conflicts(self, annotations: List[Dict]) -> Dict:
        """
        حل التعارضات بين المصنفين (Majority Vote)
        
        Args:
            annotations: قائمة التصنيفات
        
        Returns:
            Dict: التصنيف النهائي
        """
        if not annotations:
            return None
        
        # تجميع التصويتات
        votes = {}
        for ann in annotations:
            label = ann.get('label')
            votes[label] = votes.get(label, 0) + 1
        
        # اختيار الأكثر تصويتاً
        majority_label = max(votes, key=votes.get)
        
        return {
            'label': majority_label,
            'sentiment': self.LABEL_NAMES[majority_label],
            'confidence': votes[majority_label] / len(annotations),
            'votes': votes
        }
    
    def save_annotations(self, output_file: str = None):
        """
        حفظ التصنيفات
        
        Args:
            output_file: مسار ملف الحفظ (اختياري)
        """
        if output_file is None:
            base_name = os.path.basename(self.data_file)
            name, ext = os.path.splitext(base_name)
            output_file = f"data/annotated/{name}_annotated{ext}"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # دمج البيانات مع التصنيفات
        annotated_data = []
        for i, item in enumerate(self.data):
            # البحث عن تصنيفات هذه المراجعة
            review_annotations = [ann for ann in self.annotations if ann['review_id'] == i]
            
            if review_annotations:
                final_label = self.resolve_conflicts(review_annotations)
                annotated_item = item.copy()
                annotated_item['sentiment'] = final_label['sentiment']
                annotated_item['label'] = final_label['label']
                annotated_item['confidence'] = final_label['confidence']
                annotated_item['annotations'] = review_annotations
                annotated_data.append(annotated_item)
        
        # حفظ البيانات المصنفة
        if output_file.endswith('.json'):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(annotated_data, f, ensure_ascii=False, indent=2)
        elif output_file.endswith('.csv'):
            df = pd.DataFrame(annotated_data)
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"تم حفظ {len(annotated_data)} مراجعة مصنفة في: {output_file}")
        return output_file
    
    def get_statistics(self) -> Dict:
        """إرجاع إحصائيات عن التصنيفات"""
        if not self.annotations:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
        
        stats = {
            'total': len(self.annotations),
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for ann in self.annotations:
            sentiment = ann.get('sentiment', '')
            if sentiment in stats:
                stats[sentiment] += 1
        
        return stats

def create_sample_annotations():
    """إنشاء تصنيفات تجريبية"""
    # تحميل البيانات النظيفة
    data_file = "data/cleaned/sample_reviews_cleaned.json"
    
    if not os.path.exists(data_file):
        print("ملف البيانات غير موجود. يرجى تشغيل data_cleaning.py أولاً")
        return
    
    annotator = AnnotationTool(data_file)
    
    # تصنيف المراجعات (محاكاة لـ 2 annotators)
    reviews_count = len(annotator.data)
    
    # Annotator 1
    for i in range(reviews_count):
        text = annotator.data[i].get('text', '').lower()
        if any(word in text for word in ['جامد', 'حلو', 'قوي', 'ممتاز', 'كويس', 'ينفع']):
            annotator.annotate_review(i, 'positive', 'annotator1')
        elif any(word in text for word in ['وحش', 'خايب', 'مش', 'مفيش', 'مينفعش']):
            annotator.annotate_review(i, 'negative', 'annotator1')
        else:
            annotator.annotate_review(i, 'neutral', 'annotator1')
    
    # Annotator 2 (محاكاة)
    for i in range(reviews_count):
        text = annotator.data[i].get('text', '').lower()
        if any(word in text for word in ['جامد', 'حلو', 'قوي', 'ممتاز']):
            annotator.annotate_review(i, 'positive', 'annotator2')
        elif any(word in text for word in ['وحش', 'خايب', 'مش']):
            annotator.annotate_review(i, 'negative', 'annotator2')
        else:
            annotator.annotate_review(i, 'neutral', 'annotator2')
    
    # حفظ التصنيفات
    annotator.save_annotations()
    
    # عرض الإحصائيات
    stats = annotator.get_statistics()
    print("\nإحصائيات التصنيف:")
    print(f"إجمالي التصنيفات: {stats['total']}")
    print(f"إيجابي: {stats['positive']}")
    print(f"سلبي: {stats['negative']}")
    print(f"محايد: {stats['neutral']}")

if __name__ == "__main__":
    create_sample_annotations()


