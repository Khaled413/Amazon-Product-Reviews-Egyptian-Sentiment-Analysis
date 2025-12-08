"""
Product-level NLP pipeline for Amazon reviews (Egyptian Arabic focus).

⚠ هذا الملف حالياً يستخدم قواعد بسيطة Heuristics لتقريب السلوك المطلوب:
- 5-level sentiment مبني جزئياً على النجوم + كلمات مفتاحية.
- Sarcasm / Fake / Aspects / NER / Summary كلها قواعد مبدئية.

يمكن لاحقاً استبدال هذه القواعد بنماذج Transformer (MarBERT / EgyptianBERT).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


SENTIMENT_5_LABELS = [
    "very_negative",
    "negative",
    "neutral",
    "positive",
    "very_positive",
]


@dataclass
class AnalyzedReview:
    author: str
    date: str
    rating: float
    title: str
    text: str
    sentiment_5: str
    sentiment_score: float
    sarcasm: str
    fake: str
    aspects: Dict[str, str]
    entities: List[Dict[str, Any]]
    summary: str


class ProductReviewAnalyzer:
    """
    Pipeline مبسط لتحليل ريفيوهات منتج واحد.

    يعتمد على:
    - rating + كلمات مفتاحية لتحديد المشاعر.
    - قواعد بسيطة لـ sarcasm / fake / aspects / entities / summary.
    """

    POSITIVE_WORDS = ["جامد", "حلو", "حلوة", "ممتاز", "كويس", "قوي", "خدمة ممتازة", "تحفة"]
    NEGATIVE_WORDS = ["وحش", "سيء", "خايب", "مش حلو", "مش كويس", "غالي", "غالي أوي", "مستاهلش"]

    SARCASM_PATTERNS = ["يا سلام", "بجد", "آه طبعاً", "واو قوي", "ياسلام"]

    ASPECT_KEYWORDS = {
        "price": ["سعر", "غالي", "رخيص", "فلوس"],
        "quality": ["جودة", "خامة", "كويس", "وحش", "جامد"],
        "shipping": ["شحن", "وصل", "توصيل", "اتأخر"],
        "packaging": ["تغليف", "علبة", "باكدج"],
        "service": ["خدمة", "دعم", "البيع", "البائع"],
        "performance": ["أداء", "سرعة", "بطئ", "سريع"],
    }

    def analyze_product_reviews(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Args:
            product: dict يحتوي على:
                {
                    "product": {...},
                    "reviews": [ {author, date, rating, title, text, ...}, ...]
                }
        Returns:
            dict يحتوي على:
                - product
                - reviews (بعد التحليل)
                - dashboard (إحصائيات جاهزة للـ UI)
        """
        reviews_raw: List[Dict[str, Any]] = product.get("reviews", [])
        analyzed_reviews: List[AnalyzedReview] = []

        for r in reviews_raw:
            analyzed = self._analyze_single_review(r)
            analyzed_reviews.append(analyzed)

        dashboard = self._build_dashboard_data(analyzed_reviews)
        
        # إضافة التقييم الحقيقي من أمازون لو موجود
        product_info = product.get("product", {})
        if product_info.get("real_rating"):
            dashboard["real_rating"] = product_info["real_rating"]

        return {
            "product": product_info,
            "scraped_at": product.get("scraped_at"),
            "reviews": [asdict(r) for r in analyzed_reviews],
            "dashboard": dashboard,
        }

    def _build_dashboard_data(self, analyzed_reviews: List[AnalyzedReview]) -> Dict[str, Any]:
        """
        بناء إحصائيات جاهزة للـ Dashboard في الواجهة.
        """
        total = len(analyzed_reviews)
        if total == 0:
            return {
                "total_reviews": 0,
                "sentiment_distribution": {},
                "rating_distribution": {},
                "aspect_sentiment": {},
                "fake_ratio": 0.0,
                "sarcasm_ratio": 0.0,
                "top_positive_phrases": [],
                "top_negative_phrases": [],
            }

        # توزيع المشاعر 5-level
        sentiment_counts = Counter(r.sentiment_5 for r in analyzed_reviews)

        # توزيع التقييمات
        rating_counts = Counter(int(round(r.rating)) for r in analyzed_reviews)

        # نسبة Fake / Sarcasm
        fake_count = sum(1 for r in analyzed_reviews if r.fake == "fake")
        sarcasm_count = sum(1 for r in analyzed_reviews if r.sarcasm == "sarcastic")

        # Aspect sentiments
        aspect_sentiment_counts: Dict[str, Counter] = defaultdict(Counter)
        for r in analyzed_reviews:
            for aspect, label in r.aspects.items():
                if label != "not_mentioned":
                    aspect_sentiment_counts[aspect][label] += 1

        # Pros / Cons من الكيانات
        pros = Counter()
        cons = Counter()
        for r in analyzed_reviews:
            for ent in r.entities:
                if ent.get("type") == "ADVANTAGE":
                    pros[ent["text"]] += 1
                elif ent.get("type") == "PROBLEM":
                    cons[ent["text"]] += 1

        dashboard = {
            "total_reviews": total,
            "sentiment_distribution": dict(sentiment_counts),
            "rating_distribution": dict(rating_counts),
            "aspect_sentiment": {
                aspect: dict(counts) for aspect, counts in aspect_sentiment_counts.items()
            },
            "fake_ratio": fake_count / total,
            "sarcasm_ratio": sarcasm_count / total,
            "top_positive_phrases": [w for w, _ in pros.most_common(10)],
            "top_negative_phrases": [w for w, _ in cons.most_common(10)],
        }

        return dashboard

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _analyze_single_review(self, review: Dict[str, Any]) -> AnalyzedReview:
        text = (review.get("text") or "").strip()
        rating = float(review.get("rating") or 0)
        author = review.get("author") or "Unknown"
        date = review.get("date") or ""
        title = review.get("title") or ""
        verified = bool(review.get("verified_purchase", False))

        sentiment_5, sentiment_score = self._infer_sentiment_5(text, rating)
        sarcasm = self._infer_sarcasm(text, sentiment_5)
        fake = self._infer_fake(review, sentiment_5, verified)
        aspects = self._infer_aspects(text, sentiment_5)
        entities = self._infer_entities(text)
        summary = self._summarize_review(text, sentiment_5)

        analyzed = AnalyzedReview(
            author=author,
            date=date,
            rating=rating,
            title=title,
            text=text,
            sentiment_5=sentiment_5,
            sentiment_score=sentiment_score,
            sarcasm=sarcasm,
            fake=fake,
            aspects=aspects,
            entities=entities,
            summary=summary,
        )
        return analyzed

    def _infer_sentiment_5(self, text: str, rating: float) -> (str, float):
        """
        تقدير 5-level sentiment من:
        - عدد النجوم
        - كلمات إيجابية/سلبية في النص
        """
        txt = text.lower()
        pos_hits = sum(1 for w in self.POSITIVE_WORDS if w in txt)
        neg_hits = sum(1 for w in self.NEGATIVE_WORDS if w in txt)

        base = 2  # neutral index
        if rating >= 4.5:
            base = 4
        elif rating >= 3.5:
            base = 3
        elif rating <= 1.5:
            base = 0
        elif rating <= 2.5:
            base = 1

        score = base
        score += 0.5 if pos_hits > neg_hits else 0
        score -= 0.5 if neg_hits > pos_hits else 0

        score = max(0, min(4, score))
        label = SENTIMENT_5_LABELS[int(round(score))]
        # normalize to [0,1]
        confidence = (score + 1) / 5
        return label, confidence

    def _infer_sarcasm(self, text: str, sentiment_5: str) -> str:
        txt = text.lower()
        if any(pat.lower() in txt for pat in self.SARCASM_PATTERNS):
            return "sarcastic"
        # مثال بسيط: كلام إيجابي واضح مع كلمات سلبية
        if "يا سلام" in txt and ("وحش" in txt or "خايب" in txt):
            return "sarcastic"
        return "not_sarcastic"

    def _infer_fake(self, review: Dict[str, Any], sentiment_5: str, verified: bool) -> str:
        rating = float(review.get("rating") or 0)
        text = (review.get("text") or "").strip()
        txt = text.lower()

        suspicious = 0
        if not verified and rating in (1.0, 5.0):
            suspicious += 1
        if len(text) < 20:
            suspicious += 1
        if txt.count("ممتاز") > 2 or txt.count("وحش") > 2:
            suspicious += 1

        return "fake" if suspicious >= 2 else "real"

    def _infer_aspects(self, text: str, sentiment_5: str) -> Dict[str, str]:
        """
        Aspect-based sentiment مبسط:
        - لو الـ aspect ظهر في النص → ياخد نفس sentiment_5.
        - وإلا يكون 'not_mentioned'.
        """
        txt = text.lower()
        aspects: Dict[str, str] = {}
        for aspect, keywords in self.ASPECT_KEYWORDS.items():
            if any(k.lower() in txt for k in keywords):
                aspects[aspect] = sentiment_5
            else:
                aspects[aspect] = "not_mentioned"
        return aspects

    def _infer_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        NER مبسط:
        - يلتقط price patterns وبعض الكلمات الإيجابية/السلبية كـ PROBLEM/ADVANTAGE.
        """
        entities: List[Dict[str, Any]] = []
        txt = text

        # Price entities (أرقام + عملة تقريبية)
        import re

        for m in re.finditer(r"(\d{2,6})\s*(جنيه|ريال|دولار)?", txt):
            entities.append(
                {
                    "text": m.group(0),
                    "type": "PRICE",
                    "start": m.start(),
                    "end": m.end(),
                }
            )

        # Problems / advantages from keywords
        for w in self.NEGATIVE_WORDS:
            if w in txt:
                idx = txt.find(w)
                entities.append(
                    {
                        "text": w,
                        "type": "PROBLEM",
                        "start": idx,
                        "end": idx + len(w),
                    }
                )

        for w in self.POSITIVE_WORDS:
            if w in txt:
                idx = txt.find(w)
                entities.append(
                    {
                        "text": w,
                        "type": "ADVANTAGE",
                        "start": idx,
                        "end": idx + len(w),
                    }
                )

        return entities

    def _summarize_review(self, text: str, sentiment_5: str) -> str:
        """
        تلخيص مبسط:
        - لو النص قصير → يرجعه كما هو.
        - لو طويل → يرجع أول جملة + توضيح sentiment.
        """
        txt = text.strip()
        if len(txt) <= 80:
            return txt

        # split by punctuation
        import re

        sentences = re.split(r"[.!؟\n]", txt)
        first = next((s.strip() for s in sentences if s.strip()), txt[:80])

        sentiment_map_arb = {
            "very_positive": "إيجابي جدًا",
            "positive": "إيجابي",
            "neutral": "محايد",
            "negative": "سلبي",
            "very_negative": "سلبي جدًا",
        }
        sent_arb = sentiment_map_arb.get(sentiment_5, "محايد")

        return f"{first} (بشكل عام التقييم {sent_arb})."


def build_dashboard(analyzed_reviews: List[AnalyzedReview]) -> Dict[str, Any]:
    """
    Helper سريع في حالة أردت استخدامه مباشرة.
    """
    analyzer = ProductReviewAnalyzer()
    return analyzer._build_dashboard_data(analyzed_reviews)  # type: ignore[attr-defined]


