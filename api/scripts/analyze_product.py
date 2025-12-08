"""
تحليل منتج كامل من أمازون:
- يستقبل رابط منتج
- يجمع الريفيوهات (placeholder / dummy scraper حالياً)
- يشغّل Pipeline مبدئي لتحليل المشاعر، السخرية، الـ fake، الـ aspects، والـ entities
- يرجّع JSON مطبوع على stdout (يُستخدم بواسطة TypeScript API)
"""

from __future__ import annotations

import json
import os
import sys
import io

# Fix Windows console encoding for Arabic text
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# project root: ../../ from this file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.scraping.amazon_scraper import AmazonProductScraper  # type: ignore
from src.nlp.product_pipeline import ProductReviewAnalyzer  # type: ignore


def main() -> None:
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "error": "Missing arguments",
                    "message": "Usage: python analyze_product.py <product_url>",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    product_url = sys.argv[1]

    try:
        scraper = AmazonProductScraper()
        scraped = scraper.fetch_product_reviews(product_url)

        analyzer = ProductReviewAnalyzer()
        result = analyzer.analyze_product_reviews(scraped)

        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(
            json.dumps(
                {
                    "error": str(e),
                    "message": "Failed to analyze product reviews",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()


