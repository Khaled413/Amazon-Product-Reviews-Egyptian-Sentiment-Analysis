import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import path from 'path';
import { sentimentRouter } from './routes/sentiment';
import { healthRouter } from './routes/health';
import { productRouter } from './routes/product';
import { projectInfoRouter } from './routes/projectInfo';

dotenv.config();

const app = express();
const PORT: number = parseInt(process.env.PORT || '3000', 10);
const HOST: string = process.env.HOST || '0.0.0.0';

// Middleware - بسيط ومباشر
app.use(cors({ origin: '*' }));
app.use(helmet({ 
  contentSecurityPolicy: false,
  crossOriginEmbedderPolicy: false
}));
app.use(morgan('dev'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Serve static files - المسار الصحيح
// __dirname في compiled code بيكون dist/, ف publicPath بيكون api/public
const publicPath = path.resolve(__dirname, '..', 'public');
console.log('📁 Public path:', publicPath);
console.log('📁 __dirname:', __dirname);

// Serve static files - مهم جداً يكون قبل أي middleware تاني
app.use(express.static(publicPath, {
  setHeaders: (res, filePath) => {
    if (filePath.endsWith('.css')) {
      res.setHeader('Content-Type', 'text/css; charset=utf-8');
    } else if (filePath.endsWith('.js')) {
      res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
    } else if (filePath.endsWith('.html')) {
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
    }
  }
}));

// API Routes
app.use('/api/health', healthRouter);
app.use('/api/sentiment', sentimentRouter);
app.use('/api/product', productRouter);
app.use('/api/project-info', projectInfoRouter);

// Root endpoint - يرجع HTML
app.get('/', (req: Request, res: Response) => {
  const indexPath = path.join(publicPath, 'index-modern.html');
  console.log('Serving index-modern.html from:', indexPath);
  res.sendFile(indexPath);
});

// 404 handler - فقط للـ API routes
app.use('/api/*', (req: Request, res: Response) => {
  res.status(404).json({
    error: 'Not found',
    message: `API route ${req.path} not found`
  });
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// Start server
app.listen(PORT, HOST, () => {
  const os = require('os');
  const networkInterfaces = os.networkInterfaces();
  const ips: string[] = [];
  
  for (const interfaceName in networkInterfaces) {
    const interfaces = networkInterfaces[interfaceName];
    if (interfaces) {
      for (const iface of interfaces) {
        if (iface.family === 'IPv4' && !iface.internal) {
          ips.push(iface.address);
        }
      }
    }
  }
  
  const mainIP = ips.length > 0 ? ips[0] : 'localhost';
  
  console.log(`\n🚀 Server running!`);
  console.log(`📱 Local:    http://localhost:${PORT}`);
  if (ips.length > 0) {
    console.log(`🌐 Network:  http://${mainIP}:${PORT}`);
  }
  console.log(`\n`);
});

export default app;

