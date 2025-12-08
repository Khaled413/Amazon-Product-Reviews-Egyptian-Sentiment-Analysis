import { exec, spawn, ChildProcess } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const execAsync = promisify(exec);

interface SentimentResult {
  text: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  label: number;
  processed_text?: string;
}

// قائمة الكلمات الإيجابية والسلبية المصرية
const POSITIVE_WORDS = [
  'جامد', 'ممتاز', 'حلو', 'كويس', 'رائع', 'جميل', 'تحفة', 'عظيم', 'هايل',
  'مبسوط', 'سعيد', 'فرحان', 'راضي', 'مرتاح', 'أحسن', 'أفضل', 'روعة',
  'خرافي', 'مذهل', 'بجد', 'فعلا', 'صح', 'تمام', 'زي الفل', 'نضيف',
  'شيك', 'فخم', 'قوي', 'متين', 'سريع', 'ممتازة', 'جودة', 'أصلي',
  'يستاهل', 'انصح', 'أنصح', 'recommend', 'good', 'great', 'excellent', 'amazing',
  'perfect', 'love', 'best', 'awesome', 'fantastic', 'wonderful', 'nice'
];

const NEGATIVE_WORDS = [
  'وحش', 'سيء', 'سيئ', 'خايب', 'زفت', 'بايظ', 'مش كويس', 'ضعيف', 'رديء',
  'زبالة', 'فاشل', 'مضروب', 'غالي', 'مغشوش', 'تقليد', 'fake', 'مزيف',
  'متأخر', 'بطيء', 'مكسور', 'خربان', 'معطل', 'ندمان', 'زعلان', 'مش راضي',
  'أسوأ', 'أوحش', 'مش هشتري', 'مش هاخد', 'ضيعت فلوسي', 'نصب', 'احتيال',
  'مقطوع', 'ناقص', 'مفيش', 'لا يوجد', 'لايوجد', 'مش موجود', 'ارجو', 'أرجو',
  'للأسف', 'لسوء', 'مشكلة', 'عيب', 'عيوب',
  // كلمات تحذير من الشراء
  'متشتريش', 'ماتشتريش', 'متشتروش', 'ماتشتروش', 'متجيبش', 'ماتجيبش',
  'مش هنصح', 'ما انصحش', 'ماانصحش', 'لا انصح', 'لاانصح',
  'متاخدش', 'ماتاخدش', 'متاخدوش', 'ماتاخدوش',
  // كلمات سلبية قوية
  'سيء جدا', 'سيئ جدا', 'وحش جدا', 'خايب جدا', 'زفت جدا',
  'اوحش', 'أوحش حاجة', 'اسوأ', 'أسوأ حاجة',
  'مش دقيق', 'مش دقيقة', 'معدتش', 'مبقتش',
  'bad', 'worst', 'terrible', 'horrible', 'awful', 'poor', 'waste', 'disappointed',
  'broken', 'fake', 'scam', 'never', 'dont', "don't", 'hate', 'useless', 'missing'
];

// كلمات الاستدراك - لو جت بعد كلمة إيجابية يبقى فيه مشكلة
const CONTRAST_WORDS = ['بس', 'لكن', 'إلا', 'غير', 'but', 'however', 'except', 'although'];

// كلمات تدل على تقييم منتج
const REVIEW_INDICATORS = [
  // كلمات عربية
  'منتج', 'المنتج', 'سلعة', 'جهاز', 'الجهاز', 'موبايل', 'تليفون', 'لابتوب',
  'شاشة', 'سماعة', 'ساعة', 'كاميرا', 'شاحن', 'كابل', 'جراب', 'كفر',
  'اشتريت', 'شريت', 'جبت', 'طلبت', 'وصل', 'وصلني', 'استلمت', 'جالي',
  'الشحن', 'التوصيل', 'التغليف', 'العلبة', 'الكرتونة', 'البوكس',
  'الجودة', 'الخامة', 'المواد', 'الصنع', 'التصنيع', 'أصلي', 'تقليد',
  'السعر', 'الفلوس', 'غالي', 'رخيص', 'يستاهل', 'مش يستاهل',
  'الضمان', 'الصيانة', 'خدمة العملاء', 'الدعم',
  'استخدمته', 'جربته', 'شغال', 'بيشتغل', 'مش شغال',
  'أنصح', 'انصح', 'مش هنصح', 'recommend', 'هشتري', 'مش هشتري',
  // كلمات تحذير/نصيحة شراء - دي بتدل على تقييم
  'متشتريش', 'ماتشتريش', 'اشتري', 'اشتروا', 'متشتروش',
  // كلمات إنجليزية
  'product', 'item', 'device', 'phone', 'laptop', 'screen', 'quality',
  'shipping', 'delivery', 'package', 'price', 'worth', 'buy', 'bought',
  'ordered', 'received', 'arrived', 'works', 'working', 'broken',
  'recommend', 'purchase', 'seller', 'amazon', 'review', 'rating',
  'stars', 'star', '⭐', '👍', '👎'
];

