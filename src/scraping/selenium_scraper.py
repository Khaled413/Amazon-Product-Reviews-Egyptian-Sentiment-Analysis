"""
Selenium-based Amazon Product Reviews Scraper

This module provides a robust scraper using Selenium WebDriver to bypass
Amazon's anti-bot protection and fetch real product reviews.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException
)
try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    ChromeDriverManager = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SeleniumScraper')


@dataclass
class Review:
    """Review data model"""
    author: str
    date: str
    rating: float
    title: str
    text: str
    images: List[str]
    verified_purchase: bool
    helpful_count: int = 0


class SeleniumAmazonScraper:
    """
    Selenium-based scraper for Amazon reviews
    
    Uses Chrome WebDriver in headless mode to fetch real reviews
    from Amazon product pages, bypassing anti-bot protection.
    """
    
    def __init__(self, headless: bool = True, timeout: int = 15):
        """
        Initialize Selenium WebDriver
        
        Args:
            headless: Run browser in headless mode for better performance
            timeout: Maximum wait time for page elements (seconds)
        """
        self.driver = None
        self.headless = headless
        self.timeout = timeout
        self.max_retries = 3
        
        logger.info(f"Initializing SeleniumAmazonScraper (headless={headless}, timeout={timeout}s)")
    
    def initialize_driver(self) -> webdriver.Chrome:
        """
        Initialize Chrome WebDriver with optimized options
        
        Returns:
            Configured Chrome WebDriver instance
            
        Raises:
            WebDriverException: If driver initialization fails
        """
        try:
            logger.info("Setting up Chrome WebDriver...")
            
            options = Options()
            
            # Headless mode for performance
            if self.headless:
                options.add_argument('--headless')
                logger.debug("Headless mode enabled")
            
            # Essential Chrome options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # User agent to mimic real browser
            user_agent = (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
            options.add_argument(f'user-agent={user_agent}')
            
            # Disable automation flags
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Try to initialize service
            try:
                if ChromeDriverManager:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                else:
                    # Fallback: use system chromedriver
                    driver = webdriver.Chrome(options=options)
            except Exception as e:
                logger.warning(f"webdriver-manager failed: {e}, trying system chromedriver")
                # Fallback: use system chromedriver
                driver = webdriver.Chrome(options=options)
            
            # Set page load timeout
            driver.set_page_load_timeout(self.timeout)
            
            # Execute CDP commands to hide webdriver
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            logger.info("✅ Chrome WebDriver initialized successfully")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize WebDriver: {e}")
            raise WebDriverException(f"Driver initialization failed: {e}")
    
    def fetch_reviews(
        self,
        reviews_url: str,
        max_reviews: int = 20
    ) -> List[Review]:
        """
        Fetch reviews from Amazon using Selenium
        
        Args:
            reviews_url: URL of the reviews page
            max_reviews: Maximum number of reviews to fetch
            
        Returns:
            List of Review objects
            
        Raises:
            TimeoutException: If page load times out
            WebDriverException: If scraping fails
        """
        if not self.driver:
            self.driver = self.initialize_driver()
        
        try:
            logger.info(f"Navigating to: {reviews_url}")
            self.driver.get(reviews_url)
            
            # Wait for reviews to load
            logger.info("Waiting for reviews to load...")
            wait = WebDriverWait(self.driver, self.timeout)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-hook='review']"))
            )
            
            # Get page source and parse with BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract reviews
            reviews = self._extract_review_elements(soup, max_reviews)
            
            logger.info(f"✅ Extracted {len(reviews)} reviews")
            return reviews
            
        except TimeoutException:
            logger.error(f"❌ Timeout waiting for reviews to load")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching reviews: {e}")
            raise WebDriverException(f"Failed to fetch reviews: {e}")
    
    @staticmethod
    def validate_review(review: Review) -> bool:
        """
        Validate review data
        
        Args:
            review: Review object to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check text is not empty or whitespace-only
        if not review.text or not review.text.strip():
            logger.debug(f"Invalid review: empty text")
            return False
        
        # Check rating is between 1.0 and 5.0
        if not (1.0 <= review.rating <= 5.0):
            logger.debug(f"Invalid review: rating {review.rating} out of range")
            return False
        
        # Check author is not empty
        if not review.author or not review.author.strip():
            logger.debug(f"Invalid review: empty author")
            return False
        
        return True
    
    def _extract_review_elements(
        self,
        soup,
        max_reviews: int = 20
    ) -> List[Review]:
        """
        Extract review data from parsed HTML
        
        Args:
            soup: BeautifulSoup object of reviews page
            max_reviews: Maximum number of reviews to extract
            
        Returns:
            List of extracted Review objects
        """
        import re
        from datetime import datetime
        
        reviews = []
        invalid_count = 0
        review_divs = soup.find_all("div", {"data-hook": "review"})
        
        logger.info(f"Found {len(review_divs)} review elements")
        
        for review_div in review_divs[:max_reviews]:
            try:
                # Extract author
                author_elem = review_div.find("span", class_="a-profile-name")
                author = author_elem.get_text(strip=True) if author_elem else "مجهول"
                
                # Extract date
                date_elem = review_div.find("span", {"data-hook": "review-date"})
                date_str = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime("%Y-%m-%d")
                # Clean date (remove "Reviewed in ..." etc)
                date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', date_str)
                date = date_match.group(1) if date_match else date_str
                
                # Extract rating
                rating_elem = review_div.find("i", {"data-hook": "review-star-rating"})
                if not rating_elem:
                    rating_elem = review_div.find("i", class_=re.compile("a-star"))
                
                rating = 3.0  # default
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    rating_match = re.search(r"(\d+\.?\d*)", rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                
                # Extract title
                title_elem = review_div.find("a", {"data-hook": "review-title"})
                if not title_elem:
                    title_elem = review_div.find("span", {"data-hook": "review-title"})
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                # Extract text
                text_elem = review_div.find("span", {"data-hook": "review-body"})
                text = text_elem.get_text(strip=True) if text_elem else ""
                
                # Check verified purchase
                verified = bool(review_div.find("span", {"data-hook": "avp-badge"}))
                
                # Create review object
                review = Review(
                    author=author,
                    date=date,
                    rating=rating,
                    title=title,
                    text=text,
                    images=[],
                    verified_purchase=verified
                )
                
                # Validate review
                if self.validate_review(review):
                    reviews.append(review)
                    logger.debug(f"Extracted review: {author} - {rating} stars")
                else:
                    invalid_count += 1
                    logger.debug(f"Skipped invalid review")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error extracting review: {e}")
                continue
        
        if invalid_count > 0:
            logger.info(f"⚠️ Skipped {invalid_count} invalid reviews")
        
        # Check if all reviews failed validation
        if len(reviews) == 0 and len(review_divs) > 0:
            raise ValueError("All reviews failed validation")
        
        return reviews
    
    def close(self):
        """
        Close WebDriver and cleanup resources
        
        This method should always be called after scraping to free resources.
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ WebDriver closed successfully")
            except Exception as e:
                logger.warning(f"⚠️ Error closing WebDriver: {e}")
            finally:
                self.driver = None


def test_selenium_scraper():
    """Test Selenium scraper initialization"""
    scraper = SeleniumAmazonScraper(headless=True)
    try:
        driver = scraper.initialize_driver()
        logger.info("Test successful - driver initialized")
    finally:
        scraper.close()



class AmazonDomainHandler:
    """
    Handle different Amazon domains and build correct URLs
    """
    
    SUPPORTED_DOMAINS = {
        'amazon.com': 'https://www.amazon.com/product-reviews/{asin}',
        'amazon.eg': 'https://www.amazon.eg/-/en/product-reviews/{asin}',
        'amazon.co.uk': 'https://www.amazon.co.uk/product-reviews/{asin}',
    }
    
    @staticmethod
    def detect_domain(url: str) -> str:
        """
        Detect Amazon domain from URL
        
        Args:
            url: Product URL
            
        Returns:
            Domain name (e.g., 'amazon.com')
            
        Raises:
            ValueError: If domain is not supported
        """
        url_lower = url.lower()
        
        for domain in AmazonDomainHandler.SUPPORTED_DOMAINS.keys():
            if domain in url_lower:
                logger.debug(f"Detected domain: {domain}")
                return domain
        
        # Unsupported domain
        logger.error(f"Unsupported Amazon domain in URL: {url}")
        raise ValueError(
            f"Unsupported Amazon domain. Supported domains: "
            f"{', '.join(AmazonDomainHandler.SUPPORTED_DOMAINS.keys())}"
        )
    
    @staticmethod
    def get_reviews_url(product_url: str, asin: str) -> str:
        """
        Get reviews URL based on domain
        
        Args:
            product_url: Original product URL
            asin: Product ASIN
            
        Returns:
            Reviews page URL for the specific domain
            
        Raises:
            ValueError: If domain is not supported
        """
        domain = AmazonDomainHandler.detect_domain(product_url)
        url_template = AmazonDomainHandler.SUPPORTED_DOMAINS[domain]
        reviews_url = url_template.format(asin=asin)
        
        logger.info(f"Reviews URL: {reviews_url}")
        return reviews_url


if __name__ == "__main__":
    # Test domain handler
    test_urls = [
        "https://www.amazon.com/dp/B08N5WRWNW",
        "https://www.amazon.eg/-/en/Samsung-Android-Smartphone-Storage-Upgrades/dp/B0FND1GG2X",
        "https://www.amazon.co.uk/dp/B08N5WRWNW",
    ]
    
    for url in test_urls:
        try:
            domain = AmazonDomainHandler.detect_domain(url)
            asin = "B08N5WRWNW"
            reviews_url = AmazonDomainHandler.get_reviews_url(url, asin)
            print(f"✅ {domain}: {reviews_url}")
        except ValueError as e:
            print(f"❌ Error: {e}")



class RetryHandler:
    """
    Handle retries with exponential backoff
    """
    
    @staticmethod
    def retry_with_backoff(
        func,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        *args,
        **kwargs
    ):
        """
        Retry function with exponential backoff
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Multiplier for delay on each retry
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Function result if successful
            
        Raises:
            Exception: If all retries fail
        """
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries}")
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"✅ Success after {attempt + 1} attempts")
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    delay *= backoff_factor
        
        # All retries failed
        logger.error(f"❌ All {max_retries} attempts failed")
        raise last_exception
