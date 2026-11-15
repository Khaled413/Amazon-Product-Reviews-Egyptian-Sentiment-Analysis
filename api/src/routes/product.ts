import { Router, Request, Response } from 'express';
import { body, validationResult } from 'express-validator';
import { execFile } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execFileAsync = promisify(execFile);
const router = Router();

// Helper function to validate Amazon URL
function isValidAmazonUrl(url: string): boolean {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();
    const amazonDomains = [
      'amazon.com', 'www.amazon.com',
      'amazon.eg', 'www.amazon.eg',
      'amazon.ae', 'www.amazon.ae',
      'amazon.sa', 'www.amazon.sa',
      'amazon.co.uk', 'www.amazon.co.uk',
      'amazon.de', 'www.amazon.de',
      'amazon.fr', 'www.amazon.fr',
      'amazon.it', 'www.amazon.it',
      'amazon.es', 'www.amazon.es',
      'amazon.in', 'www.amazon.in',
      'amazon.ca', 'www.amazon.ca',
      'amazon.com.au', 'www.amazon.com.au',
      'amazon.co.jp', 'www.amazon.co.jp',
    ];
    return amazonDomains.includes(hostname);
  } catch {
    return false;
  }
}

// Helper function to check if URL contains a product (ASIN)
function hasProductAsin(url: string): boolean {
  // ASIN is 10 alphanumeric characters after /dp/ or /gp/product/
  const asinPattern = /\/(dp|gp\/product)\/[A-Z0-9]{10}/i;
  return asinPattern.test(url);
}

/**
 * POST /api/product/analyze
 * Analyze an Amazon product by URL (scrape + NLP pipeline).
 */
router.post(
  '/analyze',
  [
    body('url')
      .notEmpty()
      .withMessage('Product URL is required')
      .isString()
      .withMessage('URL must be a string')
      .isLength({ max: 1024 })
      .withMessage('URL is too long'),
  ],
  async (req: Request, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation error',
        details: errors.array(),
      });
    }

    const { url } = req.body as { url: string };

    // التحقق من أن الرابط من أمازون
    if (!isValidAmazonUrl(url)) {
      return res.status(400).json({
        error: 'رابط غير صالح',
        message: 'الرابط ده مش من أمازون! لازم يكون من amazon.com أو amazon.eg',
      });
    }

    // التحقق من أن الرابط فيه منتج (ASIN)
    if (!hasProductAsin(url)) {
      return res.status(400).json({
        error: 'مفيش منتج',
        message: 'الرابط ده مفيهوش منتج! لازم يكون رابط منتج زي: amazon.eg/dp/B0XXXXX',
      });
    }

    // فحص البيئة السحابية Vercel: لا تدعم تشغيل سكريبتات Python المعقدة محلياً
    if (process.env.VERCEL) {
      return res.status(501).json({
        error: 'الخدمة غير متوفرة على بيئة Vercel السحابية',
        message: 'تحليل رابط المنتج الكامل وسحب المراجعات يتطلب بيئة بايثون محلية أو خادم مخصص. يمكنك تجربة ميزة "تحليل تقييم فردي" مباشرة!',
        isVercel: true
      });
    }

    try {
      const apiDir = path.resolve(__dirname, '..', '..');
      const projectRoot = path.resolve(apiDir, '..');
      const scriptPath = path.join(apiDir, 'scripts', 'analyze_product.py');

      const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

      const { stdout, stderr } = await execFileAsync(pythonCmd, [scriptPath, url], {
        cwd: projectRoot,
        maxBuffer: 20 * 1024 * 1024,
        encoding: 'buffer',
        timeout: 45000,
      });

      if (stderr && !stderr.toString('utf8').toLowerCase().includes('warning')) {
        console.warn('Python stderr:', stderr.toString('utf8'));
      }

      let data: any;
      try {
        const outputStr = stdout.toString('utf8').trim();
        const jsonStart = outputStr.indexOf('{');
        const jsonStr = jsonStart >= 0 ? outputStr.substring(jsonStart) : outputStr;
        data = JSON.parse(jsonStr);
      } catch (parseError) {
        console.error('Failed to parse Python output:', parseError);
        return res.status(500).json({
          error: 'فشل تحليل المنتج',
          message: 'حدث خطأ في معالجة البيانات',
        });
      }

      if (data?.error) {
        return res.status(500).json({
          error: data.error,
          message: data.message || 'فشل تحليل المنتج',
        });
      }

      return res.json({ success: true, data });
    } catch (error) {
      console.error('Error in /api/product/analyze:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      const isTimeout = errorMessage.includes('timeout') || errorMessage.includes('ETIMEDOUT');
      
      return res.status(500).json({
        error: 'فشل تحليل المنتج',
        message: isTimeout 
          ? 'استغرق التحليل وقتاً طويلاً، جرب تاني'
          : 'حدث خطأ أثناء تحليل المنتج',
      });
    }
  }
);

