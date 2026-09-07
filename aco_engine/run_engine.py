# aco_engine/run_engine.py
import sys
import os
import numpy as np
import pandas as pd
import logging

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aco_engine.utils import (
    load_data_from_db, 
    save_clustering_results, 
    calculate_churn_indicators,
    get_cluster_statistics
)
from aco_engine.preprocess import DataPreprocessor
from aco_engine.aco_clustering import AntColonyClustering
from aco_engine.risk_scoring import RiskScorer

# إعداد Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_aco_engine(
    n_clusters: int = 3, 
    n_ants: int = 15, 
    max_iter: int = 30, 
    n_components: int = 10
) -> dict:
    """
    تشغيل محرك ACO الكامل مع Cluster Profiling الديناميكي
    
    المميزات:
    - تحميل البيانات من قاعدة البيانات
    - معالجة البيانات وتقليل الأبعاد
    - تنفيذ خوارزمية ACO
    - Cluster Profiling ديناميكي (بدون تعيين ثابت)
    - حساب درجات المخاطرة
    - حفظ النتائج في قاعدة البيانات
    
    Returns:
        dict: يحتوي على جميع نتائج المحرك
    """
    
    print("="*70)
    print(" تشغيل محرك ACO للتجميع وتحليل المخاطرة")
    print("="*70)
    
    # ========================================
    # الخطوة 1: تحميل البيانات
    # ========================================
    print("\n الخطوة 1: تحميل البيانات من قاعدة البيانات...")
    df = load_data_from_db()
    
    if df.empty:
        print("❌ لا توجد بيانات للتحميل")
        return None
    
    print(f"✅ تم تحميل {len(df):,} عميل")
    
    # ========================================
    # الخطوة 2: حساب مؤشرات التسرب
    # ========================================
    print("\n📊 الخطوة 2: حساب مؤشرات التسرب...")
    df = calculate_churn_indicators(df)
    
    # ========================================
    # الخطوة 3: معالجة البيانات وتقليل الأبعاد
    # ========================================
    print("\n🔄 الخطوة 3: معالجة البيانات...")
    preprocessor = DataPreprocessor(n_components=n_components)
    X_pca, X_scaled, features = preprocessor.preprocess(df)
    
    print(f" شكل البيانات بعد المعالجة: {X_pca.shape}")
    print(f" التباين المفسر: {preprocessor.pca.explained_variance_ratio_.sum():.2%}")
    
    # تنظيف القيم غير الصالحة
    X_pca = np.nan_to_num(X_pca, nan=0.0, posinf=0.0, neginf=0.0)
    
    # ========================================
    # الخطوة 4: تنفيذ خوارزمية ACO
    # ========================================
    print("\n🐜 الخطوة 4: تنفيذ خوارزمية ACO...")
    aco = AntColonyClustering(
        n_clusters=n_clusters,
        n_ants=n_ants,
        max_iter=max_iter,
        random_state=42,
        convergence_threshold=0.001
    )
    
    aco.fit(X_pca)
    
    # الحصول على النتائج
    cluster_labels = aco.labels_
    cluster_centers = aco.cluster_centers_
    
    # ========================================
    # الخطوة 5: Cluster Profiling الديناميكي
    # ========================================
    print("\n الخطوة 5: Cluster Profiling الديناميكي...")
    print("-"*70)
    
    # حساب إحصائيات كل عنقود
    cluster_stats = get_cluster_statistics(df, cluster_labels)
    print("\n📊 إحصائيات العناقيد:")
    print(cluster_stats.to_string())
    
    # ========================================
    # الخطوة 6: حساب درجات المخاطرة (ديناميكي)
    # ========================================
    print("\n⚠️ الخطوة 6: حساب درجات المخاطرة...")
    scorer = RiskScorer()
    
    # استخدام Cluster Profiling الديناميكي
    risk_results = scorer.calculate_risk_scores(
        df=df,
        cluster_labels=cluster_labels
    )
    
    # عرض التوزيع
    print("\n توزيع مستويات المخاطرة:")
    distribution, percentages = scorer.get_risk_distribution(risk_results)
    for level, count in distribution.items():
        print(f"   {level}: {count:,} عميل ({percentages[level]:.1f}%)")
    
    # ========================================
    # الخطوة 7: حفظ النتائج في قاعدة البيانات
    # ========================================
    print("\n💾 الخطوة 7: حفظ النتائج...")
    save_clustering_results(risk_results)
    
    # ========================================
    # الخطوة 8: عرض العملاء الأكثر خطورة
    # ========================================
    print("\n🔥 الخطوة 8: العملاء الأكثر خطورة...")
    high_risk = scorer.get_high_risk_customers(risk_results)
    print(f"   عدد العملاء عاليي الخطورة: {len(high_risk):,}")
    
    if len(high_risk) > 0:
        print("\n📋 نموذج لأكثر 5 عملاء خطورة:")
        print(high_risk[['id', 'risk_score', 'risk_level', 'cluster_id']].head())
    
    # ========================================
    # الخطوة 9: إحصائيات الأداء
    # ========================================
    print("\n📈 إحصائيات الأداء:")
    if aco.history_:
        print(f"   - Inertia النهائية: {aco.history_[-1]['best_inertia']:.2f}")
        print(f"   - عدد التكرارات الفعلية: {len(aco.history_)}")
    print(f"   - عدد العناقيد: {n_clusters}")
    print(f"   - تباين PCA: {preprocessor.pca.explained_variance_ratio_.sum():.2%}")
    
    print("\n" + "="*70)
    print("✅ اكتمل تشغيل محرك ACO بنجاح")
    print("="*70)
    
    # ========================================
    # إرجاع النتائج
    # ========================================
    return {
        'clusters': cluster_labels,
        'cluster_centers': cluster_centers,
        'cluster_stats': cluster_stats,
        'risk_results': risk_results,
        'aco_model': aco,
        'preprocessor': preprocessor,
        'processed_data': df,
        'features': features
    }


if __name__ == "__main__":
    # تشغيل المحرك بالمعاملات الافتراضية
    results = run_aco_engine(
        n_clusters=3,
        n_ants=15,
        max_iter=30,
        n_components=10
    )
    
    if results:
        print("\n تم تشغيل المحرك بنجاح!")
        print(f"📊 عدد العملاء المعالجين: {len(results['processed_data']):,}")
        print(f"🎯 عدد العناقيد: {results['clusters'].max() + 1}")