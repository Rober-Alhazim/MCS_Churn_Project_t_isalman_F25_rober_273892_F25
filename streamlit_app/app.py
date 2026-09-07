# streamlit_app/app.py
import streamlit as st
import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# استيراد الأنماط الموحدة
from utils.styles import inject_styles

# استيراد دوال قاعدة البيانات
from utils.db_connector import (
    get_total_customers,
    get_avg_arpu,
    get_high_risk_count,
    get_avg_aon,
    get_risk_distribution,
    get_revenue_at_risk,
    test_connection
)

# إعداد الصفحة
st.set_page_config(
    page_title="منظومة دعم قرار الاتصالات",
    page_icon="",
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
st.title("📱 منظومة دعم قرار ذكية للتنبؤ بمغادرة العملاء")
st.markdown("---")

# ============================================
# KPIs الرئيسية (4 مؤشرات ذات معنى)
# ============================================
st.subheader("📊 المؤشرات الرئيسية")

# جلب البيانات
total_customers = get_total_customers()
avg_arpu = get_avg_arpu()
high_risk_count = get_high_risk_count()
avg_aon = get_avg_aon()
revenue_at_risk = get_revenue_at_risk()

# حساب النسب
risk_distribution = get_risk_distribution()
high_risk_pct = (high_risk_count / total_customers * 100) if total_customers > 0 else 0

# عرض الـ KPIs في 4 أعمدة
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 إجمالي العملاء",
        value=f"{total_customers:,}",
        help="إجمالي عدد العملاء في قاعدة البيانات"
    )

with col2:
    st.metric(
        label="⚠️ العملاء عاليي الخطورة",
        value=f"{high_risk_count:,}",
        delta=f"{high_risk_pct:.1f}% من الإجمالي",
        delta_color="inverse",
        help="عدد العملاء المعرضين للتسرب (High Risk)"
    )

with col3:
    st.metric(
        label="💰 متوسط ARPU",
        value=f"{avg_arpu:.2f}",
        help="متوسط الإيرادات الشهرية لكل مستخدم (الشهر 8)"
    )

with col4:
    st.metric(
        label="📅 متوسط عمر العميل",
        value=f"{avg_aon:.0f} يوم",
        help="متوسط مدة بقاء العميل على الشبكة"
    )

st.markdown("---")

# ============================================
# معلومات إضافية (توزيع المخاطرة + الإيرادات المعرضة للخطر)
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 توزيع مستويات المخاطرة")
    
    if risk_distribution:
        # رسم بياني بسيط للتوزيع
        import plotly.graph_objects as go
        
        labels = list(risk_distribution.keys())
        values = list(risk_distribution.values())
        
        colors = ['#ff4d4d', '#ffd700', '#00d4ff']  # أحمر، أصفر، أزرق
        
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors,
                textinfo='label+percent',
                textfont_size=14,
                hole=0.4
            )
        ])
        
        fig.update_layout(
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8f1f5')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("️ لا توجد بيانات عن توزيع المخاطرة. يرجى تشغيل محرك ACO أولاً.")

with col2:
    st.subheader("💸 الإيرادات المعرضة للخطر")
    
    # حساب الإيرادات الشهرية الكلية
    total_revenue = total_customers * avg_arpu
    revenue_at_risk_pct = (revenue_at_risk / total_revenue * 100) if total_revenue > 0 else 0
    
    st.markdown(f"""
    ### 📈 ملخص الإيرادات
    
    | المؤشر | القيمة |
    |--------|--------|
    | **الإيرادات الشهرية الكلية** | {total_revenue:,.0f} |
    | **الإيرادات المعرضة للخطر** | {revenue_at_risk:,.0f} |
    | **نسبة الخطر** | {revenue_at_risk_pct:.1f}% |
    
    > 💡 **تفسير:** إذا فقدنا جميع العملاء عاليي الخطورة، سنخسر حوالي **{revenue_at_risk:,.0f}** شهرياً.
    """)

st.markdown("---")

# ============================================
# معلومات عن النظام
# ============================================
st.subheader("ℹ️ معلومات عن النظام")

with st.expander("📋 تفاصيل النظام والبيانات", expanded=False):
    st.markdown(f"""
    ### 🎯 الهدف من النظام
    هذا النظام يساعدك في:
    - ✅ **تحليل سلوك العملاء** وتحديد أنماط الاستخدام بدقة هندسية متطورة
    - ✅ **التنبؤ بالعملاء المهددين بالمغادرة** بالاعتماد على خوارزمية التجميع العنقودي الموجهة بالفيرومون (ACO Clustering)
    - ✅ **محاكاة ديناميكية للمخاطر** وضبط أوزان خطورة المجموعات بناءً على قرارات الإدارة
    - ✅ **اقتراح عروض وحملات مخصصة** وتصدير القوائم الجاهزة فوراً لفرق المبيعات وخدمة العملاء
    
    ###  حالة البيانات
    - **إجمالي العملاء:** {total_customers:,} مشترك
    - **متوسط ARPU:** {avg_arpu:.2f}
    - **العملاء عاليي الخطورة:** {high_risk_count:,} ({high_risk_pct:.1f}%)
    - **متوسط عمر العميل:** {avg_aon:.0f} يوم
    
    ###  الخوارزمية المستخدمة
    - **Ant Colony Optimization (ACO)** المطورة ذاتياً لحساب مسارات الفيرومون والقرب الهيكلي لمراكز التراجع العنقودي
    - **Cluster Profiling ديناميكي** لتحديد مستويات الخطورة بناءً على السلوك الفعلي للعملاء
    - **ML-based Offer Composer** لتقديم توصيات مخصصة لكل عميل
    
    ### 🔗 التنقل بين الصفحات
    استخدم القائمة الجانبية للتنقل بين الشاشات المختلفة:
    - 📊 **إدارة البيانات** - تشغيل محرك ACO ومعاينة البيانات
    - ️ **تحليل المخاطر** - استكشاف العملاء حسب مستوى الخطورة
    - 🎯 **حملات الحفاظ** - إنشاء حملات مخصصة وتصدير القوائم
    - 🤖 **المساعد الذكي** - طرح أسئلة وتحليلات ذكية
    """)

# ============================================
# زر الانتقال السريع للمساعد الذكي
# ============================================
st.markdown("---")
st.markdown("### 🚀 ابدأ الآن")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 تشغيل محرك ACO", use_container_width=True):
        st.switch_page("pages/1_Data_Management.py")

with col2:
    if st.button("⚠️ تحليل المخاطر", use_container_width=True):
        st.switch_page("pages/2_Risk_Analysis.py")

with col3:
    if st.button(" المساعد الذكي", use_container_width=True):
        st.switch_page("pages/4_AI_Assistant.py")
