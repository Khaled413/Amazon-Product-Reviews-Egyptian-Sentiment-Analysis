/**
 * Modern Egyptian Sentiment Analysis - Frontend
 * ATOS-fit Inspired Dark Theme
 */

// ============================================
// Configuration
// ============================================
const API_BASE = window.location.origin;
const API = {
    analyzeProduct: `${API_BASE}/api/product/analyze`,
    productInfo: `${API_BASE}/api/product/info`,
    analyzeReview: `${API_BASE}/api/sentiment/analyze`,
    projectInfo: `${API_BASE}/api/project-info`,
    health: `${API_BASE}/api/health`
};

// ============================================
// DOM Elements
// ============================================
const elements = {
    // Product Analyzer
    productUrl: document.getElementById('productUrl'),
    analyzeProductBtn: document.getElementById('analyzeProductBtn'),
    productResults: document.getElementById('productResults'),
    
    // Review Analyzer
    reviewText: document.getElementById('reviewText'),
    analyzeReviewBtn: document.getElementById('analyzeReviewBtn'),
    reviewResults: document.getElementById('reviewResults'),
    
    // UI Elements
    loadingOverlay: document.getElementById('loadingOverlay'),
    projectInfoBtn: document.getElementById('projectInfoBtn'),
    projectInfoModal: document.getElementById('projectInfoModal'),
    closeModalBtn: document.getElementById('closeModalBtn'),
    projectInfoContent: document.getElementById('projectInfoContent')
};

// ============================================
// Utility Functions
// ============================================
const utils = {
    showLoading() {
        elements.loadingOverlay.classList.remove('hidden');
    },
    
    hideLoading() {
        elements.loadingOverlay.classList.add('hidden');
    },
    
    showError(message, type = 'error') {
        // إنشاء مربع الخطأ
        const existingToast = document.querySelector('.toast-message');
        if (existingToast) existingToast.remove();
        
        const icons = {
            error: '❌',
            warning: '⚠️',
            success: '✅',
            info: 'ℹ️'
        };
        
        const colors = {
            error: 'var(--negative)',
            warning: 'var(--neutral)',
            success: 'var(--positive)',
            info: 'var(--accent-primary)'
        };
        
        const toast = document.createElement('div');
        toast.className = 'toast-message';
        toast.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: var(--bg-card);
                border: 2px solid ${colors[type]};
                border-radius: 16px;
                padding: 1.5rem 2rem;
                box-shadow: 0 10px 40px rgba(0,0,0,0.5), 0 0 20px ${colors[type]}40;
                z-index: 10000;
                display: flex;
                align-items: center;
                gap: 1rem;
                max-width: 90%;
                animation: slideDown 0.3s ease;
            ">
                <span style="font-size: 2rem;">${icons[type]}</span>
                <div>
                    <p style="color: var(--text-white); font-weight: 600; font-size: 1rem; margin: 0;">
                        ${message}
                    </p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: var(--text-muted);
                    font-size: 1.5rem;
                    cursor: pointer;
                    padding: 0;
                    margin-right: -0.5rem;
                ">×</button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // إزالة تلقائية بعد 5 ثواني
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'slideUp 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    },
    
    isValidAmazonUrl(url) {
        // التحقق من أن الرابط من أمازون فقط
        try {
            const urlObj = new URL(url);
            const hostname = urlObj.hostname.toLowerCase();
            // التحقق إن الهوست هو amazon.xxx أو www.amazon.xxx
            const isAmazon = hostname === 'amazon.com' || 
                             hostname === 'www.amazon.com' ||
                             hostname.match(/^(www\.)?amazon\.(eg|ae|sa|co\.uk|de|fr|it|es|in|ca|com\.au|com\.br|com\.mx|co\.jp|nl|pl|se|sg|com\.tr)$/);
            return isAmazon;
        } catch (e) {
            return false;
        }
    },
    
    isValidProductUrl(url) {
        // التحقق من أن الرابط فيه منتج (ASIN)
        // ASIN هو 10 حروف/أرقام بعد /dp/ أو /gp/product/
        const asinPattern = /\/(dp|gp\/product)\/[A-Z0-9]{10}/i;
        return asinPattern.test(url);
    },
    
    formatPercent(value) {
        return Math.round(value * 100);
    },
    
    getSentimentEmoji(sentiment) {
        const emojis = {
            'positive': '😍',
            'very_positive': '😍',
            'negative': '😡',
            'very_negative': '😡',
            'neutral': '😐'
        };
        return emojis[sentiment] || '😐';
    },
    
    getSentimentClass(sentiment) {
        if (sentiment.includes('positive')) return 'positive';
        if (sentiment.includes('negative')) return 'negative';
        return 'neutral';
    }
};

// ============================================
// API Functions
// ============================================
const api = {
    async analyzeProduct(url) {
        const response = await fetch(API.analyzeProduct, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'فشل تحليل المنتج');
        }
        
        return await response.json();
    },
    
    async getProductInfo(url) {
        const response = await fetch(API.productInfo, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'فشل جلب معلومات المنتج');
        }
        
        return await response.json();
    },
    
    async analyzeReview(text) {
        const response = await fetch(API.analyzeReview, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'فشل تحليل التقييم');
        }
        
        return await response.json();
    },
    
    async getProjectInfo() {
        const response = await fetch(API.projectInfo);
        
        if (!response.ok) {
            throw new Error('فشل تحميل معلومات المشروع');
        }
        
        return await response.json();
    }
};

