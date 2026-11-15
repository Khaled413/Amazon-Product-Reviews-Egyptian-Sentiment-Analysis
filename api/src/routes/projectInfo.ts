import { Router, Request, Response } from 'express';

const router = Router();

/**
 * GET /api/project-info
 * Get project information
 */
router.get('/', (req: Request, res: Response) => {
  try {
    const projectInfo = {
      name: 'منصة تحليل المشاعر المصرية',
      version: '4.0.0',
      description: 'منصة متقدمة لتحليل مشاعر مراجعات منتجات أمازون باللهجة المصرية. تحلل المشاعر، تكتشف السخرية والتقييمات المزيفة، وتعرض السعر والمواصفات.',
      features: [
        'تحليل مشاعر مراجعات أمازون باللهجة المصرية',
        'تصنيف المشاعر على 5 مستويات (إيجابي جداً → سلبي جداً)',
        'كشف السخرية في التقييمات',
        'كشف التقييمات المزيفة',
        'عرض سعر المنتج والخصومات',
        'عرض المواصفات التقنية للمنتج',
        'عرض صور المنتج',
        'استخراج المميزات والعيوب تلقائياً',
        'ملخص ذكي بالذكاء الاصطناعي',
        'واجهة مستخدم عصرية بتصميم داكن',
        'دعم كامل للغة العربية (RTL)'
      ],
      technologies: [
        { name: 'الخادم الخلفي', value: 'Node.js + Express + TypeScript' },
        { name: 'معالجة اللغة', value: 'Python + scikit-learn + NLTK' },
        { name: 'الواجهة الأمامية', value: 'HTML5 + CSS3 + JavaScript' },
        { name: 'نماذج التعلم الآلي', value: 'SVM (94.1%) + Random Forest (94.1%) + Logistic Regression (94.1%)' },
        { name: 'جمع البيانات', value: 'BeautifulSoup + Requests' },
        { name: 'واجهة برمجية', value: 'RESTful API مع JSON' }
      ],
      endpoints: [
        { method: 'GET', path: '/api/health', description: 'فحص حالة النظام' },
        { method: 'POST', path: '/api/sentiment/analyze', description: 'تحليل مشاعر تقييم واحد' },
        { method: 'POST', path: '/api/product/analyze', description: 'تحليل منتج كامل من أمازون (محلياً)' },
        { method: 'POST', path: '/api/product/info', description: 'جلب معلومات المنتج (السعر، المواصفات) (محلياً)' },
        { method: 'GET', path: '/api/project-info', description: 'معلومات المشروع' }
      ],
      models: [
        { name: 'SVM', accuracy: '94.1%', description: 'أعلى دقة وثبات' },
        { name: 'Random Forest', accuracy: '94.1%', description: 'متوازن' },
        { name: 'Logistic Regression', accuracy: '94.1%', description: 'أسرع' }
      ],
      supportedSites: ['amazon.eg', 'amazon.com', 'amazon.ae', 'amazon.sa'],
      developer: {
        name: 'Egyptian Sentiment Analysis Team',
        year: '2024-2025',
        description: 'مشروع تحليل مشاعر باللهجة المصرية'
      },
      date: new Date().toISOString().split('T')[0]
    };

    res.json(projectInfo);
  } catch (error) {
    console.error('Error getting project info:', error);
    res.status(500).json({
      error: 'Failed to get project information',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export { router as projectInfoRouter };
