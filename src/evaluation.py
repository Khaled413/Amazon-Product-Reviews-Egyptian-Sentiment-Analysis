"""
تقييم النماذج
Model Evaluation Module
"""

import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_curve, auc
)
from typing import Dict, List, Tuple
import json

# تعيين الخطوط العربية
plt.rcParams['font.family'] = 'Arial Unicode MS'  # قد تحتاج تغيير هذا حسب نظامك

class ModelEvaluator:
    """فئة لتقييم النماذج"""
    
    def __init__(self, model, model_name: str = "model"):
        """
        Args:
            model: النموذج المدرب
            model_name: اسم النموذج
        """
        self.model = model
        self.model_name = model_name
        self.predictions = None
        self.probabilities = None
    
    def evaluate(self, X_test, y_test) -> Dict:
        """
        تقييم النموذج
        
        Args:
            X_test: بيانات الاختبار
            y_test: التصنيفات الحقيقية
        
        Returns:
            Dict: نتائج التقييم
        """
        # التنبؤ
        self.predictions = self.model.predict(X_test)
        
        try:
            self.probabilities = self.model.predict_proba(X_test)
        except:
            self.probabilities = None
        
        # حساب المقاييس
        accuracy = accuracy_score(y_test, self.predictions)
        precision = precision_score(y_test, self.predictions, average='weighted', zero_division=0)
        recall = recall_score(y_test, self.predictions, average='weighted', zero_division=0)
        f1 = f1_score(y_test, self.predictions, average='weighted', zero_division=0)
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, self.predictions)
        
        # Classification Report
        class_report = classification_report(
            y_test, self.predictions,
            target_names=['Negative', 'Neutral', 'Positive'],
            output_dict=True
        )
        
        results = {
            'model_name': self.model_name,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm.tolist(),
            'classification_report': class_report
        }
        
        return results
    
    def plot_confusion_matrix(self, y_test, save_path: str = None):
        """رسم Confusion Matrix"""
        cm = confusion_matrix(y_test, self.predictions)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Negative', 'Neutral', 'Positive'],
                   yticklabels=['Negative', 'Neutral', 'Positive'])
        plt.title(f'Confusion Matrix - {self.model_name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"تم حفظ الصورة في: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def generate_report(self, results: Dict, output_file: str = None):
        """إنشاء تقرير نصي"""
        if output_file is None:
            output_file = f"reports/{self.model_name}_evaluation_report.txt"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*60}\n")
            f.write(f"تقرير تقييم النموذج: {self.model_name}\n")
            f.write(f"{'='*60}\n\n")
            
            f.write("المقاييس العامة:\n")
            f.write(f"  الدقة (Accuracy): {results['accuracy']:.4f}\n")
            f.write(f"  الدقة التفصيلية (Precision): {results['precision']:.4f}\n")
            f.write(f"  الاستدعاء (Recall): {results['recall']:.4f}\n")
            f.write(f"  F1-Score: {results['f1_score']:.4f}\n\n")
            
            f.write("التقرير التفصيلي:\n")
            f.write(f"{'='*60}\n")
            report = results['classification_report']
            
            for label in ['Negative', 'Neutral', 'Positive']:
                if label in report:
                    f.write(f"\n{label}:\n")
                    f.write(f"  Precision: {report[label]['precision']:.4f}\n")
                    f.write(f"  Recall: {report[label]['recall']:.4f}\n")
                    f.write(f"  F1-Score: {report[label]['f1-score']:.4f}\n")
                    f.write(f"  Support: {report[label]['support']}\n")
            
            f.write(f"\n{'='*60}\n")
            f.write(f"المتوسطات:\n")
            f.write(f"  Macro Avg - Precision: {report['macro avg']['precision']:.4f}\n")
            f.write(f"  Macro Avg - Recall: {report['macro avg']['recall']:.4f}\n")
            f.write(f"  Macro Avg - F1-Score: {report['macro avg']['f1-score']:.4f}\n")
            f.write(f"  Weighted Avg - Precision: {report['weighted avg']['precision']:.4f}\n")
            f.write(f"  Weighted Avg - Recall: {report['weighted avg']['recall']:.4f}\n")
            f.write(f"  Weighted Avg - F1-Score: {report['weighted avg']['f1-score']:.4f}\n")
        
        print(f"تم حفظ التقرير في: {output_file}")

