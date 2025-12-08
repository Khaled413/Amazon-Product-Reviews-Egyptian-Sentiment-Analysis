"""
مثال على جمع البيانات من مصادر مختلفة
Example: Data Collection from Various Sources
"""

import sys
import os

# إضافة المسارات المطلوبة
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_collection import DataCollector
from src.web_scrapers import WebScraper, create_egyptian_reviews_dataset

def example_1_create_egyptian_data():
    """مثال 1: إنشاء بيانات مصرية بالعامية"""
    print("="*60)
    print("مثال 1: إنشاء بيانات مصرية بالعامية")
    print("="*60)
    
    # إنشاء بيانات مصرية
    egyptian_reviews = create_egyptian_reviews_dataset()
    
    # حفظ البيانات
    collector = DataCollector()
    collector.collect_from_manual_input(egyptian_reviews)
    collector.save_collected_data("egyptian_reviews_example.json")
    
    print(f"✓ تم إنشاء {len(egyptian_reviews)} مراجعة مصرية")
    return collector

def example_2_collect_from_amazon():
    """مثال 2: جمع البيانات من أمازون"""
    print("="*60)
    print("مثال 2: جمع البيانات من أمازون")
    print("="*60)
    
    scraper = WebScraper()
    
    # ضع رابط المنتج هنا
    amazon_url = "https://www.amazon.eg/dp/PRODUCT_ID"
    
    print(f"محاولة جمع البيانات من: {amazon_url}")
    print("ملاحظة: يحتاج Selenium و ChromeDriver")
    
    reviews = scraper.scrape_amazon_egypt(amazon_url, max_reviews=20)
    
    if reviews:
        scraper.save_reviews(reviews, "amazon_reviews_example.json")
        print(f"✓ تم جمع {len(reviews)} مراجعة من أمازون")
    else:
        print("⚠ لم يتم جمع أي بيانات. تأكد من إعدادات Selenium")
    
    return reviews

def example_3_collect_from_noon():
    """مثال 3: جمع البيانات من نون"""
    print("="*60)
    print("مثال 3: جمع البيانات من نون")
    print("="*60)
    
    scraper = WebScraper()
    
    # ضع رابط المنتج هنا
    noon_url = "https://www.noon.com/egypt-en/product-url"
    
    print(f"محاولة جمع البيانات من: {noon_url}")
    
    reviews = scraper.scrape_noon_egypt(noon_url, max_reviews=20)
    
    if reviews:
        scraper.save_reviews(reviews, "noon_reviews_example.json")
        print(f"✓ تم جمع {len(reviews)} مراجعة من نون")
    else:
        print("⚠ لم يتم جمع أي بيانات")
    
    return reviews

def example_4_collect_from_olx():
    """مثال 4: جمع البيانات من أوليكس"""
    print("="*60)
    print("مثال 4: جمع البيانات من أوليكس")
    print("="*60)
    
    scraper = WebScraper()
    
    # ضع رابط الإعلان هنا
    olx_url = "https://www.olx.com.eg/ad/AD_ID"
    
    print(f"محاولة جمع البيانات من: {olx_url}")
    
    comments = scraper.scrape_olx_egypt(olx_url, max_comments=20)
    
    if comments:
        scraper.save_reviews(comments, "olx_comments_example.json")
        print(f"✓ تم جمع {len(comments)} تعليق من أوليكس")
    else:
        print("⚠ لم يتم جمع أي بيانات")
    
    return comments

def example_5_collect_from_facebook():
    """مثال 5: جمع البيانات من فيسبوك"""
    print("="*60)
    print("مثال 5: جمع البيانات من فيسبوك")
    print("="*60)
    
    scraper = WebScraper()
    
    # ضع رابط المنشور هنا
    facebook_url = "https://www.facebook.com/PAGE/posts/POST_ID"
    
    print(f"محاولة جمع البيانات من: {facebook_url}")
    print("ملاحظة: يحتاج Selenium و ChromeDriver")
    
    comments = scraper.scrape_facebook_comments(facebook_url, max_comments=20)
    
    if comments:
        scraper.save_reviews(comments, "facebook_comments_example.json")
        print(f"✓ تم جمع {len(comments)} تعليق من فيسبوك")
    else:
        print("⚠ لم يتم جمع أي بيانات. تأكد من إعدادات Selenium")
    
    return comments

if __name__ == "__main__":
    print("\n" + "="*60)
    print("أمثلة على جمع البيانات")
    print("="*60 + "\n")
    
    # مثال 1: إنشاء بيانات مصرية (يعمل دائماً)
    example_1_create_egyptian_data()
    
    print("\n" + "="*60)
    print("ملاحظة: الأمثلة التالية تحتاج روابط حقيقية وإعدادات Web Scraping")
    print("="*60 + "\n")
    
    # أمثلة أخرى (تعليق لأنها تحتاج روابط حقيقية)
    # example_2_collect_from_amazon()
    # example_3_collect_from_noon()
    # example_4_collect_from_olx()
    # example_5_collect_from_facebook()
    
    print("\n✓ انتهت الأمثلة!")
    print("\nلجمع بيانات أكثر، استخدم:")
    print("  python src/collect_from_websites.py --egyptian-only")


