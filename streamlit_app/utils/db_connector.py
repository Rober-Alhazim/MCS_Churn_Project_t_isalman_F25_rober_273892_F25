# streamlit_app/utils/db_connector.py
"""
دوال الاتصال بقاعدة البيانات و KPIs ذات المعنى
مرتبطة مباشرة بنتائج خوارزمية ACO
"""

import streamlit as st
import pandas as pd
from sqlalchemy import text
import os
import sys
from dotenv import load_dotenv

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# الاستيراد الصحيح
from database.db_config import get_db_connection

load_dotenv()


# ============================================
# 🔌 دوال الاتصال الأساسية
# ============================================

def get_db_engine():
    """الحصول على محرك قاعدة البيانات (للتوافق مع الكود القديم)"""
    return get_db_connection()


def test_connection() -> bool:
    """اختبار الاتصال بقاعدة البيانات"""
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        st.error(f"فشل الاتصال بقاعدة البيانات: {e}")
        return False


# ============================================
# 📊 KPIs الأساسية
# ============================================

@st.cache_data(ttl=300)
def get_total_customers() -> int:
    """إجمالي عدد العملاء"""
    try:
        engine = get_db_connection()
        query = "SELECT COUNT(*) FROM customers"
        df = pd.read_sql(query, engine)
        return int(df.iloc[0, 0]) if not df.empty else 0
    except Exception as e:
        st.error(f"خطأ في جلب عدد العملاء: {e}")
        return 0


@st.cache_data(ttl=300)
def get_avg_arpu() -> float:
    """متوسط ARPU"""
    try:
        engine = get_db_connection()
        query = "SELECT AVG(arpu_8) FROM customers"
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب متوسط ARPU: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_avg_aon() -> float:
    """متوسط عمر العميل على الشبكة"""
    try:
        engine = get_db_connection()
        query = "SELECT AVG(aon) FROM customers"
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب متوسط AON: {e}")
        return 0.0


# ============================================
# ️ دوال توزيع المخاطرة
# ============================================

@st.cache_data(ttl=300)
def get_risk_distribution() -> dict:
    """توزيع مستويات المخاطرة"""
    try:
        engine = get_db_connection()
        query = """
            SELECT 
                risk_level,
                COUNT(*) as count
            FROM clustering_results
            GROUP BY risk_level
        """
        df = pd.read_sql(query, engine)
        return dict(zip(df['risk_level'], df['count']))
    except Exception as e:
        st.error(f"خطأ في جلب توزيع المخاطرة: {e}")
        return {}


@st.cache_data(ttl=300)
def get_high_risk_count() -> int:
    """عدد العملاء عاليي المخاطرة"""
    try:
        engine = get_db_connection()
        query = "SELECT COUNT(*) FROM clustering_results WHERE risk_level = 'High Risk'"
        df = pd.read_sql(query, engine)
        return int(df.iloc[0, 0]) if not df.empty else 0
    except Exception as e:
        st.error(f"خطأ في جلب عدد العملاء عاليي المخاطرة: {e}")
        return 0


@st.cache_data(ttl=300)
def get_medium_risk_count() -> int:
    """عدد العملاء متوسطي المخاطرة"""
    try:
        engine = get_db_connection()
        query = "SELECT COUNT(*) FROM clustering_results WHERE risk_level = 'Medium Risk'"
        df = pd.read_sql(query, engine)
        return int(df.iloc[0, 0]) if not df.empty else 0
    except Exception as e:
        st.error(f"خطأ في جلب عدد العملاء متوسطي المخاطرة: {e}")
        return 0


@st.cache_data(ttl=300)
def get_low_risk_count() -> int:
    """عدد العملاء منخفضي المخاطرة"""
    try:
        engine = get_db_connection()
        query = "SELECT COUNT(*) FROM clustering_results WHERE risk_level = 'Low Risk'"
        df = pd.read_sql(query, engine)
        return int(df.iloc[0, 0]) if not df.empty else 0
    except Exception as e:
        st.error(f"خطأ في جلب عدد العملاء منخفضي المخاطرة: {e}")
        return 0


# ============================================
# 💰 دوال مالية متقدمة
# ============================================

