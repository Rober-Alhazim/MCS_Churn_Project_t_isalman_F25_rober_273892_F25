# streamlit_app/pages/4_AI_Assistant.py
import streamlit as st
import pandas as pd
import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# استيراد الأنماط الموحدة
from utils.styles import inject_styles

from utils.db_connector import (
    ask_groq_assistant,  # ← تغيير الاسم
    get_customer_full_context,
    ask_about_general_insights,
    get_total_customers,
    get_avg_arpu,
    get_high_risk_count,
    get_avg_aon,
    get_revenue_at_risk,
    test_connection
)

# إعداد الصفحة
st.set_page_config(
    page_title="المساعد الذكي",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# حقن الأنماط الموحدة
inject_styles()

# ============================================
# التحقق من الاتصال بقاعدة البيانات
# ============================================
if not test_connection():
    st.error("❌ لا يمكن الاتصال بقاعدة البيانات. يرجى التأكد من تشغيل PostgreSQL.")
    st.stop()


# ============================================
# العنوان الرئيسي
# ============================================
st.title(" المساعد الذكي لتحليل المخاطر")
st.markdown("---")

# ============================================
# تهيئة Session State
# ============================================
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_customer_id' not in st.session_state:
    st.session_state.current_customer_id = None

# ============================================
# التحقق من وجود سياق حملة من صفحة Retention
# ============================================
if 'campaign_context' in st.session_state:
    ctx = st.session_state['campaign_context']
    st.info(f"""
    🔗 **تم استلام سياق من حملة الاحتفاظ:**
    - **العميل:** {ctx.get('customer_id', 'غير محدد')}
    - **مستوى الخطر:** {ctx.get('risk_level', 'غير محدد')}
    - **درجة الخطر:** {ctx.get('risk_score', 0):.1f}
    - **العرض المقترح:** {ctx.get('offer_text', 'لا يوجد')}
    """)
    
    # تعيين العميل الحالي تلقائياً
    if ctx.get('customer_id'):
        st.session_state.current_customer_id = ctx['customer_id']
    
    # إضافة رسالة ترحيبية في المحادثة إذا كانت فارغة
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"مرحباً! لقد استلمت سياق الحملة للعميل رقم **{ctx.get('customer_id')}**. كيف يمكنني مساعدتك في تحليل هذا العرض أو اقتراح تحسينات؟"
        })

