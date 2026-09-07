# aco_engine/utils.py
import pandas as pd
import numpy as np
import os
import sys
from sqlalchemy import text, create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
from datetime import datetime

# تحميل متغيرات البيئة
load_dotenv()

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_db_engine() -> Engine:
    """
    إنشاء اتصال بقاعدة البيانات مع تحسينات الأداء
    """
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'rober123')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'telecom_churn_db_v2')
    
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        echo=False
    )
    
    return engine


def load_data_from_db() -> pd.DataFrame:
    """
    تحميل بيانات العملاء من قاعدة البيانات
    """
    print("🔌 جاري الاتصال بقاعدة البيانات...")
    engine = get_db_engine()
    
    try:
        query = """
            SELECT 
                id, circle_id,
                arpu_6, arpu_7, arpu_8,
                total_og_mou_6, total_og_mou_7, total_og_mou_8,
                total_ic_mou_6, total_ic_mou_7, total_ic_mou_8,
                total_rech_amt_6, total_rech_amt_7, total_rech_amt_8,
                total_rech_num_6, total_rech_num_7, total_rech_num_8,
                aon,
                vol_3g_mb_6, vol_3g_mb_7, vol_3g_mb_8
            FROM customers
            ORDER BY id
        """
        
        print("📥 جاري تحميل البيانات...")
        df = pd.read_sql(query, engine)
        print(f"✅ تم تحميل {len(df):,} سجل بنجاح")
        
        return df
        
    except Exception as e:
        print(f"❌ خطأ في تحميل البيانات: {e}")
        return pd.DataFrame()


def calculate_churn_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    حساب مؤشرات التسرب (Churn Indicators) - تراجع الاستهلاك
    """
    print("📊 جاري حساب مؤشرات التسرب...")
    
    df = df.copy()
    
    # مؤشرات التراجع الشهرية
    df['arpu_decline'] = (df['arpu_8'] - df['arpu_7']).fillna(0)
    df['arpu_decline_pct'] = (df['arpu_8'] - df['arpu_7']) / (df['arpu_7'] + 1e-10)
    
    df['mou_decline'] = (df['total_og_mou_8'] - df['total_og_mou_7']).fillna(0)
    df['mou_decline_pct'] = (df['total_og_mou_8'] - df['total_og_mou_7']) / (df['total_og_mou_7'] + 1e-10)
    
    df['rech_decline'] = (df['total_rech_amt_8'] - df['total_rech_amt_7']).fillna(0)
    df['rech_decline_pct'] = (df['total_rech_amt_8'] - df['total_rech_amt_7']) / (df['total_rech_amt_7'] + 1e-10)
    
    # مؤشرات النشاط
    df['total_mou_8'] = df['total_og_mou_8'] + df['total_ic_mou_8']
    df['ic_og_ratio'] = df['total_ic_mou_8'] / (df['total_og_mou_8'] + 1e-10)
    df['avg_rech_value'] = df['total_rech_amt_8'] / (df['total_rech_num_8'] + 1e-10)
    
    print("✅ تم حساب مؤشرات التسرب")
    return df


def save_clustering_results(risk_results: pd.DataFrame) -> bool:
    """
    حفظ نتائج التجميع ودرجات المخاطرة في قاعدة البيانات
    """
    print("💾 جاري حفظ النتائج في قاعدة البيانات...")
    engine = get_db_engine()
    
    try:
        with engine.connect() as conn:
            # حذف النتائج القديمة
            conn.execute(text("TRUNCATE TABLE clustering_results CASCADE"))
            conn.commit()
            
            # إضافة timestamp
            risk_results = risk_results.copy()
            risk_results['updated_at'] = datetime.now()
            
            # حفظ النتائج
            risk_results.to_sql(
                'clustering_results', 
                con=engine, 
                if_exists='append', 
                index=False,
                chunksize=10000
            )
            
            # التحقق
            result = conn.execute(text("SELECT COUNT(*) FROM clustering_results"))
            count = result.scalar()
            print(f"✅ تم حفظ {count:,} نتيجة في clustering_results")
            
            return True
            
    except Exception as e:
        print(f" خطأ في حفظ النتائج: {e}")
        return False


def get_cluster_statistics(df: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    """
    حساب إحصائيات تفصيلية لكل عنقود (Cluster Profiling)
    """
    df_temp = df.copy()
    df_temp['cluster_id'] = labels
    
    stats = df_temp.groupby('cluster_id').agg({
        'arpu_8': ['mean', 'median', 'std'],
        'total_og_mou_8': ['mean', 'median'],
        'total_ic_mou_8': ['mean', 'median'],
        'total_rech_amt_8': ['mean', 'median'],
        'total_rech_num_8': ['mean', 'median'],
        'aon': ['mean', 'median'],
        'vol_3g_mb_8': ['mean', 'median'],
        'arpu_decline': 'mean',
        'mou_decline': 'mean',
        'rech_decline': 'mean'
    }).round(2)
    
    # تسطيح الأعمدة متعددة المستويات
    stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
    stats = stats.reset_index()
    
    # إضافة حجم العنقود
    sizes = df_temp['cluster_id'].value_counts().sort_index()
    stats['size'] = sizes.values
    stats['percentage'] = (sizes.values / len(df_temp) * 100).round(1)
    
    return stats


if __name__ == "__main__":
    # اختبار الدوال
    print("="*60)
    print("🧪 اختبار دوال utils.py")
    print("="*60)
    
    df = load_data_from_db()
    if not df.empty:
        df = calculate_churn_indicators(df)
        print(f"\n📊 أبعاد البيانات: {df.shape}")
        print(f"\n📋 الأعمدة:")
        print(df.columns.tolist())