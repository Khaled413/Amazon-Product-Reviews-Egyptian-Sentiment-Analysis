"""
جمع البيانات من مصادر مصرية
Data Collection from Egyptian Sources
"""

import os
import json
import csv
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

class DataCollector:
    """فئة لجمع البيانات من مصادر مختلفة"""
    
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.collected_data = []
    
    def collect_from_manual_input(self, reviews: List[Dict[str, str]]):
        """
        جمع البيانات يدوياً (للاستخدام في البداية)
        
        Args:
            reviews: قائمة من المراجعات كل مراجعة عبارة عن dict يحتوي على 'text' و 'source'
        """
        for review in reviews:
            self.collected_data.append({
                'text': review.get('text', ''),
                'source': review.get('source', 'manual'),
                'date_collected': datetime.now().isoformat(),
                'raw': True
            })
    
    def collect_from_file(self, file_path: str, source_name: str = "file"):
        """
        جمع البيانات من ملف نصي أو CSV
        
        Args:
            file_path: مسار الملف
            source_name: اسم المصدر
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    text = str(row.get('review', row.get('text', '')))
                    if text and len(text.strip()) > 0:
                        self.collected_data.append({
                            'text': text,
                            'source': source_name,
                            'date_collected': datetime.now().isoformat(),
                            'raw': True
                        })
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        text = str(item.get('review', item.get('text', '')))
                        if text and len(text.strip()) > 0:
                            self.collected_data.append({
                                'text': text,
                                'source': source_name,
                                'date_collected': datetime.now().isoformat(),
                                'raw': True
                            })
            else:
                # ملف نصي عادي
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        text = line.strip()
                        if text and len(text) > 0:
                            self.collected_data.append({
                                'text': text,
                                'source': source_name,
                                'date_collected': datetime.now().isoformat(),
                                'raw': True
                            })
        except Exception as e:
            print(f"خطأ في قراءة الملف {file_path}: {e}")
    
    def save_collected_data(self, filename: str = None):
        """
        حفظ البيانات المجمعة
        
        Args:
            filename: اسم الملف (اختياري)
        """
        if filename is None:
            filename = f"collected_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        print(f"تم حفظ {len(self.collected_data)} مراجعة في {filepath}")
        return filepath
    
    def get_statistics(self) -> Dict:
        """إرجاع إحصائيات عن البيانات المجمعة"""
        if not self.collected_data:
            return {
                'total_reviews': 0,
                'sources': {},
                'avg_length': 0
            }
        
        sources = {}
        total_length = 0
        
        for review in self.collected_data:
            source = review.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
            total_length += len(review.get('text', ''))
        
        return {
            'total_reviews': len(self.collected_data),
            'sources': sources,
            'avg_length': total_length / len(self.collected_data) if self.collected_data else 0
        }

def create_sample_data():
    """إنشاء بيانات تجريبية للاختبار - بيانات مصرية بالعامية"""
    sample_reviews = [
        # Positive reviews - إيجابية
        {
            'text': 'المنتج ده جامد أوي والجودة قوية خالص، أنصح بيه',
            'source': 'sample_positive'
        },
        {
            'text': 'حلوة أوي والجودة عالية، مستريح في استخدامها',
            'source': 'sample_positive'
        },
        {
            'text': 'المنتج ده قوي أوي والخدمة ممتازة، أنصح بيه',
            'source': 'sample_positive'
        },
        {
            'text': 'كويسة أوي والمنتج خالص، جربته ومرتاح بيه',
            'source': 'sample_positive'
        },
        {
            'text': 'المنتج ده حلو أوي والجودة عالية، ينفع كويس',
            'source': 'sample_positive'
        },
        {
            'text': 'ممتازة أوي والخدمة سريعة، أنصح بيه خالص',
            'source': 'sample_positive'
        },
        {
            'text': 'المنتج جامد والجودة قوية، مستريح في استخدامه',
            'source': 'sample_positive'
        },
        {
            'text': 'حلوة أوي والمنتج كويس، جربته ومرتاح بيه',
            'source': 'sample_positive'
        },
        {
            'text': 'المنتج ده قوي والخدمة ممتازة، أنصح بيه خالص',
            'source': 'sample_positive'
        },
        {
            'text': 'كويسة أوي والجودة عالية، ينفع كويس',
            'source': 'sample_positive'
        },
        {
            'text': 'المنتج ده حلو والخدمة سريعة، مستريح بيه',
            'source': 'sample_positive'
        },
        {
            'text': 'ممتازة أوي والمنتج خالص، جربته ومرتاح بيه',
            'source': 'sample_positive'
        },
        
        # Negative reviews - سلبية
        {
            'text': 'مش حلو خالص والمنتج خايب، غالي أوي ومش يستاهل',
            'source': 'sample_negative'
        },
        {
            'text': 'مش كويسة خالص، مينفعش تستخدمها كويس',
            'source': 'sample_negative'
        },
        {
            'text': 'مش حلو والمنتج وحش، غالي أوي ومش يستاهل',
            'source': 'sample_negative'
        },
        {
            'text': 'المنتج ده خايب أوي والجودة وحشة، مينفعش',
            'source': 'sample_negative'
        },
        {
            'text': 'مش كويس خالص والخدمة وحشة، غالي أوي',
            'source': 'sample_negative'
        },
        {
            'text': 'المنتج ده وحش والجودة خايب، مينفعش يستخدم',
            'source': 'sample_negative'
        },
        {
            'text': 'مش حلوة خالص والمنتج خايب، غالي أوي',
            'source': 'sample_negative'
        },
        {
            'text': 'المنتج ده وحش والخدمة خايب، مينفعش',
            'source': 'sample_negative'
        },
        {
            'text': 'مش كويسة والجودة وحشة، غالي أوي ومش يستاهل',
            'source': 'sample_negative'
        },
        {
            'text': 'المنتج ده خايب والخدمة وحشة، مينفعش يستخدم',
            'source': 'sample_negative'
        },
        
        # Neutral reviews - محايدة
        {
            'text': 'المنتج عادي يعني، مش حلو ومش وحش، كويس',
            'source': 'sample_neutral'
        },
        {
            'text': 'عادي يعني، مش حلو ومش وحش، كويس',
            'source': 'sample_neutral'
        },
        {
            'text': 'المنتج عادي والجودة متوسطة، مش حلو ومش وحش',
            'source': 'sample_neutral'
        },
        {
            'text': 'كويس يعني، مش حلو أوي ومش وحش، عادي',
            'source': 'sample_neutral'
        },
        {
            'text': 'المنتج عادي والخدمة متوسطة، مش حلو ومش وحش',
            'source': 'sample_neutral'
        },
        {
            'text': 'عادي يعني، مش حلو ومش وحش، كويس',
            'source': 'sample_neutral'
        },
    ]
    
    collector = DataCollector()
    collector.collect_from_manual_input(sample_reviews)
    collector.save_collected_data("sample_reviews.json")
    
    stats = collector.get_statistics()
    print("\nإحصائيات البيانات المجمعة:")
    print(f"إجمالي المراجعات: {stats['total_reviews']}")
    print(f"المصادر: {stats['sources']}")
    print(f"متوسط طول المراجعة: {stats['avg_length']:.2f} حرف")
    
    return collector

if __name__ == "__main__":
    print("بدء جمع البيانات...")
    collector = create_sample_data()
    print("تم جمع البيانات بنجاح!")
    print("\nلجمع بيانات أكثر، استخدم:")
    print("  python src/collect_from_websites.py --egyptian-only")
    print("  python src/collect_from_websites.py --all-sources")

