# -*- coding: utf-8 -*-
"""
Product Info Scraper
يجيب معلومات المنتج من أمازون: السعر، المواصفات، الصور، التقييم
"""

from __future__ import annotations

import json
import re
import sys
import io
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional, List

import requests
from bs4 import BeautifulSoup

# Fix Windows console encoding for Arabic text
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def log(msg: str) -> None:
    """Print debug messages to stderr to keep stdout clean for JSON output."""
    print(msg, file=sys.stderr)


@dataclass
class PriceData:
    current: Optional[float]
    original: Optional[float]
    currency: str
    discount_percent: Optional[int]
    price_string: str


@dataclass
class RatingData:
    score: Optional[float]
    count: Optional[int]


@dataclass
class ProductInfo:
    url: str
    asin: Optional[str]
    title: str
    price: PriceData
    rating: RatingData
    specs: Dict[str, str]
    images: List[str]
    availability: str
    fetched_at: str


class ProductInfoScraper:
    """
    Scraper لجلب معلومات المنتج من أمازون
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def scrape_product_info(self, url: str) -> ProductInfo:
        """
        جلب معلومات المنتج الكاملة من أمازون
        """
        log(f"🔄 جاري جلب معلومات المنتج...")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                log(f"⚠️ Status code: {response.status_code}")
                return self._create_error_response(url, "فشل الاتصال بأمازون")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # استخراج ASIN
            asin = self._extract_asin(url)
            
            # استخراج العنوان
            title = self._extract_title(soup) or "منتج أمازون"
            
            # استخراج السعر
            price = self._extract_price(soup)
            
            # استخراج التقييم
            rating = self._extract_rating(soup)
            
            # استخراج المواصفات
            specs = self._extract_specs(soup)
            
            # استخراج الصور
            images = self._extract_images(soup)
            
            # استخراج التوفر
            availability = self._extract_availability(soup)
            
            log(f"✅ تم جلب معلومات المنتج: {title[:50]}...")
            
            return ProductInfo(
                url=url,
                asin=asin,
                title=title,
                price=price,
                rating=rating,
                specs=specs,
                images=images,
                availability=availability,
                fetched_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            log(f"❌ خطأ: {e}")
            return self._create_error_response(url, str(e))

    def _extract_asin(self, url: str) -> Optional[str]:
        """استخراج ASIN من الرابط"""
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'/([A-Z0-9]{10})(?:[/?]|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                asin = match.group(1)
                if len(asin) == 10 and asin.isalnum():
                    return asin
        return None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """استخراج عنوان المنتج"""
        selectors = [
            ('span', {'id': 'productTitle'}),
            ('h1', {'id': 'title'}),
        ]
        
        for tag, attrs in selectors:
            elem = soup.find(tag, attrs)
            if elem:
                title = elem.get_text(strip=True)
                if title and len(title) > 3:
                    return title
        
        # Try meta tags
        meta = soup.find('meta', {'name': 'title'})
        if meta and meta.get('content'):
            title = meta.get('content').strip()
            title = re.sub(r'^Amazon\.(com|eg|co\.uk):\s*', '', title)
            if title:
                return title
        
        return None

    def _extract_price(self, soup: BeautifulSoup) -> PriceData:
        """استخراج بيانات السعر"""
        current_price = None
        original_price = None
        currency = "EGP"
        price_string = "السعر غير متوفر"
        
        # Try multiple price selectors - more comprehensive
        price_selectors = [
            ('span', {'class': 'a-price-whole'}),
            ('span', {'id': 'priceblock_ourprice'}),
            ('span', {'id': 'priceblock_dealprice'}),
            ('span', {'id': 'priceblock_saleprice'}),
            ('span', {'class': 'a-offscreen'}),
            ('span', {'class': 'priceToPay'}),
            ('span', {'data-a-color': 'price'}),
        ]
        
        # Also try to find price in the page text using regex
        page_text = soup.get_text()
        price_patterns = [
            r'EGP\s*([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)\s*EGP',
            r'([\d,]+\.?\d*)\s*جنيه',
            r'\$\s*([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)\s*\$',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, page_text)
            if match:
                try:
                    price_val = float(match.group(1).replace(',', ''))
                    if price_val > 10:  # Reasonable price
                        current_price = price_val
                        price_string = match.group(0)
                        break
                except ValueError:
                    continue
        
        # If still no price, try selectors
        if not current_price:
            for tag, attrs in price_selectors:
                elem = soup.find(tag, attrs)
                if elem:
                    price_text = elem.get_text(strip=True)
                    numbers = re.findall(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if numbers:
                        try:
                            current_price = float(numbers[0].replace(',', ''))
                            price_string = price_text
                            break
                        except ValueError:
                            continue
        
        # Try to find original price (for discounts)
        original_selectors = [
            ('span', {'class': 'a-price a-text-price'}),
            ('span', {'data-a-strike': 'true'}),
        ]
        
        for tag, attrs in original_selectors:
            elem = soup.find(tag, attrs)
            if elem:
                price_text = elem.get_text(strip=True)
                numbers = re.findall(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if numbers:
                    try:
                        original_price = float(numbers[0])
                        break
                    except ValueError:
                        continue
        
        # Detect currency
        page_text = soup.get_text()
        if 'EGP' in page_text or 'جنيه' in page_text:
            currency = 'EGP'
        elif '$' in page_text or 'USD' in page_text:
            currency = 'USD'
        elif 'SAR' in page_text or 'ريال' in page_text:
            currency = 'SAR'
        elif '£' in page_text or 'GBP' in page_text:
            currency = 'GBP'
        
        # Calculate discount
        discount_percent = None
        if current_price and original_price and original_price > current_price:
            discount_percent = round(((original_price - current_price) / original_price) * 100)
        
        return PriceData(
            current=current_price,
            original=original_price,
            currency=currency,
            discount_percent=discount_percent,
            price_string=price_string
        )

    def _extract_rating(self, soup: BeautifulSoup) -> RatingData:
        """استخراج التقييم"""
        score = None
        count = None
        
        # Extract rating score
        patterns = [
            r'(\d+\.?\d*)\s*out of\s*5',
            r'(\d+\.?\d*)\s*من\s*5',
        ]
        
        text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    if 0 <= score <= 5:
                        break
                except ValueError:
                    continue
        
        # Extract review count
        count_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
        if count_elem:
            count_text = count_elem.get_text(strip=True).replace(',', '')
            numbers = re.findall(r'\d+', count_text)
            if numbers:
                count = int(numbers[0])
        
        return RatingData(score=score, count=count)

    def _extract_specs(self, soup: BeautifulSoup) -> Dict[str, str]:
        """استخراج المواصفات التقنية"""
        specs = {}
        
        # Try product details table
        detail_tables = soup.find_all('table', {'id': 'productDetails_techSpec_section_1'})
        detail_tables += soup.find_all('table', {'class': 'a-keyvalue'})
        
        for table in detail_tables:
            rows = table.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    key = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    if key and value:
                        specs[key] = value
        
        # Try feature bullets
        feature_div = soup.find('div', {'id': 'feature-bullets'})
        if feature_div:
            bullets = feature_div.find_all('li')
            for i, bullet in enumerate(bullets[:5]):
                text = bullet.get_text(strip=True)
                if text and len(text) > 5:
                    specs[f'ميزة {i+1}'] = text[:200]
        
        return specs

    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """استخراج صور المنتج"""
        images = []
        
        # Try main image
        main_img = soup.find('img', {'id': 'landingImage'})
        if main_img and main_img.get('src'):
            images.append(main_img['src'])
        
        # Try data-old-hires attribute
        if main_img and main_img.get('data-old-hires'):
            images.append(main_img['data-old-hires'])
        
        # Try thumbnail images
        thumb_container = soup.find('div', {'id': 'altImages'})
        if thumb_container:
            thumbs = thumb_container.find_all('img')
            for thumb in thumbs[:5]:
                src = thumb.get('src') or thumb.get('data-old-hires')
                if src and 'sprite' not in src.lower():
                    # Convert thumbnail to full size
                    full_src = re.sub(r'\._[A-Z]+\d+_\.', '.', src)
                    if full_src not in images:
                        images.append(full_src)
        
        return images[:5]  # Limit to 5 images

    def _extract_availability(self, soup: BeautifulSoup) -> str:
        """استخراج حالة التوفر"""
        avail_elem = soup.find('div', {'id': 'availability'})
        if avail_elem:
            text = avail_elem.get_text(strip=True)
            if 'in stock' in text.lower() or 'متوفر' in text:
                return 'متوفر'
            elif 'out of stock' in text.lower() or 'غير متوفر' in text:
                return 'غير متوفر'
            return text[:50]
        return 'غير معروف'

    def _create_error_response(self, url: str, error: str) -> ProductInfo:
        """إنشاء response في حالة الخطأ"""
        return ProductInfo(
            url=url,
            asin=self._extract_asin(url),
            title="فشل جلب المعلومات",
            price=PriceData(None, None, "EGP", None, "غير متوفر"),
            rating=RatingData(None, None),
            specs={},
            images=[],
            availability="غير معروف",
            fetched_at=datetime.now().isoformat()
        )


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Missing URL",
            "message": "Usage: python product_info_scraper.py <product_url>"
        }, ensure_ascii=False))
        sys.exit(1)
    
    url = sys.argv[1]
    scraper = ProductInfoScraper()
    info = scraper.scrape_product_info(url)
    
    # Convert to dict for JSON
    result = asdict(info)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