@st.cache_data(ttl=300)
def get_revenue_at_risk() -> float:
    """الإيرادات المعرضة للخطر (عملاء High Risk)"""
    try:
        engine = get_db_connection()
        query = """
            SELECT SUM(c.arpu_8) as total_revenue_at_risk
            FROM clustering_results cr
            JOIN customers c ON cr.id = c.id
            WHERE cr.risk_level = 'High Risk'
        """
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب الإيرادات المعرضة للخطر: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_avg_risk_score(risk_level: str = None) -> float:
    """
    حساب متوسط درجة الخطورة
    :param risk_level: مستوى الخطورة (High Risk, Medium Risk, Low Risk)
    :return: متوسط درجة الخطورة
    """
    try:
        engine = get_db_connection()
        if risk_level:
            query = f"""
                SELECT AVG(risk_score) 
                FROM clustering_results 
                WHERE risk_level = '{risk_level}'
            """
        else:
            query = "SELECT AVG(risk_score) FROM clustering_results"
        
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب متوسط درجة الخطورة: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_critical_accounts(threshold: int = 85) -> int:
    """عدد الحسابات الحرجة جداً (درجة خطر > threshold)"""
    try:
        engine = get_db_connection()
        query = f"SELECT COUNT(*) FROM clustering_results WHERE risk_score > {threshold}"
        df = pd.read_sql(query, engine)
        return int(df.iloc[0, 0]) if not df.empty else 0
    except Exception as e:
        st.error(f"خطأ في جلب عدد الحسابات الحرجة: {e}")
        return 0


@st.cache_data(ttl=300)
def get_rescue_potential() -> float:
    """نسبة الإنقاذ المحتملة (عملاء Medium Risk قابلين للإنقاذ)"""
    try:
        engine = get_db_connection()
        query = """
            SELECT 
                COUNT(CASE WHEN risk_level = 'Medium Risk' AND risk_score < 60 THEN 1 END) as rescuable,
                COUNT(*) as total
            FROM clustering_results
        """
        df = pd.read_sql(query, engine)
        if not df.empty and df.iloc[0, 1] > 0:
            return (df.iloc[0, 0] / df.iloc[0, 1]) * 100
        return 0.0
    except Exception as e:
        st.error(f"خطأ في حساب نسبة الإنقاذ: {e}")
        return 0.0


# ============================================
# 📉 دوال مؤشرات التراجع
# ============================================

@st.cache_data(ttl=300)
def get_arpu_decline_rate() -> float:
    """معدل تراجع ARPU من شهر 6 إلى 8"""
    try:
        engine = get_db_connection()
        query = """
            SELECT 
                (AVG(arpu_8) - AVG(arpu_6)) / NULLIF(AVG(arpu_6), 0) * 100 as decline_rate
            FROM customers
        """
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب معدل تراجع ARPU: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_avg_risk_age() -> float:
    """متوسط عمر العملاء الخطرين (High Risk)"""
    try:
        engine = get_db_connection()
        query = """
            SELECT AVG(c.aon)
            FROM clustering_results cr
            JOIN customers c ON cr.id = c.id
            WHERE cr.risk_level = 'High Risk'
        """
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب متوسط عمر العملاء الخطرين: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_daily_call_loss() -> float:
    """فقدان المكالمات اليومي (متوسط MOU للعملاء High Risk)"""
    try:
        engine = get_db_connection()
        query = """
            SELECT AVG(c.total_og_mou_8)
            FROM clustering_results cr
            JOIN customers c ON cr.id = c.id
            WHERE cr.risk_level = 'High Risk'
        """
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب فقدان المكالمات: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_recharge_loss() -> float:
    """انخفاض الشحنات (متوسط Recharge للعملاء High Risk)"""
    try:
        engine = get_db_connection()
        query = """
            SELECT AVG(c.total_rech_amt_8)
            FROM clustering_results cr
            JOIN customers c ON cr.id = c.id
            WHERE cr.risk_level = 'High Risk'
        """
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب انخفاض الشحنات: {e}")
        return 0.0


# ============================================
# 📈 دوال المؤشرات
# ============================================

@st.cache_data(ttl=300)
def get_arpu_trend() -> pd.DataFrame:
    """اتجاه ARPU عبر الأشهر"""
    try:
        engine = get_db_connection()
        query = """
            SELECT 
                AVG(arpu_6) as arpu_6,
                AVG(arpu_7) as arpu_7,
                AVG(arpu_8) as arpu_8
            FROM customers
        """
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"خطأ في جلب اتجاه ARPU: {e}")
        return pd.DataFrame()


# ============================================
# 👥 دوال العملاء
# ============================================