/**
 * التحقق من أن النص يشبه تقييم منتج
 */
interface ValidationResult {
  isValid: boolean;
  reason?: string;
}

// كلمات عامة مش بتدل على تقييم منتج
const NON_REVIEW_CONTEXTS = [
  'الجو', 'الطقس', 'النهارده', 'اليوم', 'الصبح', 'بالليل',
  'الاكل', 'الأكل', 'المطعم', 'الفيلم', 'المسلسل', 'الماتش',
  'weather', 'today', 'movie', 'food', 'restaurant'
];

function isValidReview(text: string): ValidationResult {
  const trimmedText = text.trim();
  
  // التحقق من الطول - الحد الأدنى 3 حروف بس
  if (trimmedText.length < 3) {
    return { isValid: false, reason: '✍️ النص قصير أوي! اكتب تقييم أطول شوية عشان أقدر أحلله' };
  }
  
  if (trimmedText.length > 5000) {
    return { isValid: false, reason: '📝 النص طويل أوي! حاول تختصر شوية' };
  }
  
  const textLower = trimmedText.toLowerCase();
  
  // التحقق من السياقات اللي مش تقييم منتج
  let hasNonReviewContext = false;
  for (const context of NON_REVIEW_CONTEXTS) {
    if (textLower.includes(context.toLowerCase()) || trimmedText.includes(context)) {
      hasNonReviewContext = true;
      break;
    }
  }
  
  // التحقق من وجود كلمات تدل على تقييم منتج
  let hasReviewIndicator = false;
  for (const indicator of REVIEW_INDICATORS) {
    if (textLower.includes(indicator.toLowerCase()) || trimmedText.includes(indicator)) {
      hasReviewIndicator = true;
      break;
    }
  }
  
  // التحقق من وجود كلمات مشاعر
  let hasSentimentWord = false;
  for (const word of [...POSITIVE_WORDS, ...NEGATIVE_WORDS]) {
    if (textLower.includes(word.toLowerCase()) || trimmedText.includes(word)) {
      hasSentimentWord = true;
      break;
    }
  }
  
  // لو فيه سياق مش تقييم (زي الجو) ومفيش مؤشر تقييم = رفض
  if (hasNonReviewContext && !hasReviewIndicator) {
    return { 
      isValid: false, 
      reason: '🤔 ده مش شبه تقييم منتج! جرب تكتب رأيك في منتج اشتريته من أمازون أو أي متجر' 
    };
  }
  
  // لو فيه مؤشر تقييم = صالح
  if (hasReviewIndicator) {
    return { isValid: true };
  }
  
  // لو فيه كلمة مشاعر والنص طويل شوية (أكتر من 15 حرف) = صالح
  if (hasSentimentWord && trimmedText.length > 15) {
    return { isValid: true };
  }
  
  // لو فيه كلمة مشاعر بس النص قصير = نطلب توضيح
  if (hasSentimentWord) {
    return { 
      isValid: false, 
      reason: '💭 وضح أكتر! إيه المنتج اللي بتتكلم عنه؟ اكتب تقييم أطول شوية' 
    };
  }
  
  // لو مفيش أي مؤشر على تقييم ومفيش كلمات مشاعر
  return { 
    isValid: false, 
    reason: '🤔 مش قادر أفهم ده تقييم لإيه! جرب تكتب رأيك في منتج اشتريته أو تجربة شراء عدت بيها' 
  };
}

/**
 * تحليل سريع باستخدام الكلمات المفتاحية - دقيق وسريع
 */