// ============================================
// UI Rendering Functions
// ============================================
const ui = {
    renderProductResults(data) {
        const dashboard = data.dashboard || {};
        const product = data.product || {};
        const reviews = data.reviews || [];
        
        const total = dashboard.total_reviews || 0;
        const sentimentDist = dashboard.sentiment_distribution || {};
        const ratingDist = dashboard.rating_distribution || {};
        
        // Calculate percentages
        const positiveCount = (sentimentDist.very_positive || 0) + (sentimentDist.positive || 0);
        const negativeCount = (sentimentDist.very_negative || 0) + (sentimentDist.negative || 0);
        const neutralCount = sentimentDist.neutral || 0;
        
        const positivePercent = total > 0 ? (positiveCount / total) * 100 : 0;
        const negativePercent = total > 0 ? (negativeCount / total) * 100 : 0;
        const neutralPercent = total > 0 ? (neutralCount / total) * 100 : 0;
        
        // استخدام التقييم الحقيقي من أمازون لو موجود
        let avgRating = 0;
        if (dashboard.real_rating) {
            // التقييم الحقيقي من أمازون
            avgRating = dashboard.real_rating;
        } else if (product.real_rating) {
            // التقييم الحقيقي من product info
            avgRating = product.real_rating;
        } else {
            // حساب من التقييمات المتاحة (fallback)
            let totalRatings = 0;
            for (const [rating, count] of Object.entries(ratingDist)) {
                avgRating += parseInt(rating) * count;
                totalRatings += count;
            }
            avgRating = totalRatings > 0 ? avgRating / totalRatings : 0;
        }
        
        // Determine quality
        let quality = 'متوسط';
        let qualityClass = 'neutral';
        if (avgRating >= 4.5) {
            quality = 'ممتاز';
            qualityClass = 'positive';
        } else if (avgRating >= 3.5) {
            quality = 'جيد';
            qualityClass = 'positive';
        } else if (avgRating < 2.5) {
            quality = 'سيء';
            qualityClass = 'negative';
        }
        
        // Get negative reviews
        const negativeReviews = reviews
            .filter(r => r.sentiment_5 && r.sentiment_5.includes('negative'))
            .slice(0, 5);
        
        const html = `
            <div class="result-card">
                <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--text-white);">
                    📊 نتيجة تحليل المنتج
                </h3>
                
                <!-- Product Info with Price -->
                <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-lg); margin-bottom: 1.5rem;">
                    
                    <!-- اسم المنتج أولاً -->
                    <h4 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-white); line-height: 1.5;">
                        ${product.title || 'Amazon Product'}
                    </h4>
                    
                    <!-- Star Rating -->
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                        <div class="star-rating">
                            ${this.renderStars(avgRating)}
                        </div>
                        <span style="font-size: 1.25rem; font-weight: 700; color: var(--text-white);">
                            ${avgRating.toFixed(1)} / 5.0
                        </span>
                        <!-- Quality Badge -->
                        <div class="sentiment-badge ${qualityClass}" style="display: inline-flex;">
                            <span>${quality}</span>
                        </div>
                    </div>
                    
                    <!-- السعر والمواصفات -->
                    ${data.productInfo ? this.renderProductInfoSection(data.productInfo) : ''}
                </div>
                
                <!-- Statistics Grid -->
                <div class="grid grid-3" style="margin-bottom: 1.5rem;">
                    <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-lg); text-align: center;">
                        <div style="font-size: 2rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 0.5rem;">
                            ${total}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">إجمالي التقييمات</div>
                    </div>
                    
                    <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-lg); text-align: center;">
                        <div style="font-size: 2rem; font-weight: 700; color: var(--positive); margin-bottom: 0.5rem;">
                            ${Math.round(positivePercent)}%
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">إيجابي</div>
                    </div>
                    
                    <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-lg); text-align: center;">
                        <div style="font-size: 2rem; font-weight: 700; color: var(--negative); margin-bottom: 0.5rem;">
                            ${Math.round(negativePercent)}%
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">سلبي</div>
                    </div>
                </div>
                
                <!-- Sentiment Distribution -->
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: var(--text-white);">
                        توزيع المشاعر
                    </h4>
                    
                    <div style="margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: var(--text-secondary);">إيجابي</span>
                            <span style="color: var(--text-white); font-weight: 600;">${Math.round(positivePercent)}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill positive" style="width: ${positivePercent}%"></div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: var(--text-secondary);">محايد</span>
                            <span style="color: var(--text-white); font-weight: 600;">${Math.round(neutralPercent)}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill neutral" style="width: ${neutralPercent}%"></div>
                        </div>
                    </div>
                    
                    <div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: var(--text-secondary);">سلبي</span>
                            <span style="color: var(--text-white); font-weight: 600;">${Math.round(negativePercent)}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill negative" style="width: ${negativePercent}%"></div>
                        </div>
                    </div>
                </div>
                
                <!-- AI Summary -->
                <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-lg); margin-bottom: 1.5rem;">
                    <h4 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: var(--text-white);">
                        🤖 ملخص الذكاء الاصطناعي
                    </h4>
                    <p style="color: var(--text-secondary); line-height: 1.8;">
                        ${this.generateAISummary(positivePercent, negativePercent, avgRating, quality)}
                    </p>
                </div>
                
                <!-- Pros & Cons -->
                ${this.renderProsAndCons(dashboard)}
                
                <!-- Sample Negative Reviews -->
                ${negativeReviews.length > 0 ? this.renderNegativeReviews(negativeReviews) : ''}
            </div>
        `;
        
        elements.productResults.innerHTML = html;
        elements.productResults.classList.remove('hidden');
        elements.productResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },
    
    renderStars(rating) {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= Math.round(rating)) {
                stars += '<span class="star">⭐</span>';
            } else {
                stars += '<span class="star empty">⭐</span>';
            }
        }
        return stars;
    },
    
    generateAISummary(positivePercent, negativePercent, avgRating, quality) {
        let summary = `المنتج ده تقييمه ${avgRating.toFixed(1)}/5.0، ومصنف على إنه "${quality}". `;
        
        if (positivePercent > 70) {
            summary += `${Math.round(positivePercent)}% من التقييمات إيجابية، والعملاء راضيين جداً عن المنتج. `;
        } else if (positivePercent > 50) {
            summary += `${Math.round(positivePercent)}% من التقييمات إيجابية، ومعظم العملاء راضيين. `;
        } else if (negativePercent > 50) {
            summary += `${Math.round(negativePercent)}% من التقييمات سلبية، وكتير من العملاء مش راضيين. `;
        } else {
            summary += `التقييمات متنوعة: ${Math.round(positivePercent)}% إيجابي و ${Math.round(negativePercent)}% سلبي. `;
        }
        
        if (positivePercent > 70) {
            summary += 'المنتج ده مرشح بقوة بناءً على آراء العملاء.';
        } else if (negativePercent > 50) {
            summary += 'فكر في منتجات تانية عندها تقييمات أحسن.';
        } else {
            summary += 'اقرأ التقييمات كويس قبل ما تشتري.';
        }
        
        return summary;
    },
    
    renderProsAndCons(dashboard) {
        const pros = dashboard.top_positive_phrases || [];
        const cons = dashboard.top_negative_phrases || [];
        
        if (pros.length === 0 && cons.length === 0) return '';
        
        return `
            <div class="grid grid-2" style="margin-bottom: 1.5rem;">
                ${pros.length > 0 ? `
                    <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-lg);">
                        <h4 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: var(--positive);">
                            ✅ المميزات
                        </h4>
                        <ul style="list-style: none; padding: 0;">
                            ${pros.slice(0, 5).map(pro => `
                                <li style="padding: 0.5rem 0; color: var(--text-secondary); border-bottom: 1px solid rgba(255,255,255,0.05);">
                                    • ${pro}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${cons.length > 0 ? `
                    <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-lg);">
                        <h4 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: var(--negative);">
                            ❌ العيوب
                        </h4>
                        <ul style="list-style: none; padding: 0;">
                            ${cons.slice(0, 5).map(con => `
                                <li style="padding: 0.5rem 0; color: var(--text-secondary); border-bottom: 1px solid rgba(255,255,255,0.05);">
                                    • ${con}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    },
    
    renderProductInfoSection(info) {
        if (!info) return '';
        
        const price = info.price || {};
        const rating = info.rating || {};
        const specs = info.specs || {};
        const images = info.images || [];
        
        // Format price
        let priceHtml = '';
        if (price.current) {
            const currencySymbol = price.currency === 'EGP' ? 'ج.م' : price.currency === 'USD' ? '$' : price.currency;
            priceHtml = `
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <span style="font-size: 2rem; font-weight: 700; color: var(--positive);">
                        ${price.current.toLocaleString()} ${currencySymbol}
                    </span>
                    ${price.original && price.discount_percent ? `
                        <span style="text-decoration: line-through; color: var(--text-muted); font-size: 1.25rem;">
                            ${price.original.toLocaleString()} ${currencySymbol}
                        </span>
                        <span style="background: var(--negative); color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem; font-weight: 600;">
                            -${price.discount_percent}%
                        </span>
                    ` : ''}
                </div>
            `;
        } else {
            priceHtml = `<p style="color: var(--text-muted); margin-bottom: 1rem;">السعر غير متوفر</p>`;
        }
        
        // Format specs
        let specsHtml = '';
        const specEntries = Object.entries(specs);
        if (specEntries.length > 0) {
            specsHtml = `
                <div style="margin-top: 1rem;">
                    <h5 style="font-size: 1rem; font-weight: 600; color: var(--text-white); margin-bottom: 0.75rem;">📋 المواصفات</h5>
                    <div style="display: grid; gap: 0.5rem;">
                        ${specEntries.slice(0, 6).map(([key, value]) => `
                            <div style="display: flex; gap: 0.5rem; padding: 0.5rem; background: var(--bg-tertiary); border-radius: 4px;">
                                <span style="color: var(--text-muted); min-width: 120px;">${key}:</span>
                                <span style="color: var(--text-secondary);">${value.substring(0, 100)}${value.length > 100 ? '...' : ''}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Product image
        let imageHtml = '';
        if (images.length > 0) {
            imageHtml = `
                <div style="float: left; margin-left: 1rem; margin-bottom: 1rem;">
                    <img src="${images[0]}" alt="Product" style="max-width: 150px; max-height: 150px; border-radius: 8px; object-fit: contain; background: white;">
                </div>
            `;
        }
        
        // Availability
        const availabilityHtml = info.availability ? `
            <span style="display: inline-block; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.875rem; 
                background: ${info.availability === 'متوفر' ? 'var(--positive)' : 'var(--negative)'}; color: white;">
                ${info.availability}
            </span>
        ` : '';
        
        return `
            <div style="margin-bottom: 1.5rem; overflow: hidden;">
                ${imageHtml}
                <div>
                    ${priceHtml}
                    ${availabilityHtml}
                    ${specsHtml}
                </div>
                <div style="clear: both;"></div>
            </div>
        `;
    },
    
    renderNegativeReviews(reviews) {
        return `
            <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-lg);">
                <h4 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: var(--text-white);">
                    📋 عينة من التقييمات السلبية
                </h4>
                ${reviews.map(review => `
                    <div style="padding: 1rem; background: var(--bg-tertiary); border-radius: var(--radius-md); margin-bottom: 1rem; border-left: 3px solid var(--negative);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="font-weight: 600; color: var(--text-white);">${review.author || 'Anonymous'}</span>
                            <span style="color: var(--text-muted); font-size: 0.875rem;">${review.date || ''}</span>
                        </div>
                        <div style="margin-bottom: 0.5rem;">
                            ${this.renderStars(review.rating || 1)}
                        </div>
                        <p style="color: var(--text-secondary); line-height: 1.6;">
                            ${review.text || review.title || 'No review text'}
                        </p>
                    </div>
                `).join('')}
            </div>
        `;
    },
    
    renderReviewResults(data) {
        const result = data.data || data;
        
        // لو فيه warning (النص مش تقييم)
        if (result.warning || result.isValidReview === false) {
            const html = `
                <div class="result-card">
                    <div style="text-align: center; padding: 2rem;">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">⚠️</div>
                        <h3 style="color: var(--neutral); font-size: 1.5rem; margin-bottom: 1rem;">
                            مش قادر أحلل ده!
                        </h3>
                        <p style="color: var(--text-secondary); font-size: 1.1rem; line-height: 1.8;">
                            ${result.warning || 'ده مش شبه تقييم منتج. اكتب رأيك في منتج أو تجربة شراء.'}
                        </p>
                        <div style="margin-top: 1.5rem; padding: 1rem; background: var(--bg-secondary); border-radius: var(--radius-md);">
                            <p style="color: var(--text-muted); font-size: 0.9rem;">
                                💡 مثال: "المنتج ده جامد جداً والجودة ممتازة" أو "الشحن اتأخر والمنتج مش زي الصورة"
                            </p>
                        </div>
                    </div>
                </div>
            `;
            elements.reviewResults.innerHTML = html;
            elements.reviewResults.classList.remove('hidden');
            elements.reviewResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            return;
        }
        
        const sentiment = result.sentiment || 'neutral';
        const confidence = result.confidence || 0;
        const emoji = utils.getSentimentEmoji(sentiment);
        const sentimentClass = utils.getSentimentClass(sentiment);
        
        // Generate explanation
        const explanation = this.generateExplanation(sentiment, confidence);
        
        const html = `
            <div class="result-card">
                <div style="text-align: center; margin-bottom: 2rem;">
                    <div class="sentiment-badge ${sentimentClass}" style="font-size: 1.5rem;">
                        <span style="font-size: 3rem;">${emoji}</span>
                        <span>${sentiment.includes('positive') ? 'إيجابي' : sentiment.includes('negative') ? 'سلبي' : 'محايد'}</span>
                    </div>
                </div>
                
                <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-lg);">
                    <h4 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: var(--text-white);">
                        🤖 شرح الذكاء الاصطناعي
                    </h4>
                    <p style="color: var(--text-secondary); line-height: 1.8;">
                        ${explanation}
                    </p>
                </div>
            </div>
        `;
        
        elements.reviewResults.innerHTML = html;
        elements.reviewResults.classList.remove('hidden');
        elements.reviewResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },
    
    generateExplanation(sentiment, confidence) {
        const confidenceLevel = confidence > 0.8 ? 'متأكد جداً' : confidence > 0.6 ? 'متأكد' : 'متأكد نوعاً ما';
        
        const sentimentAr = sentiment.includes('positive') ? 'إيجابي' : sentiment.includes('negative') ? 'سلبي' : 'محايد';
        
        let explanation = `الذكاء الاصطناعي ${confidenceLevel} إن التقييم ده ${sentimentAr}. `;
        
        if (sentiment.includes('positive')) {
            explanation += 'التقييم فيه كلام إيجابي ومدح وعلامات رضا. ';
            explanation += 'العميل يبدو إنه مبسوط من المنتج.';
        } else if (sentiment.includes('negative')) {
            explanation += 'التقييم فيه كلام سلبي وشكاوى وعلامات عدم رضا. ';
            explanation += 'العميل يبدو إنه مش مبسوط من المنتج.';
        } else {
            explanation += 'التقييم فيه كلام متوازن ومحايد من غير علامات قوية إيجابية أو سلبية. ';
            explanation += 'العميل يبدو عنده مشاعر مختلطة.';
        }
        
        return explanation;
    },
    
    renderProjectInfo(data) {
        const html = `
            <div style="padding: 1rem 0;">
                <div style="margin-bottom: 2rem;">
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 1rem;">
                        📌 عن المشروع
                    </h3>
                    <p style="color: var(--text-secondary); line-height: 1.8;">
                        ${data.description || 'منصة متقدمة لتحليل مشاعر مراجعات أمازون باللهجة المصرية'}
                    </p>
                </div>
                
                <div style="margin-bottom: 2rem;">
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 1rem;">
                        🚀 المميزات
                    </h3>
                    <ul style="list-style: none; padding: 0;">
                        ${(data.features || [
                            'تحليل مشاعر مراجعات أمازون',
                            'تصنيف 5 مستويات للمشاعر',
                            'كشف السخرية والتقييمات المزيفة',
                            'عرض السعر والمواصفات'
                        ]).map(feature => `
                            <li style="padding: 0.5rem; background: var(--bg-tertiary); border-radius: var(--radius-md); margin-bottom: 0.25rem; color: var(--text-secondary); font-size: 0.875rem;">
                                ✅ ${feature}
                            </li>
                        `).join('')}
                    </ul>
                </div>
                
                ${data.models ? `
                <div style="margin-bottom: 2rem;">
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 1rem;">
                        🤖 النماذج المستخدمة
                    </h3>
                    <div style="display: flex; gap: 1rem; justify-content: space-between;">
                        ${data.models.map(model => `
                            <div style="flex: 1; padding: 1rem; background: var(--bg-tertiary); border-radius: var(--radius-md); text-align: center;">
                                <div style="font-weight: 700; color: var(--positive); font-size: 1.5rem; margin-bottom: 0.25rem;">
                                    ${model.accuracy}
                                </div>
                                <div style="font-weight: 600; color: var(--text-white); margin-bottom: 0.25rem;">
                                    ${model.name}
                                </div>
                                <div style="color: var(--text-muted); font-size: 0.75rem;">
                                    ${model.description}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                <div style="margin-bottom: 2rem;">
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 1rem;">
                        🛠️ التقنيات
                    </h3>
                    <div class="grid grid-2">
                        ${(data.technologies || [
                            { name: 'Backend', value: 'Node.js + Express + TypeScript' },
                            { name: 'ML/NLP', value: 'Python + scikit-learn + NLTK' },
                            { name: 'Frontend', value: 'HTML5 + CSS3 + JavaScript' },
                            { name: 'Scraping', value: 'BeautifulSoup + Requests' }
                        ]).map(tech => `
                            <div style="padding: 0.75rem; background: var(--bg-tertiary); border-radius: var(--radius-md);">
                                <div style="font-weight: 600; color: var(--text-white); font-size: 0.875rem;">
                                    ${tech.name}
                                </div>
                                <div style="color: var(--text-secondary); font-size: 0.75rem;">
                                    ${tech.value}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                ${data.supportedSites ? `
                <div style="margin-bottom: 2rem;">
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 1rem;">
                        🌐 المواقع المدعومة
                    </h3>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                        ${data.supportedSites.map(site => `
                            <span style="padding: 0.5rem 1rem; background: var(--bg-tertiary); border-radius: 20px; color: var(--text-secondary); font-size: 0.875rem;">
                                🛒 ${site}
                            </span>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
            </div>
        `;
        
        elements.projectInfoContent.innerHTML = html;
    }
};

// ============================================
// Event Handlers
// ============================================
const handlers = {
    async analyzeProduct() {
        const url = elements.productUrl.value.trim();
        
        if (!url) {
            utils.showError('من فضلك حط لينك المنتج من أمازون', 'warning');
            return;
        }
        
        // التحقق من أن الرابط من أمازون
        if (!utils.isValidAmazonUrl(url)) {
            utils.showError('الرابط ده مش من أمازون! لازم يكون من amazon.com أو amazon.eg', 'error');
            return;
        }
        
        // التحقق من أن الرابط فيه منتج
        if (!utils.isValidProductUrl(url)) {
            utils.showError('الرابط ده مفيهوش منتج! لازم يكون رابط منتج زي: amazon.eg/dp/B0XXXXX', 'error');
            return;
        }
        
        try {
            utils.showLoading();
            elements.analyzeProductBtn.disabled = true;
            
            // جلب الاتنين بالتوازي عشان نوفر وقت
            const [infoResult, analysisResult] = await Promise.all([
                api.getProductInfo(url).catch(e => ({ success: false, error: e })),
                api.analyzeProduct(url).catch(e => ({ success: false, error: e }))
            ]);
            
            // Get analysis data
            let data = {};
            if (analysisResult.success) {
                data = analysisResult.data;
            } else {
                throw new Error(analysisResult.message || 'فشل تحليل المنتج');
            }
            
            // Add product info (price, specs) if available
            if (infoResult.success && infoResult.data) {
                data.productInfo = infoResult.data;
                // Update product title if we got a better one
                if (infoResult.data.title && infoResult.data.title !== 'فشل جلب المعلومات') {
                    data.product = data.product || {};
                    data.product.title = infoResult.data.title;
                }
            }
            
            ui.renderProductResults(data);
            
        } catch (error) {
            console.error('Product analysis error:', error);
            utils.showError(error.message || 'حصل مشكلة في تحليل المنتج، جرب تاني', 'error');
        } finally {
            utils.hideLoading();
            elements.analyzeProductBtn.disabled = false;
        }
    },
    
    async analyzeReview() {
        const text = elements.reviewText.value.trim();
        
        if (!text) {
            utils.showError('من فضلك اكتب نص التقييم الأول', 'warning');
            return;
        }
        
        try {
            utils.showLoading();
            elements.analyzeReviewBtn.disabled = true;
            
            const result = await api.analyzeReview(text);
            
            if (result.success) {
                ui.renderReviewResults(result);
            } else {
                throw new Error(result.error || 'فشل التحليل');
            }
        } catch (error) {
            console.error('Review analysis error:', error);
            utils.showError(error.message || 'حصل مشكلة في تحليل التقييم، جرب تاني', 'error');
        } finally {
            utils.hideLoading();
            elements.analyzeReviewBtn.disabled = false;
        }
    },
    
    async showProjectInfo() {
        try {
            const data = await api.getProjectInfo();
            ui.renderProjectInfo(data);
            elements.projectInfoModal.classList.remove('hidden');
        } catch (error) {
            console.error('Project info error:', error);
            // Show default info if API fails
            ui.renderProjectInfo({});
            elements.projectInfoModal.classList.remove('hidden');
        }
    },
    
    closeModal() {
        elements.projectInfoModal.classList.add('hidden');
    }
};

// ============================================
// Event Listeners
// ============================================
function initializeApp() {
    // Product Analyzer
    elements.analyzeProductBtn.addEventListener('click', handlers.analyzeProduct);
    elements.productUrl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handlers.analyzeProduct();
    });
    
    // Review Analyzer
    elements.analyzeReviewBtn.addEventListener('click', handlers.analyzeReview);
    elements.reviewText.addEventListener('keypress', (e) => {
        if (e.ctrlKey && e.key === 'Enter') handlers.analyzeReview();
    });
    
    // Project Info
    elements.projectInfoBtn.addEventListener('click', handlers.showProjectInfo);
    elements.closeModalBtn.addEventListener('click', handlers.closeModal);
    
    // Close modal on overlay click
    elements.projectInfoModal.addEventListener('click', (e) => {
        if (e.target === elements.projectInfoModal) {
            handlers.closeModal();
        }
    });
    
    console.log('✅ Modern Egyptian Sentiment Analysis initialized');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
