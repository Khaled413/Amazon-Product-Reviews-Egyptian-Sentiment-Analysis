"""
إعدادات المشروع
Project Configuration
"""

# مسارات المجلدات
DATA_DIR = "data"
RAW_DATA_DIR = "data/raw"
CLEANED_DATA_DIR = "data/cleaned"
ANNOTATED_DATA_DIR = "data/annotated"
PROCESSED_DATA_DIR = "data/processed"
MODELS_DIR = "models"
REPORTS_DIR = "reports"

# إعدادات جمع البيانات
COLLECTION_SOURCES = [
    "jumia",
    "noon",
    "olx",
    "facebook",
    "youtube",
    "twitter"
]

# إعدادات التنظيف
CLEANING_CONFIG = {
    'remove_emojis': True,
    'remove_urls': True,
    'remove_mentions': True,
    'remove_hashtags': True,
    'remove_elongated': True,
    'remove_numbers': True,
    'normalize_arabic': True,
    'remove_special_chars': True
}

# إعدادات فلترة اللهجة
DIALECT_FILTER_THRESHOLD = 0.3

# إعدادات المعالجة
PREPROCESSING_CONFIG = {
    'remove_stopwords': True,
    'stem': False
}

# إعدادات استخراج الخصائص
FEATURE_EXTRACTION_CONFIG = {
    'method': 'tfidf',  # 'tfidf', 'bow', 'bert', 'marbert', 'arabert'
    'max_features': 5000,
    'ngram_range': (1, 2),
    'min_df': 2,
    'max_df': 0.95
}

# إعدادات التدريب
TRAINING_CONFIG = {
    'test_size': 0.15,
    'val_size': 0.15,
    'random_state': 42,
    'models': ['lr', 'svm', 'rf'],  # 'lr', 'svm', 'rf', 'lstm'
    'lstm_config': {
        'epochs': 50,
        'batch_size': 32,
        'learning_rate': 0.001,
        'hidden_size': 128,
        'num_layers': 2,
        'dropout': 0.3
    }
}

# إعدادات التقييم
EVALUATION_METRICS = [
    'accuracy',
    'precision',
    'recall',
    'f1_score'
]

# تصنيفات المشاعر
SENTIMENT_LABELS = {
    'positive': 1,
    'negative': -1,
    'neutral': 0
}

SENTIMENT_NAMES = {
    1: 'positive',
    -1: 'negative',
    0: 'neutral'
}