function quickAnalyze(text: string): SentimentResult & { warning?: string } {
  const textLower = text.toLowerCase();
  const textArabic = text;
  
  let positiveScore = 0;
  let negativeScore = 0;
  
  // حساب النقاط الإيجابية
  for (const word of POSITIVE_WORDS) {
    if (textLower.includes(word) || textArabic.includes(word)) {
      positiveScore += 1;
    }
  }
  
  // حساب النقاط السلبية
  for (const word of NEGATIVE_WORDS) {
    if (textLower.includes(word) || textArabic.includes(word)) {
      negativeScore += 1;
    }
  }
  
  // كشف الاستدراك - لو فيه "بس" أو "لكن" يبقى فيه مشاعر مختلطة
  let hasContrast = false;
  for (const contrast of CONTRAST_WORDS) {
    if (textLower.includes(contrast) || textArabic.includes(contrast)) {
      hasContrast = true;
      break;
    }
  }
  
  // تحديد المشاعر
  let sentiment: 'positive' | 'negative' | 'neutral' = 'neutral';
  let confidence = 0.5;
  let label = 0;
  
  const totalScore = positiveScore + negativeScore;
  const scoreDiff = Math.abs(positiveScore - negativeScore);
  
  if (totalScore === 0) {
    // لو مفيش كلمات معروفة، نحلل بناءً على الرموز
    if (text.includes('⭐') || text.includes('👍') || text.includes('❤') || text.includes('😍')) {
      sentiment = 'positive';
      confidence = 0.7;
      label = 1;
    } else if (text.includes('👎') || text.includes('😡') || text.includes('💔') || text.includes('😤')) {
      sentiment = 'negative';
      confidence = 0.7;
      label = -1;
    } else {
      sentiment = 'neutral';
      confidence = 0.5;
      label = 0;
    }
  } else if (hasContrast && positiveScore > 0 && negativeScore > 0) {
    // لو فيه استدراك وفيه كلمات إيجابية وسلبية = مختلط/محايد
    sentiment = 'neutral';
    confidence = 0.7;
    label = 0;
  } else if (scoreDiff <= 1 && positiveScore > 0 && negativeScore > 0) {
    // لو الفرق قليل وفيه الاتنين = محايد
    sentiment = 'neutral';
    confidence = 0.6;
    label = 0;
  } else if (positiveScore > negativeScore) {
    sentiment = 'positive';
    confidence = Math.min(0.95, 0.6 + scoreDiff * 0.1);
    label = 1;
  } else if (negativeScore > positiveScore) {
    sentiment = 'negative';
    confidence = Math.min(0.95, 0.6 + scoreDiff * 0.1);
    label = -1;
  } else {
    sentiment = 'neutral';
    confidence = 0.5;
    label = 0;
  }
  
  return {
    text,
    sentiment,
    confidence,
    label,
    processed_text: text
  };
}

/**
 * Analyze sentiment of a single text - سريع ودقيق
 */
export async function analyzeSentiment(text: string): Promise<SentimentResult & { warning?: string; isValidReview?: boolean }> {
  // التحقق من صحة التقييم
  const validation = isValidReview(text);
  
  if (!validation.isValid) {
    return {
      text,
      sentiment: 'neutral',
      confidence: 0,
      label: 0,
      processed_text: text,
      warning: validation.reason,
      isValidReview: false
    };
  }
  
  // استخدام التحليل السريع
  const result = quickAnalyze(text);
  return { ...result, isValidReview: true };
}

/**
 * Analyze sentiment of multiple texts
 */
export async function batchAnalyzeSentiment(texts: string[]): Promise<SentimentResult[]> {
  const results: SentimentResult[] = [];
  
  // Process texts in parallel (with limit to avoid overwhelming the system)
  const batchSize = 10;
  for (let i = 0; i < texts.length; i += batchSize) {
    const batch = texts.slice(i, i + batchSize);
    const batchResults = await Promise.all(
      batch.map(text => analyzeSentiment(text).catch(error => ({
        text,
        sentiment: 'neutral' as const,
        confidence: 0,
        label: 0,
        error: error instanceof Error ? error.message : 'Unknown error'
      })))
    );
    results.push(...batchResults);
  }

  return results;
}

