import { Router, Request, Response } from 'express';
import { body, validationResult } from 'express-validator';
import { analyzeSentiment, batchAnalyzeSentiment } from '../services/sentimentService';

const router = Router();

/**
 * POST /api/sentiment/analyze
 * Analyze sentiment of a single text
 */
router.post(
  '/analyze',
  [
    body('text')
      .notEmpty()
      .withMessage('Text is required')
      .isString()
      .withMessage('Text must be a string')
      .isLength({ min: 1, max: 1000 })
      .withMessage('Text must be between 1 and 1000 characters')
  ],
  async (req: Request, res: Response) => {
    try {
      // Check validation errors
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          error: 'Validation error',
          details: errors.array()
        });
      }

      const { text } = req.body;
      const result = await analyzeSentiment(text);

      res.json({
        success: true,
        data: result
      });
    } catch (error) {
      console.error('Error analyzing sentiment:', error);
      res.status(500).json({
        error: 'Failed to analyze sentiment',
        message: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

/**
 * POST /api/sentiment/batch
 * Analyze sentiment of multiple texts
 */
router.post(
  '/batch',
  [
    body('texts')
      .isArray()
      .withMessage('Texts must be an array')
      .notEmpty()
      .withMessage('Texts array cannot be empty')
      .custom((texts) => {
        if (texts.length > 100) {
          throw new Error('Maximum 100 texts allowed per batch');
        }
        return true;
      })
  ],
  async (req: Request, res: Response) => {
    try {
      // Check validation errors
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          error: 'Validation error',
          details: errors.array()
        });
      }

      const { texts } = req.body;
      const results = await batchAnalyzeSentiment(texts);

      res.json({
        success: true,
        count: results.length,
        data: results
      });
    } catch (error) {
      console.error('Error in batch analysis:', error);
      res.status(500).json({
        error: 'Failed to analyze sentiments',
        message: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

export { router as sentimentRouter };