@st.cache_data(ttl=300)
def get_high_risk_customers(limit: int = 20) -> pd.DataFrame:
    """أعلى العملاء خطورة"""
    try:
        engine = get_db_connection()
        query = f"""
            SELECT 
                c.id,
                cr.risk_score,
                cr.risk_level,
                c.arpu_8,
                cr.arpu_decline,
                cr.mou_decline,
                cr.rech_decline
            FROM clustering_results cr
            JOIN customers c ON cr.id = c.id
            WHERE cr.risk_level = 'High Risk'
            ORDER BY cr.risk_score DESC
            LIMIT {limit}
        """
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"خطأ في جلب أعلى العملاء خطورة: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_customers_preview(limit: int = 100) -> pd.DataFrame:
    """معاينة العملاء"""
    try:
        engine = get_db_connection()
        query = f"SELECT * FROM customers LIMIT {limit}"
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"خطأ في جلب معاينة العملاء: {e}")
        return pd.DataFrame()


# ============================================
# 💰 دوال KPIs المالية والتشغيلية
# ============================================

@st.cache_data(ttl=300)
def get_monthly_recurring_revenue() -> float:
    """الإيرادات الشهرية المتكررة (MRR)"""
    try:
        engine = get_db_connection()
        query = "SELECT SUM(arpu_8) as mrr FROM customers"
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب MRR: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_mom_growth_rate() -> float:
    """معدل النمو الشهري (Month-over-Month)"""
    try:
        engine = get_db_connection()
        query = """
            SELECT 
                ((AVG(arpu_8) - AVG(arpu_7)) / NULLIF(AVG(arpu_7), 0)) * 100 as growth_rate
            FROM customers
        """
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب معدل النمو الشهري: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_active_customers_rate() -> float:
    """نسبة العملاء النشطين"""
    try:
        engine = get_db_connection()
        query = """
            SELECT 
                COUNT(CASE WHEN total_og_mou_8 > 0 OR vol_3g_mb_8 > 0 THEN 1 END) * 100.0 / COUNT(*) as active_rate
            FROM customers
        """
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب نسبة العملاء النشطين: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_avg_data_usage() -> float:
    """متوسط استهلاك البيانات"""
    try:
        engine = get_db_connection()
        query = "SELECT AVG(vol_3g_mb_8) as avg_data FROM customers"
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب متوسط استهلاك البيانات: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_avg_daily_mou() -> float:
    """متوسط المكالمات اليومية"""
    try:
        engine = get_db_connection()
        query = "SELECT AVG(total_og_mou_8) / 30.0 as avg_daily_mou FROM customers"
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب متوسط المكالمات اليومية: {e}")
        return 0.0


@st.cache_data(ttl=300)
def get_avg_transaction_value() -> float:
    """متوسط قيمة الشحنة (ATV)"""
    try:
        engine = get_db_connection()
        query = """
            SELECT 
                AVG(total_rech_amt_8) / NULLIF(AVG(total_rech_num_8), 0) as atv
            FROM customers
        """
        df = pd.read_sql(query, engine)
        return float(df.iloc[0, 0]) if not df.empty and df.iloc[0, 0] else 0.0
    except Exception as e:
        st.error(f"خطأ في حساب متوسط قيمة الشحنة: {e}")
        return 0.0


# ============================================
# 🎯 دوال التوصيات الذكية
# ============================================

@st.cache_data(ttl=300)
def get_smart_recommendations() -> pd.DataFrame:
    """جلب التوصيات الذكية للعملاء عاليي ومتوسطي الخطورة"""
    try:
        engine = get_db_connection()
        query = """
            SELECT 
                c.id,
                c.arpu_6, c.arpu_7, c.arpu_8,
                c.total_og_mou_6, c.total_og_mou_7, c.total_og_mou_8,
                c.vol_3g_mb_6, c.vol_3g_mb_7, c.vol_3g_mb_8,
                c.total_rech_amt_6, c.total_rech_amt_7, c.total_rech_amt_8,
                c.aon,
                cr.risk_score,
                cr.risk_level,
                cr.arpu_decline,
                cr.mou_decline,
                cr.rech_decline,
                (c.vol_3g_mb_6 - c.vol_3g_mb_8) / NULLIF(c.vol_3g_mb_6, 0) * 100 as data_decline
            FROM clustering_results cr
            JOIN customers c ON cr.id = c.id
            WHERE cr.risk_level IN ('High Risk', 'Medium Risk')
            ORDER BY cr.risk_score DESC
        """
        df = pd.read_sql(query, engine)
        
        # إضافة ملخص التراجع
        if not df.empty:
            decline_summaries = []
            for _, row in df.iterrows():
                declines = []
                if row.get('data_decline', 0) > 30:
                    declines.append(f"بيانات {row['data_decline']:.0f}%")
                if row.get('mou_decline', 0) > 30:
                    declines.append(f"مكالمات {row['mou_decline']:.0f}%")
                if row.get('rech_decline', 0) > 30:
                    declines.append(f"شحن {row['rech_decline']:.0f}%")
                
                if declines:
                    decline_summaries.append(f"📉 تراجع في: {', '.join(declines)}")
                else:
                    decline_summaries.append("📉 تراجع عام")
            
            df['decline_summary'] = decline_summaries
        
        return df
    except Exception as e:
        st.error(f"خطأ في جلب التوصيات الذكية: {e}")
        return pd.DataFrame()


