# database/db_config.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

def get_db_connection() -> Engine:
    """إنشاء اتصال بقاعدة البيانات مع تحسينات الأداء"""
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'rober123')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'telecom_churn_db_v2')
    
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # تحسينات الأداء (Connection Pooling)
    engine = create_engine(
        db_url,
        pool_size=10,           # عدد الاتصالات النشطة
        max_overflow=20,        # الحد الأقصى للاتصالات الإضافية
        pool_timeout=30,        # وقت الانتظار للحصول على اتصال
        pool_recycle=1800,      # إعادة تدوير الاتصال كل 30 دقيقة
        echo=False              # اجعلها True إذا أردت رؤية استعلامات SQL في الكونسول
    )
    
    return engine

def test_connection() -> bool:
    """اختبار الاتصال بقاعدة البيانات"""
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ الاتصال بقاعدة البيانات ناجح!")
        return True
    except Exception as e:
        print(f"❌ فشل الاتصال بقاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print(" اختبار الاتصال بقاعدة البيانات")
    print("="*50)
    test_connection()