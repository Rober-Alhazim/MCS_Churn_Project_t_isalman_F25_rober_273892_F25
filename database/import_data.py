# database/import_data.py
import pandas as pd
import os
import sys
from sqlalchemy import text
from db_config import get_db_connection

# إضافة مسار المشروع للـ Python Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def import_data_to_db(file_path: str):
    """استيراد بيانات Excel إلى قاعدة البيانات الجديدة"""
    
    # 1. التحقق من وجود الملف
    if not os.path.exists(file_path):
        print(f"❌ الملف غير موجود: {file_path}")
        return False
    
    print(f"📂 جاري قراءة الملف: {file_path} ...")
    
    # 2. قراءة بيانات Excel
    try:
        # استخدام openpyxl لقراءة ملفات xlsx
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"📊 تم قراءة {len(df)} سجل بنجاح من ملف Excel.")
    except Exception as e:
        print(f" خطأ في قراءة ملف Excel: {e}")
        print("💡 تأكد من تثبيت مكتبة openpyxl: pip install openpyxl")
        return False

    # 3. اختيار الأعمدة المطلوبة فقط (لتقليل حجم البيانات وتسريع ACO)
    required_columns = [
        'id', 'circle_id', 
        'arpu_6', 'arpu_7', 'arpu_8',
        'total_og_mou_6', 'total_og_mou_7', 'total_og_mou_8',
        'total_ic_mou_6', 'total_ic_mou_7', 'total_ic_mou_8',
        'total_rech_amt_6', 'total_rech_amt_7', 'total_rech_amt_8',
        'total_rech_num_6', 'total_rech_num_7', 'total_rech_num_8',
        'aon', 
        'vol_3g_mb_6', 'vol_3g_mb_7', 'vol_3g_mb_8'
    ]
    
    # فلترة الأعمدة الموجودة فعلياً في الملف
    available_columns = [col for col in required_columns if col in df.columns]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"⚠️ تحذير: الأعمدة التالية غير موجودة في الملف: {missing_columns}")
        
    df = df[available_columns]
    
    # 4. معالجة القيم المفقودة (NaN) وتحويلها إلى None لـ PostgreSQL
    df = df.where(pd.notnull(df), None)
    
    # 5. الاتصال بقاعدة البيانات
    print("🔌 جاري الاتصال بقاعدة البيانات (telecom_churn_db_v2)...")
    engine = get_db_connection()
    
    try:
        with engine.connect() as conn:
            # حذف الجدول القديم إذا وجد (لضمان نظافة البيانات)
            print("🗑️ جاري حذف جدول customers القديم (إن وجد)...")
            conn.execute(text("DROP TABLE IF EXISTS customers CASCADE"))
            conn.commit()
            
            # إنشاء الجدول الجديد
            print("🛠️ جاري إنشاء جدول customers...")
            conn.execute(text("""
                CREATE TABLE customers (
                    id INTEGER PRIMARY KEY,
                    circle_id INTEGER,
                    arpu_6 FLOAT, arpu_7 FLOAT, arpu_8 FLOAT,
                    total_og_mou_6 FLOAT, total_og_mou_7 FLOAT, total_og_mou_8 FLOAT,
                    total_ic_mou_6 FLOAT, total_ic_mou_7 FLOAT, total_ic_mou_8 FLOAT,
                    total_rech_amt_6 FLOAT, total_rech_amt_7 FLOAT, total_rech_amt_8 FLOAT,
                    total_rech_num_6 INTEGER, total_rech_num_7 INTEGER, total_rech_num_8 INTEGER,
                    aon INTEGER,
                    vol_3g_mb_6 FLOAT, vol_3g_mb_7 FLOAT, vol_3g_mb_8 FLOAT
                )
            """))
            conn.commit()
            
            # 6. استيراد البيانات
            print("⬇️ جاري استيراد البيانات إلى PostgreSQL...")
            # نستخدم chunksize لتجنب مشاكل الذاكرة مع 100 ألف سجل
            df.to_sql('customers', con=engine, if_exists='append', index=False, chunksize=10000)
            
            # 7. التحقق من النجاح
            result = conn.execute(text("SELECT COUNT(*) FROM customers"))
            count = result.scalar()
            print(f"✅ تم استيراد البيانات بنجاح! إجمالي السجلات: {count}")
            return True
            
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاستيراد: {e}")
        return False

def clear_clustering_results():
    """مسح نتائج التجميع القديمة قبل تشغيل ACO"""
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS clustering_results CASCADE"))
            conn.commit()
            print("🗑️ تم مسح جدول clustering_results بنجاح (تحضيراً لتشغيل ACO).")
    except Exception as e:
        print(f"⚠️ لم يتم مسح جدول clustering_results: {e}")

if __name__ == "__main__":
    # ✅ المسار الجديد لملف Excel
    DATA_FILE_PATH = r"E:\SVU\Graduation Project\telecom_churn_project\data\telecom_data.xlsx" 
    
    print("="*60)
    print("🚀 بدء عملية استيراد البيانات إلى قاعدة البيانات الجديدة")
    print("="*60)
    
    # استيراد بيانات العملاء
    import_data_to_db(DATA_FILE_PATH)
    
    # مسح نتائج التجميع القديمة (تحضيراً لتشغيل ACO لاحقاً)
    clear_clustering_results()
    
    print("="*60)
    print("🎉 اكتملت عملية الاستيراد!")
    print("="*60)