# ============================================
# 🤖 دوال المساعد الذكي (Groq - Llama 3.1 70B)
# ============================================

from groq import Groq

@st.cache_resource
def get_groq_client():
    """تهيئة عميل Groq"""
    try:
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            st.warning("️ لم يتم تعيين GROQ_API_KEY في ملف .env")
            return None
        
        client = Groq(api_key=api_key)
        return client
    except Exception as e:
        st.error(f" خطأ في تهيئة Groq: {e}")
        return None


def get_customer_full_context(customer_id: int) -> dict:
    """الحصول على سياق كامل للعميل كقاموس"""
    try:
        engine = get_db_connection()
        query = f"""
            SELECT 
                c.id,
                c.arpu_6, c.arpu_7, c.arpu_8,
                c.total_og_mou_6, c.total_og_mou_7, c.total_og_mou_8,
                c.total_ic_mou_6, c.total_ic_mou_7, c.total_ic_mou_8,
                c.total_rech_amt_6, c.total_rech_amt_7, c.total_rech_amt_8,
                c.total_rech_num_6, c.total_rech_num_7, c.total_rech_num_8,
                c.aon, c.vol_3g_mb_6, c.vol_3g_mb_7, c.vol_3g_mb_8,
                cr.cluster_id,
                cr.risk_score,
                cr.risk_level,
                cr.arpu_decline,
                cr.mou_decline,
                cr.rech_decline
            FROM customers c
            LEFT JOIN clustering_results cr ON c.id = cr.id
            WHERE c.id = {customer_id}
        """
        df = pd.read_sql(query, engine)
        if df.empty:
            return None
        return df.iloc[0].to_dict()
    except Exception as e:
        st.error(f"خطأ في جلب سياق العميل: {e}")
        return None


def ask_groq_assistant(question: str, customer_data: dict = None) -> str:
    """إرسال سؤال لـ Groq مع سياق العميل، ونظام رد احتياطي في حال الفشل"""
    client = get_groq_client()
    
    # 1. إذا كان Groq متوفر، نقوم بالاستعلام منه
    if client:
        system_prompt = """أنت مساعد ذكي متخصص في تحليل مخاطر مغادرة العملاء في قطاع الاتصالات.
مهمتك: تحليل حالة العميل، شرح التوصيات، وتقديم نصائح عملية لموظف خدمة العملاء."""

        customer_context = ""
        if customer_data:
            customer_context = f"""
بيانات العميل الحالي:
• رقم العميل: {customer_data.get('id')}
• درجة الخطورة: {customer_data.get('risk_score', 0):.1f}/100
• مستوى الخطر: {customer_data.get('risk_level', 'غير محدد')}
• مدة العضوية: {customer_data.get('aon', 0):.0f} يوم
📊 المؤشرات:
• ARPU الحالي: {customer_data.get('arpu_8', 0):.2f} | السابق: {customer_data.get('arpu_6', 0):.2f}
• المكالمات الصادرة دقيقة: {customer_data.get('total_og_mou_8', 0):.0f} | السابق: {customer_data.get('total_og_mou_6', 0):.0f}
• الشحن الحالي: {customer_data.get('total_rech_amt_8', 0):.0f} | السابق: {customer_data.get('total_rech_amt_6', 0):.0f}
---"""

        full_prompt = f"{system_prompt}\n\n{customer_context}\n\nسؤال المستخدم: {question}"

        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": full_prompt}],
                model="openai/gpt-oss-120b",  # 💡 تم التحديث للنموذج البديل الشغال حالياً
                temperature=0.7,
                max_tokens=1024
            )
            # صياغة جلب النص الصحيحة في بايثون
            return response.choices[0].message.content 
        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            pass


    # 2. 🛡️ نظام الخبراء الاحتياطي المدمج (يعمل محلياً بدون إنترنت)
    if customer_data:
        risk = customer_data.get('risk_level', 'غير محدد')
        score = customer_data.get('risk_score', 0)
        arpu_drop = customer_data.get('arpu_decline', 0)
        mou_drop = customer_data.get('mou_decline', 0)
        
        reply = f"### 🤖 تحليل نظام الخبراء الاحتياطي (وضع العمل المحلي):\n\n"
        reply += f"تم تحليل حالة العميل رقم **{customer_data.get('id')}** بنجاح:\n"
        reply += f"- **مستوى المخورة:** {risk} (الدرجة: {score:.1f}/100)\n\n"
        
        reply += "📊 **الأسباب التشخيصية:**\n"
        if arpu_drop > 20 or mou_drop > 20:
            reply += f"  - يوجد تراجع واضح في مؤشرات العميل: معدل انخفاض العوائد {arpu_drop:.1f}% ومعدل انخفاض المكالمات {mou_drop:.1f}%.\n"
        if risk == 'High Risk':
            reply += "  - سلوك العميل يظهر نمط انسحاب حاد يتطلب تدخلاً فورياً لحماية الحساب.\n"
        else:
            reply += "  - مؤشرات العميل مستقرة نسبياً ولكن تحتاج لمراقبة دورية.\n"
            
        reply += "\n💡 **الإجراءات الموصى بها للموظف:**\n"
        if risk == 'High Risk':
            reply += "  1. التواصل مع العميل خلال 24 ساعة عبر الهاتف.\n  2. تقديم عرض مخصص يتضمن خصومات على المكالمات أو باقات إنترنت مجانية تعوض هذا النقص.\n"
        else:
            reply += "  1. إرسال استبيان رضا قصير عبر الرسائل النصية.\n  2. إدراج العميل في قائمة المتابعة الشهرية.\n"
        return reply
        
    return "عذراً، لم نتمكن من الاتصال بالخادم ولم يتوفر سياق كافٍ للنظام الاحتياطي."



