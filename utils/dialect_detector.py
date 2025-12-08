"""
كاشف اللهجة المصرية
Egyptian Dialect Detector
"""

import re
from typing import List, Tuple

# كلمات ومصطلحات مميزة للهجة المصرية
EGYPTIAN_KEYWORDS = [
    # Common Egyptian words
    "جامد", "حلو", "حلوة", "قوي", "قوية", "أوي", "خالص",
    "يعني", "كده", "كدا", "عشان", "علشان", "مش", "مفيش",
    "إيه", "ايه", "ليه", "ازاي", "ازي", "امتى", "امتي",
    "فين", "مين", "دلوقتي", "دلوقت", "النهاردة", "النهارده",
    "امبارح", "بكرة", "بكرا", "كويس", "كويسة", "كويسين",
    "ينفع", "مينفعش", "مستريح", "مستريحة", "وحش", "وحشة",
    "خايب", "خايبين", "غالي", "غالية", "رخيص", "رخيصة",
    
    # Egyptian grammar patterns
    "اللي", "اللى", "الللي", "الللى",
    "ده", "دي", "دول",
    "احنا", "انتم", "انتوا",
    "انا", "انت", "انتي",
    
    # Common expressions
    "يعني", "مثلا", "زي", "كده", "كدا",
    "عشان", "علشان", "لأن", "لأنه", "لأنها", "لأنهم",
]

# Patterns that indicate Egyptian dialect
EGYPTIAN_PATTERNS = [
    r'\b(جامد|حلو|قوي|أوي|خالص)\b',
    r'\b(يعني|كده|كدا|عشان|علشان)\b',
    r'\b(مش|مفيش|مينفعش)\b',
    r'\b(إيه|ايه|ليه|ازاي|ازي|امتى|امتي|فين|مين)\b',
    r'\b(دلوقتي|دلوقت|النهاردة|النهارده|امبارح|بكرة|بكرا)\b',
    r'\b(كويس|كويسة|كويسين|ينفع|مستريح|مستريحة)\b',
    r'\b(اللي|اللى|الللي|الللى)\b',
    r'\b(ده|دي|دول)\b',
    r'\b(احنا|انتم|انتوا|انا|انت|انتي)\b',
]

def detect_egyptian_dialect(text: str, threshold: float = 0.3) -> Tuple[bool, float]:
    """
    كشف إذا كان النص باللهجة المصرية
    
    Args:
        text: النص المراد فحصه
        threshold: الحد الأدنى لنسبة الكلمات المصرية (افتراضي 0.3)
    
    Returns:
        Tuple[bool, float]: (هل النص مصري, نسبة الثقة)
    """
    if not text or len(text.strip()) == 0:
        return False, 0.0
    
    text_lower = text.lower()
    words = text_lower.split()
    
    if len(words) == 0:
        return False, 0.0
    
    # حساب عدد الكلمات المصرية
    egyptian_word_count = 0
    for word in words:
        if word in EGYPTIAN_KEYWORDS:
            egyptian_word_count += 1
    
    # حساب عدد الأنماط المصرية
    pattern_matches = 0
    for pattern in EGYPTIAN_PATTERNS:
        if re.search(pattern, text_lower):
            pattern_matches += 1
    
    # حساب نسبة الثقة
    word_ratio = egyptian_word_count / len(words) if len(words) > 0 else 0
    pattern_ratio = pattern_matches / len(EGYPTIAN_PATTERNS) if len(EGYPTIAN_PATTERNS) > 0 else 0
    
    # دمج النسبتين
    confidence = (word_ratio * 0.7 + pattern_ratio * 0.3)
    
    is_egyptian = confidence >= threshold
    
    return is_egyptian, confidence

def filter_egyptian_texts(texts: List[str], threshold: float = 0.3) -> List[str]:
    """
    فلترة قائمة النصوص لإرجاع النصوص المصرية فقط
    
    Args:
        texts: قائمة النصوص
        threshold: الحد الأدنى لنسبة الثقة
    
    Returns:
        List[str]: قائمة النصوص المصرية فقط
    """
    egyptian_texts = []
    for text in texts:
        is_egyptian, confidence = detect_egyptian_dialect(text, threshold)
        if is_egyptian:
            egyptian_texts.append(text)
    
    return egyptian_texts