# ============================================
# الشريط الجانبي (Sidebar)
# ============================================
with st.sidebar:
    st.markdown("### 🎯 خيارات المساعد")
    
    # إدخال رقم العميل
    customer_id = st.number_input(
        "🔍 رقم العميل (اختياري)",
        min_value=0,
        value=int(st.session_state.current_customer_id) if st.session_state.current_customer_id else 0,
        help="أدخل رقم العميل للحصول على تحليل مخصص"
    )
    
    if customer_id > 0:
        st.session_state.current_customer_id = customer_id
        st.success(f"✅ تم تحديد العميل رقم {customer_id}")
        
        # عرض ملخص سريع عن العميل
        with st.spinner("🔄 جاري تحميل البيانات..."):
            try:
                # جلب بيانات العميل من قاعدة البيانات
                from sqlalchemy import text
                from database.db_config import get_db_connection
                
                engine = get_db_connection()
                query = f"""
                    SELECT 
                        c.id, c.arpu_8, c.aon,
                        cr.risk_score, cr.risk_level, cr.cluster_id
                    FROM customers c
                    LEFT JOIN clustering_results cr ON c.id = cr.id
                    WHERE c.id = {customer_id}
                """
                df = pd.read_sql(query, engine)
                
                if not df.empty:
                    row = df.iloc[0]
                    st.markdown("---")
                    st.markdown("### 📊 ملخص سريع")
                    st.metric("درجة الخطورة", f"{row['risk_score']:.1f}/100" if pd.notnull(row['risk_score']) else "N/A")
                    st.metric("مستوى الخطر", row['risk_level'] if pd.notnull(row['risk_level']) else "N/A")
                    st.metric("ARPU الحالي", f"{row['arpu_8']:.2f}" if pd.notnull(row['arpu_8']) else "N/A")
                    st.metric("مدة العضوية", f"{row['aon']:.0f} يوم" if pd.notnull(row['aon']) else "N/A")
                    
                    # تحذير إذا كان العميل خطر
                    if row['risk_level'] == 'High Risk':
                        st.error("️ هذا العميل معرض للمغادرة!")
                    elif row['risk_level'] == 'Medium Risk':
                        st.warning("⚠️ هذا العميل يحتاج مراقبة.")
                    else:
                        st.success("✅ هذا العميل آمن.")
                else:
                    st.warning(f"⚠️ لم يتم العثور على عميل رقم {customer_id}")
            except Exception as e:
                st.error(f"❌ خطأ في جلب بيانات العميل: {e}")
    else:
        st.session_state.current_customer_id = None
        st.info("📌 وضع الأسئلة العامة")
    
    st.markdown("---")
    st.markdown("###  أمثلة على الأسئلة:")
    
    if st.session_state.current_customer_id:
        st.markdown("""
        **أسئلة عن العميل:**
        - ما هي حالة هذا العميل؟
        - لماذا هذا العميل معرض للمغادرة؟
        - كيف أتواصل مع هذا العميل؟
        - ما هي البدائل الأخرى؟
        """)
    else:
        st.markdown("""
        **أسئلة عامة:**
        - ما هي حالة قاعدة العملاء؟
        - ما هي أكثر أسباب المغادرة شيوعاً؟
        - كيف يمكن تحسين الحملة؟
        - اقترح خطة للعملاء متوسطي الخطورة
        """)
    
    st.markdown("---")
    
    # زر مسح المحادثة
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================
# عرض المحادثة
# ============================================
st.markdown("### 💬 المحادثة")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================
# معالجة إدخال المستخدم
# ============================================
if prompt := st.chat_input("اكتب سؤالك هنا..."):
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # معالجة السؤال
    with st.chat_message("assistant"):
        with st.spinner("🤖 جاري التحليل..."):
            try:
                # جلب بيانات العميل إذا موجود
                customer_data = None
                if st.session_state.current_customer_id:
                    customer_data = get_customer_full_context(st.session_state.current_customer_id)
                
                # ✅ إرسال السؤال لـ Groq
                if customer_data:
                    response = ask_groq_assistant(prompt, customer_data)
                else:
                    response = ask_about_general_insights(prompt)
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ حدث خطأ أثناء التحليل: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ============================================
# معلومات عن المساعد (أسفل الصفحة)
# ============================================

with st.expander("ℹ️ دليل استخدام المساعد الذكي (كيف يستجيب لطلباتك؟)", expanded=True):
    st.markdown("""
    ### 👋 مرحباً بك في مساعدك الرقمي الذكي
    تم تصميم هذا المساعد ليكون مستشارك الشخصي في فهم العملاء ومساعدتك على إقناعهم بالبقاء في الشركة، عبر تزويدك بتحليلات فورية مبنية على أرقام حقيقية.

    ### 🛠️ كيف تستفيد من المساعد في عملك اليومي؟
    * **🔍 تشخيص حالة العميل فوراً:** عند اختيارك لعميل معين، لا داعي لقراءة الجداول المعقدة؛ فقط اسأل المساعد وسيشرح لك بلغة بسيطة سبب تراجع استهلاكه ومستوى خطورة مغادرته.
    * **💡 حلول واقتراحات جاهزة:** يقدم لك المساعد نصائح عملية وعروضاً مخصصة (مثل خصومات، أو باقات إنترنت مجانية) لتقديمها للعميل أثناء المكالمة لإقناعه بعدم إلغاء الخط.
    * **📊 تقارير سريعة لمديرك:** يمكنك سؤاله عن إحصائيات عامة (مثل: "كم عدد العملاء المعرضين للخطر هذا الشهر؟" أو "ما هي الخسائر المالية المتوقعة؟") ليعطيك ملخصاً جاهزاً للنسخ خلال ثوانٍ.

    ### 🛡️ ضمان استمرارية العمل والأمان:
    * **⚡ سرعة فائقة:** يعمل المساعد بنظام معالجة فوري ليمنحك الإجابة خلال أجزاء من الثانية دون تضييع وقت العميل على الهاتف.
    * **🔋 لا يتوقف أبداً:** يحتوي النظام على خطة بديلة ذكية؛ حتى لو ضعفت شبكة الإنترنت أو حدثت صيانة في الخوادم، سيستمر المساعد في قراءة بياناتك الحية وإعطائك الحلول التشغيلية المناسبة.
    * **🔒 خصوصية تامة:** جميع بيانات العملاء وأرقامهم مشفرة ومحمية محلياً، ولا تخرج لأي أطراف خارجية.
    """)
