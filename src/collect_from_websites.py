"""
سكريبت لجمع البيانات من مواقع الويب المختلفة
Script to collect data from various websites
"""

import os
import sys
import json
from datetime import datetime

# إضافة المسارات المطلوبة
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.data_collection import DataCollector
from src.web_scrapers import WebScraper, create_egyptian_reviews_dataset

def collect_from_all_sources():
    """جمع البيانات من جميع المصادر"""
    
    print("="*60)
    print("جمع البيانات من مصادر مختلفة")
    print("="*60)
    
    collector = DataCollector()
    scraper = WebScraper()
    
    all_reviews = []
    
    # 1. إنشاء بيانات مصرية كبيرة بالعامية
    print("\n[1/5] إنشاء بيانات مصرية بالعامية...")
    egyptian_reviews = create_egyptian_reviews_dataset()
    all_reviews.extend(egyptian_reviews)
    print(f"✓ تم إنشاء {len(egyptian_reviews)} مراجعة مصرية")
    
    # 2. جمع من أمازون (مثال)
    print("\n[2/5] محاولة جمع البيانات من أمازون...")
    print("ملاحظة: يحتاج Selenium و ChromeDriver")
    # amazon_url = "https://www.amazon.eg/product-url"  # ضع رابط المنتج هنا
    # amazon_reviews = scraper.scrape_amazon_egypt(amazon_url, max_reviews=20)
    # all_reviews.extend(amazon_reviews)
    # print(f"✓ تم جمع {len(amazon_reviews)} مراجعة من أمازون")
    
    # 3. جمع من نون (مثال)
    print("\n[3/5] محاولة جمع البيانات من نون...")
    # noon_url = "https://www.noon.com/product-url"  # ضع رابط المنتج هنا
    # noon_reviews = scraper.scrape_noon_egypt(noon_url, max_reviews=20)
    # all_reviews.extend(noon_reviews)
    # print(f"✓ تم جمع {len(noon_reviews)} مراجعة من نون")
    
    # 4. جمع من أوليكس (مثال)
    print("\n[4/5] محاولة جمع البيانات من أوليكس...")
    # olx_url = "https://www.olx.com.eg/ad-url"  # ضع رابط الإعلان هنا
    # olx_comments = scraper.scrape_olx_egypt(olx_url, max_comments=20)
    # all_reviews.extend(olx_comments)
    # print(f"✓ تم جمع {len(olx_comments)} تعليق من أوليكس")
    
    # 5. جمع من فيسبوك (مثال)
    print("\n[5/5] محاولة جمع البيانات من فيسبوك...")
    print("ملاحظة: يحتاج Selenium و ChromeDriver")
    # facebook_url = "https://www.facebook.com/post-url"  # ضع رابط المنشور هنا
    # facebook_comments = scraper.scrape_facebook_comments(facebook_url, max_comments=20)
    # all_reviews.extend(facebook_comments)
    # print(f"✓ تم جمع {len(facebook_comments)} تعليق من فيسبوك")
    
    # حفظ جميع البيانات
    if all_reviews:
        collector.collect_from_manual_input(all_reviews)
        filename = f"all_sources_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        collector.save_collected_data(filename)
        
        # إحصائيات
        stats = collector.get_statistics()
        print("\n" + "="*60)
        print("إحصائيات البيانات المجمعة:")
        print("="*60)
        print(f"إجمالي المراجعات: {stats['total_reviews']}")
        print(f"المصادر: {stats['sources']}")
        print(f"متوسط طول المراجعة: {stats['avg_length']:.2f} حرف")
        print("="*60)
    else:
        print("\nلم يتم جمع أي بيانات. تأكد من إعدادات Web Scraping")
    
    return collector

def collect_egyptian_data_only():
    """جمع البيانات المصرية فقط (بدون Web Scraping)"""
    
    print("="*60)
    print("إنشاء مجموعة بيانات مصرية بالعامية")
    print("="*60)
    
    # إنشاء بيانات مصرية كبيرة
    egyptian_reviews = create_egyptian_reviews_dataset()
    
    # حفظ البيانات
    collector = DataCollector()
    collector.collect_from_manual_input(egyptian_reviews)
    collector.save_collected_data("egyptian_reviews_large.json")
    
    # إحصائيات
    stats = collector.get_statistics()
    print("\n" + "="*60)
    print("إحصائيات البيانات:")
    print("="*60)
    print(f"إجمالي المراجعات: {stats['total_reviews']}")
    print(f"المصادر: {stats['sources']}")
    print(f"متوسط طول المراجعة: {stats['avg_length']:.2f} حرف")
    
    # تفصيل حسب المشاعر
    positive = len([r for r in egyptian_reviews if 'positive' in r['source']])
    negative = len([r for r in egyptian_reviews if 'negative' in r['source']])
    neutral = len([r for r in egyptian_reviews if 'neutral' in r['source']])
    
    print(f"\nالتوزيع حسب المشاعر:")
    print(f"  إيجابية: {positive}")
    print(f"  سلبية: {negative}")
    print(f"  محايدة: {neutral}")
    print("="*60)
    
    return collector

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='جمع البيانات من مصادر مختلفة')
    parser.add_argument('--egyptian-only', action='store_true', 
                       help='إنشاء بيانات مصرية فقط (بدون Web Scraping)')
    parser.add_argument('--all-sources', action='store_true',
                       help='محاولة جمع البيانات من جميع المصادر')
    
    args = parser.parse_args()
    
    if args.egyptian_only:
        collect_egyptian_data_only()
    elif args.all_sources:
        collect_from_all_sources()
    else:
        # افتراضي: جمع البيانات المصرية فقط
        print("استخدام --egyptian-only للبيانات المصرية فقط")
        print("استخدام --all-sources لمحاولة جمع من جميع المصادر")
        collect_egyptian_data_only()