def ask_about_general_insights(question: str) -> str:
    """الإجابة على أسئلة عامة عن قاعدة العملاء مع نظام رد احتياطي"""
    insights = {
        'total_customers': get_total_customers(),
        'high_risk': get_high_risk_count(),
        'medium_risk': get_medium_risk_count(),
        'low_risk': get_low_risk_count(),
        'avg_arpu': get_avg_arpu(),
        'revenue_at_risk': get_revenue_at_risk(),
        'critical_accounts': get_critical_accounts(85)
    }
    
    total = insights['total_customers']
    high_pct = (insights['high_risk'] / total * 100) if total > 0 else 0
    med_pct = (insights['medium_risk'] / total * 100) if total > 0 else 0
    
    context = f"""إحصائيات قاعدة العملاء:
• إجمالي العملاء: {insights['total_customers']:,}
• عاليي الخطورة: {insights['high_risk']:,} ({high_pct:.1f}%)
• متوسطي الخطورة: {insights['medium_risk']:,} ({med_pct:.1f}%)
• متوسط ARPU: {insights['avg_arpu']:.2f}
• الإيرادات المعرضة للخطر: {insights['revenue_at_risk']:,.0f}"""

    client = get_groq_client()
    if client:
        full_prompt = f"أنت مساعد ذكي لتحليل بيانات العملاء.\n\n{context}\n\nالسؤال: {question}"
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": full_prompt}],
                model="openai/gpt-oss-120b",  # 💡 تم التحديث هنا أيضاً
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API General Insights Error: {str(e)}")
            pass



    # 🛡️ الرد الاحتياطي التلقائي المبني على الأرقام الحقيقية لقاعدة البيانات
    fallback_reply = f"### 📊 ملخص لوحة البيانات التشغيلية (الرد المدمج):\n\n"
    fallback_reply += f"بناءً على طلبك الإحصائي، إليك التقرير المباشر المستخرج من قاعدة البيانات:\n"
    fallback_reply += f"- **حجم قاعدة البيانات:** نتابع حالياً إجمالي **{insights['total_customers']:,}** عميل نشط.\n"
    fallback_reply += f"- **مستوى الخطر:** لدينا **{insights['high_risk']:,}** عميل بمستوى خطورة مرتفع، مما يمثل تهديداً مالياً بقيمة **{insights['revenue_at_risk']:,.2f}** كإيرادات معرضة للفقد الفوري.\n"
    fallback_reply += f"- **الحسابات الحرجة جداً:** تم رصد **{insights['critical_accounts']:,}** حساب تجاوزت درجة خطورتهم السلوكية 85/100 ويجب التعامل معهم كأولوية قصوى.\n\n"
    fallback_reply += "💡 **توصية تشغيلية:** نقترح توجيه حملة الاحتفاظ (Retention Campaign) القادمة للتركيز الفوري على الشريحة عالية الخطورة لتقليل الهدر المالي."
    return fallback_reply
