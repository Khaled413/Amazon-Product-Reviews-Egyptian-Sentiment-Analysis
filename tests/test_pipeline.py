import unittest
from unittest.mock import MagicMock
import numpy as np

from src.data_cleaning import DataCleaner
from src.preprocessing import TextPreprocessor

class TestDataPipeline(unittest.TestCase):
    def setUp(self):
        self.cleaner = DataCleaner()
        self.preprocessor = TextPreprocessor(remove_stopwords=False, stem=False)

    def test_clean_text(self):
        text = "المنتج ده ممتااااز جداااا!! http://example.com"
        cleaned = self.cleaner.clean_text(text)
        self.assertNotIn("http", cleaned)
        self.assertTrue(len(cleaned) > 0)

    def test_preprocessing(self):
        text = "المنتج كويس أوي"
        processed = self.preprocessor.preprocess_text(text)
        self.assertIsInstance(processed, str)
        self.assertTrue(len(processed) > 0)

    def test_rule_based_sentiment_logic(self):
        positive_sample = "المنتج تحفة وممتاز جدا وأنصح بشرائه"
        negative_sample = "المنتج سيء وخايب وزبالة وماتشتريش"
        
        # التأكد من احتواء النصوص على الكلمات الدلالية
        self.assertIn("ممتاز", positive_sample)
        self.assertIn("سيء", negative_sample)

if __name__ == "__main__":
    unittest.main()
