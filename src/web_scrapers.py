"""
جمع البيانات من مواقع الويب (أمازون، نون، أوليكس، فيسبوك)
Web Scraping for Amazon, Noon, OLX, Facebook
"""

import os
import json
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import re

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("تحذير: Selenium غير مثبت. بعض وظائف Web Scraping قد لا تعمل")

class WebScraper:
    """فئة لجمع البيانات من مواقع الويب"""
    
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.collected_data = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_amazon_egypt(self, product_url: str, max_reviews: int = 50) -> List[Dict]:
        """
        جمع مراجعات من أمازون مصر
        
        Args:
            product_url: رابط المنتج
            max_reviews: الحد الأقصى للمراجعات
        
        Returns:
            List[Dict]: قائمة المراجعات
        """
        reviews = []
        
        try:
            # ملاحظة: أمازون يحتاج Selenium للوصول للمراجعات
            if not SELENIUM_AVAILABLE:
                print("تحذير: Selenium غير متاح. استخدام طريقة بديلة...")
                return self._scrape_amazon_alternative(product_url, max_reviews)
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(product_url)
            
            # انتظار تحميل المراجعات
            time.sleep(3)
            
            # البحث عن عناصر المراجعات
            review_elements = driver.find_elements(By.CSS_SELECTOR, '[data-hook="review-body"]')
            
            for element in review_elements[:max_reviews]:
                try:
                    review_text = element.text.strip()
                    if review_text and len(review_text) > 10:
                        reviews.append({
                            'text': review_text,
                            'source': 'amazon_egypt',
                            'date_collected': datetime.now().isoformat()
                        })
                except:
                    continue
            
            driver.quit()
            
        except Exception as e:
            print(f"خطأ في جمع البيانات من أمازون: {e}")
        
        return reviews
    
    def _scrape_amazon_alternative(self, product_url: str, max_reviews: int) -> List[Dict]:
        """طريقة بديلة لجمع البيانات من أمازون"""
        # في حالة عدم توفر Selenium، يمكن استخدام API أو ملفات محفوظة
        print("استخدام بيانات تجريبية من أمازون...")
        return []
    
    def scrape_noon_egypt(self, product_url: str, max_reviews: int = 50) -> List[Dict]:
        """
        جمع مراجعات من نون مصر
        
        Args:
            product_url: رابط المنتج
            max_reviews: الحد الأقصى للمراجعات
        
        Returns:
            List[Dict]: قائمة المراجعات
        """
        reviews = []
        
        try:
            response = requests.get(product_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # البحث عن عناصر المراجعات (يحتاج تعديل حسب هيكل الموقع)
                review_elements = soup.find_all('div', class_=re.compile(r'review|comment|rating'))
                
                for element in review_elements[:max_reviews]:
                    try:
                        review_text = element.get_text(strip=True)
                        if review_text and len(review_text) > 10:
                            reviews.append({
                                'text': review_text,
                                'source': 'noon_egypt',
                                'date_collected': datetime.now().isoformat()
                            })
                    except:
                        continue
            
        except Exception as e:
            print(f"خطأ في جمع البيانات من نون: {e}")
        
        return reviews
    
    def scrape_olx_egypt(self, product_url: str, max_comments: int = 50) -> List[Dict]:
        """
        جمع تعليقات من أوليكس مصر
        
        Args:
            product_url: رابط الإعلان
            max_comments: الحد الأقصى للتعليقات
        
        Returns:
            List[Dict]: قائمة التعليقات
        """
        comments = []
        
        try:
            response = requests.get(product_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # البحث عن التعليقات
                comment_elements = soup.find_all('div', class_=re.compile(r'comment|review|message'))
                
                for element in comment_elements[:max_comments]:
                    try:
                        comment_text = element.get_text(strip=True)
                        if comment_text and len(comment_text) > 10:
                            comments.append({
                                'text': comment_text,
                                'source': 'olx_egypt',
                                'date_collected': datetime.now().isoformat()
                            })
                    except:
                        continue
            
        except Exception as e:
            print(f"خطأ في جمع البيانات من أوليكس: {e}")
        
        return comments
    
    def scrape_facebook_comments(self, post_url: str, max_comments: int = 50) -> List[Dict]:
        """
        جمع تعليقات من فيسبوك
        
        ملاحظة: فيسبوك يحتاج API أو Selenium للوصول للتعليقات
        
        Args:
            post_url: رابط المنشور
            max_comments: الحد الأقصى للتعليقات
        
        Returns:
            List[Dict]: قائمة التعليقات
        """
        comments = []
        
        try:
            if not SELENIUM_AVAILABLE:
                print("تحذير: Selenium غير متاح. فيسبوك يحتاج Selenium للوصول للتعليقات")
                return comments
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(post_url)
            
            # انتظار تحميل التعليقات
            time.sleep(5)
            
            # البحث عن عناصر التعليقات
            comment_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="comment"]')
            
            for element in comment_elements[:max_comments]:
                try:
                    comment_text = element.text.strip()
                    if comment_text and len(comment_text) > 10:
                        comments.append({
                            'text': comment_text,
                            'source': 'facebook',
                            'date_collected': datetime.now().isoformat()
                        })
                except:
                    continue
            
            driver.quit()
            
        except Exception as e:
            print(f"خطأ في جمع البيانات من فيسبوك: {e}")
        
        return comments
    
    def save_reviews(self, reviews: List[Dict], filename: str = None):
        """حفظ المراجعات"""
        if filename is None:
            filename = f"web_scraped_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        
        print(f"تم حفظ {len(reviews)} مراجعة في {filepath}")
        return filepath

def create_egyptian_reviews_dataset():
    """إنشاء مجموعة بيانات مصرية كبيرة بالعامية"""
    
    # بيانات مصرية إيجابية بالعامية
    positive_reviews = [
        'المنتج ده جامد أوي والجودة قوية خالص، أنصح بيه',
        'حلوة أوي والجودة عالية، مستريح في استخدامها',
        'المنتج ده قوي أوي والخدمة ممتازة، أنصح بيه',
        'كويسة أوي والمنتج خالص، جربته ومرتاح بيه',
        'المنتج ده حلو أوي والجودة عالية، ينفع كويس',
        'ممتازة أوي والخدمة سريعة، أنصح بيه خالص',
        'المنتج جامد والجودة قوية، مستريح في استخدامه',
        'حلوة أوي والمنتج كويس، جربته ومرتاح بيه',
        'المنتج ده قوي والخدمة ممتازة، أنصح بيه خالص',
        'كويسة أوي والجودة عالية، ينفع كويس',
        'المنتج ده حلو والخدمة سريعة، مستريح بيه',
        'ممتازة أوي والمنتج خالص، جربته ومرتاح بيه',
        'المنتج ده حلو أوي والجودة عالية خالص',
        'كويسة والخدمة ممتازة، أنصح بيه',
        'المنتج جامد والجودة قوية، مستريح بيه',
        'حلوة أوي والمنتج كويس، ينفع كويس',
        'المنتج ده قوي والخدمة سريعة، أنصح بيه',
        'ممتازة والجودة عالية، مستريح في استخدامها',
        'المنتج ده حلو والخدمة ممتازة، أنصح بيه خالص',
        'كويسة أوي والمنتج خالص، جربته ومرتاح بيه',
    ]
    
    # بيانات مصرية سلبية بالعامية
    negative_reviews = [
        'مش حلو خالص والمنتج خايب، غالي أوي ومش يستاهل',
        'مش كويسة خالص، مينفعش تستخدمها كويس',
        'مش حلو والمنتج وحش، غالي أوي ومش يستاهل',
        'المنتج ده خايب أوي والجودة وحشة، مينفعش',
        'مش كويس خالص والخدمة وحشة، غالي أوي',
        'المنتج ده وحش والجودة خايب، مينفعش يستخدم',
        'مش حلوة خالص والمنتج خايب، غالي أوي',
        'المنتج ده وحش والخدمة خايب، مينفعش',
        'مش كويسة والجودة وحشة، غالي أوي ومش يستاهل',
        'المنتج ده خايب والخدمة وحشة، مينفعش يستخدم',
        'مش حلو والمنتج خايب، غالي أوي',
        'المنتج ده وحش والجودة خايب، مينفعش',
        'مش كويسة خالص والخدمة وحشة، غالي أوي',
        'المنتج ده خايب والمنتج وحش، مينفعش يستخدم',
        'مش حلوة والجودة خايب، غالي أوي ومش يستاهل',
        'المنتج ده وحش والخدمة خايب، مينفعش',
        'مش كويس والمنتج خايب، غالي أوي',
        'المنتج ده خايب والجودة وحشة، مينفعش يستخدم',
        'مش حلوة خالص والخدمة وحشة، غالي أوي',
        'المنتج ده وحش والمنتج خايب، مينفعش',
    ]
    
    # بيانات مصرية محايدة بالعامية
    neutral_reviews = [
        'المنتج عادي يعني، مش حلو ومش وحش، كويس',
        'عادي يعني، مش حلو ومش وحش، كويس',
        'المنتج عادي والجودة متوسطة، مش حلو ومش وحش',
        'كويس يعني، مش حلو أوي ومش وحش، عادي',
        'المنتج عادي والخدمة متوسطة، مش حلو ومش وحش',
        'عادي يعني، مش حلو ومش وحش، كويس',
        'المنتج عادي والجودة متوسطة، مش حلو ومش وحش',
        'كويس يعني، مش حلو أوي ومش وحش، عادي',
        'المنتج عادي والخدمة متوسطة، مش حلو ومش وحش',
        'عادي يعني، مش حلو ومش وحش، كويس',
    ]
    
    # دمج جميع البيانات
    all_reviews = []
    
    for text in positive_reviews:
        all_reviews.append({
            'text': text,
            'source': 'egyptian_positive',
            'date_collected': datetime.now().isoformat()
        })
    
    for text in negative_reviews:
        all_reviews.append({
            'text': text,
            'source': 'egyptian_negative',
            'date_collected': datetime.now().isoformat()
        })
    
    for text in neutral_reviews:
        all_reviews.append({
            'text': text,
            'source': 'egyptian_neutral',
            'date_collected': datetime.now().isoformat()
        })
    
    return all_reviews

if __name__ == "__main__":
    # إنشاء مجموعة بيانات مصرية كبيرة
    print("إنشاء مجموعة بيانات مصرية بالعامية...")
    reviews = create_egyptian_reviews_dataset()
    
    scraper = WebScraper()
    scraper.save_reviews(reviews, "egyptian_reviews_large.json")
    
    print(f"\nتم إنشاء {len(reviews)} مراجعة مصرية بالعامية")
    print(f"  - إيجابية: {len([r for r in reviews if 'positive' in r['source']])}")
    print(f"  - سلبية: {len([r for r in reviews if 'negative' in r['source']])}")
    print(f"  - محايدة: {len([r for r in reviews if 'neutral' in r['source']])}")


