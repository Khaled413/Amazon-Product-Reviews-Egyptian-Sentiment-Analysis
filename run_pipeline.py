"""
سكريبت لتشغيل Pipeline كامل
Complete Pipeline Runner
"""

import os
import sys

def run_pipeline():
    """تشغيل Pipeline كامل من البداية للنهاية"""
    
    print("="*60)
    print("تشغيل Pipeline كامل لتحليل المشاعر")
    print("="*60)
    
    # 1. جمع البيانات
    print("\n[1/7] جمع البيانات...")
    try:
        from src.data_collection import create_sample_data
        create_sample_data()
        print("✓ تم جمع البيانات")
    except Exception as e:
        print(f"✗ خطأ في جمع البيانات: {e}")
        return
    
    # 2. تنظيف البيانات
    print("\n[2/7] تنظيف البيانات...")
    try:
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner()
        input_file = "data/raw/sample_reviews.json"
        if os.path.exists(input_file):
            cleaner.clean_dataset(input_file)
            print("✓ تم تنظيف البيانات")
        else:
            print("⚠ ملف البيانات غير موجود، تخطي...")
    except Exception as e:
        print(f"✗ خطأ في تنظيف البيانات: {e}")
        return
    
    # 3. فلترة اللهجة المصرية
    print("\n[3/7] فلترة اللهجة المصرية...")
    try:
        from src.dialect_filter import DialectFilter
        filter_tool = DialectFilter(threshold=0.3)
        input_file = "data/cleaned/sample_reviews_cleaned.json"
        if os.path.exists(input_file):
            filter_tool.filter_dataset(input_file)
            print("✓ تم فلترة البيانات")
        else:
            print("⚠ ملف البيانات غير موجود، تخطي...")
    except Exception as e:
        print(f"✗ خطأ في فلترة البيانات: {e}")
        return
    
    # 4. تصنيف المشاعر
    print("\n[4/7] تصنيف المشاعر...")
    try:
        from src.annotation_tool import create_sample_annotations
        input_file = "data/cleaned/sample_reviews_cleaned_egyptian_only.json"
        if not os.path.exists(input_file):
            input_file = "data/cleaned/sample_reviews_cleaned.json"
        if os.path.exists(input_file):
            # تعديل المسار في annotation_tool
            import src.annotation_tool as ann_module
            ann_module.create_sample_annotations.__globals__['data_file'] = input_file
            create_sample_annotations()
            print("✓ تم تصنيف البيانات")
        else:
            print("⚠ ملف البيانات غير موجود، تخطي...")
    except Exception as e:
        print(f"✗ خطأ في تصنيف البيانات: {e}")
        return
    
    # 5. معالجة النصوص
    print("\n[5/7] معالجة النصوص...")
    try:
        from src.preprocessing import prepare_training_data
        input_file = "data/annotated/sample_reviews_cleaned_egyptian_only_annotated.json"
        if not os.path.exists(input_file):
            input_file = "data/annotated/sample_reviews_cleaned_annotated.json"
        if os.path.exists(input_file):
            prepare_training_data(input_file)
            print("✓ تم معالجة النصوص")
        else:
            print("⚠ ملف البيانات غير موجود، تخطي...")
    except Exception as e:
        print(f"✗ خطأ في معالجة النصوص: {e}")
        return
    
    # 6. استخراج الخصائص
    print("\n[6/7] استخراج الخصائص...")
    try:
        from src.feature_extraction import extract_features_from_file
        input_file = "data/processed/sample_reviews_cleaned_egyptian_only_annotated_processed.json"
        if not os.path.exists(input_file):
            input_file = "data/processed/sample_reviews_cleaned_annotated_processed.json"
        if os.path.exists(input_file):
            extract_features_from_file(input_file, method='tfidf')
            print("✓ تم استخراج الخصائص")
        else:
            print("⚠ ملف البيانات غير موجود، تخطي...")
    except Exception as e:
        print(f"✗ خطأ في استخراج الخصائص: {e}")
        return
    
    # 7. تدريب النماذج
    print("\n[7/7] تدريب النماذج...")
    try:
        from src.training import train_models_from_file
        input_file = "data/processed/sample_reviews_cleaned_egyptian_only_annotated_processed_features_tfidf.pkl"
        if not os.path.exists(input_file):
            input_file = "data/processed/sample_reviews_cleaned_annotated_processed_features_tfidf.pkl"
        if os.path.exists(input_file):
            train_models_from_file(input_file, models=['lr', 'svm', 'rf'])
            print("✓ تم تدريب النماذج")
        else:
            print("⚠ ملف البيانات غير موجود، تخطي...")
    except Exception as e:
        print(f"✗ خطأ في تدريب النماذج: {e}")
        return
    
    print("\n" + "="*60)
    print("✓ تم إكمال Pipeline بنجاح!")
    print("="*60)
    print("\nيمكنك الآن:")
    print("  1. تشغيل evaluation.py لتقييم النماذج")
    print("  2. تشغيل app.py لاستخدام الواجهة")

if __name__ == "__main__":
    run_pipeline()


