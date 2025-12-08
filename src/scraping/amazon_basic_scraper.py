# -*- coding: utf-8 -*-
"""
Amazon Basic Info Scraper
يجيب معلومات أساسية من صفحة المنتج: النجوم، عدد التقييمات، نسبة الرضا
ثم يولد عينة واقعية من التقييمات بناءً على البيانات الحقيقية
"""

from __future__ import annotations

import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup


def log(msg: str) -> None:
    """Print debug messages to stderr to keep stdout clean for JSON output."""
    print(msg, file=sys.stderr)


@dataclass
class Review:
    author: str
    date: str
    rating: float
    title: str
    text: str
    images: List[str]
    verified_purchase: bool


class AmazonBasicScraper:
    """
    يجيب المعلومات الأساسية من صفحة المنتج ويولد تقييمات واقعية
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def fetch_product_info(self, product_url: str) -> Dict[str, Any]:
        """
        يجيب معلومات المنتج الأساسية من أمازون
        """
        try:
            log("🔄 جاري جلب معلومات المنتج من أمازون...")
            response = requests.get(product_url, headers=self.headers, timeout=8)
            
            if response.status_code != 200:
                log(f"⚠️ Status: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # استخراج اسم المنتج
            title = self._extract_title(soup)
            
            # استخراج التقييم (النجوم)
            rating = self._extract_rating(soup)
            
            # استخراج عدد التقييمات
            review_count = self._extract_review_count(soup)
            
            # استخراج توزيع النجوم
            star_distribution = self._extract_star_distribution(soup)
            
            if rating and review_count:
                log(f"✅ المنتج: {title}")
                log(f"⭐ التقييم: {rating}/5.0 ({review_count} تقييم)")
                log(f"📊 توزيع النجوم: {star_distribution}")
                
                return {
                    'title': title,
                    'rating': rating,
                    'review_count': review_count,
                    'star_distribution': star_distribution
                }
            else:
                log("⚠️ لم نتمكن من استخراج معلومات المنتج")
                return None
                
        except Exception as e:
            log(f"❌ خطأ في جلب معلومات المنتج: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """استخراج اسم المنتج"""
        title_elem = soup.find('span', {'id': 'productTitle'})
        if title_elem:
            return title_elem.get_text(strip=True)
        return None
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """استخراج التقييم (النجوم) بطرق متعددة"""
        patterns = [
            r'(\d+\.?\d*)\s*out of\s*5\s*stars',
            r'(\d+\.?\d*)\s*من\s*5',
            r'(\d+\.?\d*)\s*/\s*5',
        ]
        
        text_content = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                rating = float(match.group(1))
                if 0 <= rating <= 5:
                    log(f"✅ وجدنا التقييم: {rating}/5.0")
                    return rating
        
        selectors = [
            {'class': 'a-icon-alt'},
            {'id': 'acrPopover'},
            {'data-hook': 'rating-out-of-text'},
            {'class': 'a-size-base'},
            {'class': 'reviewCountTextLinkedHistogram'}
        ]
        
        for selector in selectors:
            rating_elem = soup.find('span', selector)
            if not rating_elem:
                rating_elem = soup.find('div', selector)
            
            if rating_elem:
                text = rating_elem.get_text(strip=True)
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        rating = float(match.group(1))
                        if 0 <= rating <= 5:
                            log(f"✅ وجدنا التقييم: {rating}/5.0")
                            return rating
        
        star_elements = soup.find_all(attrs={'aria-label': True})
        for elem in star_elements:
            aria_label = elem.get('aria-label', '')
            for pattern in patterns:
                match = re.search(pattern, aria_label, re.IGNORECASE)
                if match:
                    rating = float(match.group(1))
                    if 0 <= rating <= 5:
                        log(f"✅ وجدنا التقييم: {rating}/5.0")
                        return rating
        
        log("⚠️ لم نتمكن من استخراج التقييم")
        return None
    
    def _extract_review_count(self, soup: BeautifulSoup) -> Optional[int]:
        """استخراج عدد التقييمات"""
        selectors = [
            {'id': 'acrCustomerReviewText'},
            {'data-hook': 'total-review-count'}
        ]
        
        for selector in selectors:
            count_elem = soup.find('span', selector)
            if count_elem:
                text = count_elem.get_text(strip=True)
                text = text.replace(',', '')
                match = re.search(r'(\d+)', text)
                if match:
                    return int(match.group(1))
        
        return None
    
    def _extract_star_distribution(self, soup: BeautifulSoup) -> Dict[int, int]:
        """استخراج توزيع النجوم"""
        distribution = {}
        
        for star in [5, 4, 3, 2, 1]:
            pattern = re.compile(f'{star}\\s*star')
            star_row = soup.find('a', {'aria-label': pattern})
            
            if star_row:
                percent_text = star_row.get_text(strip=True)
                match = re.search(r'(\d+)%', percent_text)
                if match:
                    distribution[star] = int(match.group(1))
        
        return distribution
    
    def generate_realistic_reviews(
        self,
        product_info: Dict[str, Any],
        num_reviews: int = 8
    ) -> List[Review]:
        """
        يولد تقييمات واقعية بناءً على معلومات المنتج الحقيقية
        """
        if not product_info:
            return self._generate_default_reviews()
        
        rating = product_info.get('rating', 4.0)
        star_dist = product_info.get('star_distribution', {})
        
        log(f"🎯 توليد {num_reviews} تقييم واقعي بناءً على التقييم {rating}/5.0")
        
        if not star_dist:
            star_dist = self._estimate_distribution_from_rating(rating)
            log(f"📊 توزيع مقدر: {star_dist}")
        
        reviews = []
        star_counts = self._calculate_star_counts(star_dist, num_reviews)
        log(f"📈 عدد التقييمات لكل نجمة: {star_counts}")
        
        for star, count in star_counts.items():
            for _ in range(count):
                review = self._generate_review_for_rating(star)
                reviews.append(review)
        
        random.shuffle(reviews)
        return reviews[:num_reviews]
    
    def _estimate_distribution_from_rating(self, rating: float) -> Dict[int, int]:
        """تقدير توزيع النجوم بناءً على التقييم العام"""
        if rating >= 4.5:
            return {5: 70, 4: 20, 3: 5, 2: 3, 1: 2}
        elif rating >= 4.0:
            return {5: 50, 4: 30, 3: 10, 2: 5, 1: 5}
        elif rating >= 3.5:
            return {5: 35, 4: 30, 3: 20, 2: 10, 1: 5}
        elif rating >= 3.0:
            return {5: 20, 4: 25, 3: 30, 2: 15, 1: 10}
        elif rating >= 2.5:
            return {5: 10, 4: 15, 3: 20, 2: 30, 1: 25}
        else:
            return {5: 5, 4: 10, 3: 15, 2: 30, 1: 40}
    
    def _calculate_star_counts(
        self,
        star_dist: Dict[int, int],
        total: int
    ) -> Dict[int, int]:
        """حساب عدد التقييمات لكل نجمة"""
        if not star_dist:
            return {5: 3, 4: 2, 3: 1, 2: 1, 1: 1}
        
        counts = {}
        remaining = total
        
        for star in [5, 4, 3, 2, 1]:
            if star in star_dist:
                percent = star_dist[star]
                count = round((percent / 100) * total)
                counts[star] = min(count, remaining)
                remaining -= counts[star]
            else:
                counts[star] = 0
        
        if remaining > 0:
            max_star = max(star_dist.keys()) if star_dist else 5
            counts[max_star] = counts.get(max_star, 0) + remaining
        
        return counts
    
    def _generate_review_for_rating(self, rating: int) -> Review:
        """يولد تقييم واقعي بناءً على عدد النجوم"""
        names = ['أحمد', 'محمد', 'علي', 'حسن', 'خالد', 'منة', 'سارة', 'نور', 'ياسمين', 'مريم']
        
        days_ago = random.randint(1, 180)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        if rating == 5:
            templates = [
                {'title': 'ممتاز جداً', 'text': 'المنتج ده جامد أوي والجودة قوية خالص، أنصح بيه لكل واحد بيشتري من أمازون.'},
                {'title': 'خدمة تحفة', 'text': 'الخدمة ممتازة والتغليف جامد والشحن وصل قبل المعاد بصراحة تجربة حلوة.'},
                {'title': 'يستاهل الفلوس', 'text': 'المنتج أحسن من المتوقع، الجودة عالية والسعر مناسب جداً.'}
            ]
        elif rating == 4:
            templates = [
                {'title': 'كويس بس في ملاحظات', 'text': 'المنتج حلو والجودة كويسة بس الشحن اتأخر شوية والتغليف كان عادي.'},
                {'title': 'جيد بشكل عام', 'text': 'المنتج كويس وبيعمل المطلوب منه، بس كان ممكن يكون أحسن شوية.'}
            ]
        elif rating == 3:
            templates = [
                {'title': 'عادي', 'text': 'المنتج عادي يعني، مش حلو ومش وحش، كويس للاستخدام اليومي بس مش واو.'},
                {'title': 'متوسط', 'text': 'الجودة متوسطة والسعر مقبول، مفيش حاجة مميزة بس مفيش مشاكل كبيرة.'}
            ]
        elif rating == 2:
            templates = [
                {'title': 'سعره مبالغ فيه', 'text': 'الجودة معقولة بس السعر غالي جدًا بالنسبة للي بيقدمه، كنت متوقع أحسن من كده.'},
                {'title': 'مش راضي', 'text': 'المنتج مش زي ما كنت متوقع، في مشاكل في الجودة والشحن كان متأخر.'}
            ]
        else:
            templates = [
                {'title': 'أسوأ تجربة', 'text': 'مش حلو خالص والمنتج خايب، غالي أوي ومش يستاهل الفلوس خالص.'},
                {'title': 'مخيب للآمال', 'text': 'المنتج وصل مكسور والجودة سيئة جداً، مش هشتري من البراند ده تاني.'}
            ]
        
        template = random.choice(templates)
        
        return Review(
            author=random.choice(names),
            date=date,
            rating=float(rating),
            title=template['title'],
            text=template['text'],
            images=[],
            verified_purchase=random.choice([True, True, True, False])
        )
    
    def _generate_default_reviews(self) -> List[Review]:
        """توليد تقييمات افتراضية لو فشل جلب المعلومات"""
        log("⚠️ استخدام تقييمات افتراضية")
        return [
            self._generate_review_for_rating(5),
            self._generate_review_for_rating(5),
            self._generate_review_for_rating(4),
            self._generate_review_for_rating(4),
            self._generate_review_for_rating(3),
            self._generate_review_for_rating(2),
        ]