def compare_models(results_dict: Dict[str, Dict], output_dir: str = "reports"):
    """
    مقارنة عدة نماذج
    
    Args:
        results_dict: قاموس يحتوي على نتائج كل نموذج
        output_dir: مجلد الحفظ
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # إنشاء جدول مقارنة
    comparison_data = []
    for model_name, results in results_dict.items():
        comparison_data.append({
            'Model': model_name.upper(),
            'Accuracy': results['accuracy'],
            'Precision': results['precision'],
            'Recall': results['recall'],
            'F1-Score': results['f1_score']
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    
    # حفظ الجدول
    comparison_file = os.path.join(output_dir, "models_comparison.csv")
    df_comparison.to_csv(comparison_file, index=False, encoding='utf-8-sig')
    print(f"تم حفظ جدول المقارنة في: {comparison_file}")
    
    # رسم مقارنة
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    for idx, metric in enumerate(metrics):
        ax = axes[idx // 2, idx % 2]
        df_comparison.plot(x='Model', y=metric, kind='bar', ax=ax, legend=False)
        ax.set_title(metric)
        ax.set_ylabel('Score')
        ax.set_ylim([0, 1])
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    comparison_plot = os.path.join(output_dir, "models_comparison.png")
    plt.savefig(comparison_plot, dpi=300, bbox_inches='tight')
    print(f"تم حفظ مخطط المقارنة في: {comparison_plot}")
    plt.close()
    
    return df_comparison

def evaluate_all_models(test_file: str, models_dir: str = "models"):
    """
    تقييم جميع النماذج المحفوظة
    
    Args:
        test_file: مسار ملف بيانات الاختبار
        models_dir: مجلد النماذج
    """
    # تحميل بيانات الاختبار
    with open(test_file, 'rb') as f:
        test_data = pickle.load(f)
    
    X_test = np.array(test_data['features'])
    y_test = np.array(test_data['labels'])
    
    # البحث عن النماذج
    model_files = {}
    for file in os.listdir(models_dir):
        if file.endswith('.pkl'):
            model_name = file.replace('_model.pkl', '')
            model_files[model_name] = os.path.join(models_dir, file)
    
    if not model_files:
        print("لم يتم العثور على أي نماذج محفوظة")
        return
    
    results_dict = {}
    
    # تقييم كل نموذج
    for model_name, model_file in model_files.items():
        print(f"\n{'='*50}")
        print(f"تقييم النموذج: {model_name.upper()}")
        print(f"{'='*50}")
        
        try:
            # تحميل النموذج (هذا مثال بسيط - قد تحتاج تعديل حسب نوع النموذج)
            from src.training import ModelTrainer
            trainer = ModelTrainer(model_type=model_name)
            trainer.load(model_file)
            
            # التقييم
            evaluator = ModelEvaluator(trainer, model_name)
            results = evaluator.evaluate(X_test, y_test)
            results_dict[model_name] = results
            
            # طباعة النتائج
            print(f"Accuracy: {results['accuracy']:.4f}")
            print(f"Precision: {results['precision']:.4f}")
            print(f"Recall: {results['recall']:.4f}")
            print(f"F1-Score: {results['f1_score']:.4f}")
            
            # حفظ Confusion Matrix
            cm_path = f"reports/{model_name}_confusion_matrix.png"
            evaluator.plot_confusion_matrix(y_test, cm_path)
            
            # حفظ التقرير
            evaluator.generate_report(results)
            
        except Exception as e:
            print(f"خطأ في تقييم {model_name}: {e}")
            continue
    
    # مقارنة النماذج
    if len(results_dict) > 1:
        print("\n" + "="*50)
        print("مقارنة النماذج")
        print("="*50)
        comparison = compare_models(results_dict)
        print("\nجدول المقارنة:")
        print(comparison.to_string(index=False))
    
    return results_dict

if __name__ == "__main__":
    # اختبار التقييم
    test_file = "data/processed/sample_reviews_cleaned_annotated_processed_features_tfidf.pkl"
    
    if os.path.exists(test_file):
        print("بدء تقييم النماذج...")
        results = evaluate_all_models(test_file)
        print("\nتم التقييم بنجاح!")
    else:
        print("ملف البيانات غير موجود. يرجى تشغيل training.py أولاً")