/**
 * POST /api/product/info
 * Get product info (price, specs, images) from Amazon URL.
 */
router.post(
  '/info',
  [
    body('url')
      .notEmpty()
      .withMessage('Product URL is required')
      .isString()
      .withMessage('URL must be a string')
      .isLength({ max: 1024 })
      .withMessage('URL is too long'),
  ],
  async (req: Request, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'الرابط غير صالح',
        message: 'يرجى إدخال رابط صالح',
      });
    }

    const { url } = req.body as { url: string };

    // التحقق من أن الرابط من أمازون
    if (!isValidAmazonUrl(url)) {
      return res.status(400).json({
        error: 'رابط غير صالح',
        message: 'الرابط ده مش من أمازون! لازم يكون من amazon.com أو amazon.eg',
      });
    }

    // التحقق من أن الرابط فيه منتج (ASIN)
    if (!hasProductAsin(url)) {
      return res.status(400).json({
        error: 'مفيش منتج',
        message: 'الرابط ده مفيهوش منتج! لازم يكون رابط منتج زي: amazon.eg/dp/B0XXXXX',
      });
    }

    // فحص البيئة السحابية Vercel: لا تدعم تشغيل سكريبتات Python المعقدة محلياً
    if (process.env.VERCEL) {
      return res.status(501).json({
        error: 'الخدمة غير متوفرة على بيئة Vercel السحابية',
        message: 'جلب بيانات المنتج من أمازون يتطلب بيئة بايثون محلية أو خادم مخصص.',
        isVercel: true
      });
    }

    try {
      const apiDir = path.resolve(__dirname, '..', '..');
      const projectRoot = path.resolve(apiDir, '..');
      const scriptPath = path.join(apiDir, 'scripts', 'product_info_scraper.py');

      const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

      const { stdout, stderr } = await execFileAsync(pythonCmd, [scriptPath, url], {
        cwd: projectRoot,
        maxBuffer: 20 * 1024 * 1024,
        encoding: 'buffer',
        timeout: 20000,
      });

      if (stderr) {
        console.log('Python stderr:', stderr.toString('utf8'));
      }

      let data: any;
      try {
        const outputStr = stdout.toString('utf8').trim();
        const jsonStart = outputStr.indexOf('{');
        const jsonStr = jsonStart >= 0 ? outputStr.substring(jsonStart) : outputStr;
        data = JSON.parse(jsonStr);
      } catch (parseError) {
        console.error('Failed to parse Python output:', parseError);
        return res.status(500).json({
          error: 'فشل جلب المعلومات',
          message: 'حدث خطأ في معالجة البيانات',
        });
      }

      if (data?.error) {
        return res.status(500).json({
          error: data.error,
          message: data.message || 'فشل جلب معلومات المنتج',
        });
      }

      return res.json({ success: true, data });
    } catch (error) {
      console.error('Error in /api/product/info:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      const isTimeout = errorMessage.includes('timeout') || errorMessage.includes('ETIMEDOUT');
      
      if (isTimeout) {
        return res.status(504).json({
          error: 'انتهت المهلة',
          message: 'استغرق جلب المعلومات وقتاً طويلاً، جرب تاني',
        });
      }
      
      return res.status(503).json({
        error: 'فشل الاتصال',
        message: 'أمازون تمنع الوصول حالياً، جرب تاني',
      });
    }
  }
);

export { router as productRouter };
