import { Router, Request, Response } from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const router = Router();

/**
 * GET /api/health
 * Health check endpoint
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    // Check Python availability
    let pythonAvailable = false;
    try {
      await execAsync('python --version');
      pythonAvailable = true;
    } catch (error) {
      try {
        await execAsync('python3 --version');
        pythonAvailable = true;
      } catch (error) {
        pythonAvailable = false;
      }
    }

    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      python: pythonAvailable ? 'available' : 'not available',
      service: 'Egyptian Sentiment Analysis API'
    });
  } catch (error) {
    res.status(500).json({
      status: 'unhealthy',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export { router as healthRouter };


