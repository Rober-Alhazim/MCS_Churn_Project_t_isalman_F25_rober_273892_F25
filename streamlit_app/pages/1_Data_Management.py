# streamlit_app/pages/1_Data_Management.py
import streamlit as st
import pandas as pd
import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# استيراد الأنماط الموحدة
from utils.styles import inject_styles

# استيراد دوال قاعدة البيانات
from utils.db_connector import (
    get_total_customers,
    get_avg_arpu,
    get_high_risk_count,
    get_avg_aon,
    get_customers_preview,
    get_risk_distribution,
    get_revenue_at_risk,
    get_arpu_trend,
    test_connection
)

# استيراد محرك ACO
try:
    from aco_engine.run_engine import run_aco_engine
    ACO_AVAILABLE = True
except ImportError:
    ACO_AVAILABLE = False

# إعداد الصفحة
st.set_page_config(
    page_title="إدارة البيانات",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# حقن الأنماط الموحدة
inject_styles()

# ============================================
# التحقق من الاتصال بقاعدة البيانات
# ============================================
# if not test_connection():
#     st.error("❌ لا يمكن الاتصال بقاعدة البيانات. يرجى التأكد من تشغيل PostgreSQL.")
#     st.stop()

# 💡 الكود الجديد والمعدل لضمان نجاح عمل السحابة مجاناً وبدون سيرفر
if not test_connection():
    st.warning("⚠️ وضع العمل السحابي نشط: لم يتم العثور على قاعدة بيانات محلية. سيتم تشغيل المنظومة بالاعتماد على الذاكرة الحية (Session State) بمجرد ضغط زر تشغيل محرك ACO في صفحة إدارة البيانات.")
    # حذفنا أمر st.stop() لكي يكمل السيرفر تحميل بقية عناصر الواجهة والأزرار بنجاح!


# ============================================
# العنوان الرئيسي
# ============================================
st.title("📁 إدارة البيانات ومحرك التجميع ACO")
st.markdown("---")

# ============================================
# إنشاء التبويبات الثلاثة
# ============================================
tab1, tab2, tab3 = st.tabs([
    "📊 معاينة البيانات",
    "📈 إحصائيات عامة",
    "⚙️ تشغيل محرك النمل (ACO)"
])

# ============================================
# التبويب 1: معاينة البيانات
# ============================================
with tab1:
    st.subheader("📊 معاينة بيانات العملاء")
    
    # جلب البيانات
    df_preview = get_customers_preview(limit=200)
    
    if not df_preview.empty:
        total_records = get_total_customers()
        st.info(f"📊 إجمالي السجلات في قاعدة البيانات: **{total_records:,}** عميل")
        
        # التحكم في عدد الصفوف المعروضة
        rows = st.slider("عدد الصفوف المعروضة", 10, 200, 50)
        
        # عرض الجدول
        st.dataframe(
            df_preview.head(rows),
            use_container_width=True,
            height=400
        )
        
        # الملخص الإحصائي
        with st.expander("📊 الملخص الإحصائي الشامل", expanded=False):
            st.markdown("إحصائيات وصفية لأهم المؤشرات المالية والاستخدامية:")
            
            # اختيار الأعمدة المهمة
            stats_cols = [
                'arpu_6', 'arpu_7', 'arpu_8',
                'total_og_mou_6', 'total_og_mou_7', 'total_og_mou_8',
                'total_rech_amt_6', 'total_rech_amt_7', 'total_rech_amt_8',
                'aon'
            ]
            
            available_stats_cols = [col for col in stats_cols if col in df_preview.columns]
            
            if available_stats_cols:
                summary_df = df_preview[available_stats_cols].describe().T
                summary_df.columns = ['العدد', 'المتوسط', 'الانحراف المعياري', 'الحد الأدنى', '25%', '50%', '75%', 'الحد الأقصى']
                
                # تسميات عربية للأعمدة
                col_labels = {
                    'arpu_6': '💰 ARPU - شهر 6',
                    'arpu_7': '💰 ARPU - شهر 7',
                    'arpu_8': '💰 ARPU - شهر 8',
                    'total_og_mou_6': '📞 دقائق صادرة - شهر 6',
                    'total_og_mou_7': ' دقائق صادرة - شهر 7',
                    'total_og_mou_8': '📞 دقائق صادرة - شهر 8',
                    'total_rech_amt_6': '💳 مبالغ الشحن - شهر 6',
                    'total_rech_amt_7': '💳 مبالغ الشحن - شهر 7',
                    'total_rech_amt_8': '💳 مبالغ الشحن - شهر 8',
                    'aon': '📅 عمر العميل (يوم)'
                }
                
                summary_df = summary_df.rename(index=col_labels)
                st.dataframe(summary_df.round(2), use_container_width=True)
            else:
                st.warning("⚠️ الأعمدة المطلوبة غير متوفرة في البيانات.")
    else:
        st.warning("️ لا توجد بيانات للعرض. يرجى التأكد من استيراد البيانات أولاً.")

# ============================================
# التبويب 2: إحصائيات عامة
# ============================================
with tab2:
    st.subheader("📈 المؤشرات الرئيسية")
    
    # جلب المؤشرات
    total_customers = get_total_customers()
    avg_arpu = get_avg_arpu()
    high_risk_count = get_high_risk_count()
    avg_aon = get_avg_aon()
    revenue_at_risk = get_revenue_at_risk()
    risk_distribution = get_risk_distribution()
    arpu_trend = get_arpu_trend()
    
    # عرض KPIs في 4 أعمدة
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
            delta=f"{(high_risk_count/total_customers*100) if total_customers > 0 else 0:.1f}% من الإجمالي",
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
    
    # صف ثاني: توزيع المخاطرة + الإيرادات المعرضة للخطر
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(" توزيع مستويات المخاطرة")
        
        if risk_distribution:
            import plotly.graph_objects as go
            
            labels = list(risk_distribution.keys())
            values = list(risk_distribution.values())
            colors = ['#ff4d4d', '#ffd700', '#00d4ff']
            
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
            st.info("ℹ️ لا توجد بيانات عن توزيع المخاطرة. يرجى تشغيل محرك ACO أولاً.")
    
    with col2:
        st.subheader("💸 الإيرادات المعرضة للخطر")
        
        total_revenue = total_customers * avg_arpu
        revenue_at_risk_pct = (revenue_at_risk / total_revenue * 100) if total_revenue > 0 else 0
        
        st.markdown(f"""
        ###  ملخص الإيرادات
        
        | المؤشر | القيمة |
        |--------|--------|
        | **الإيرادات الشهرية الكلية** | {total_revenue:,.0f} |
        | **الإيرادات المعرضة للخطر** | {revenue_at_risk:,.0f} |
        | **نسبة الخطر** | {revenue_at_risk_pct:.1f}% |
        
        > 💡 **تفسير:** إذا فقدنا جميع العملاء عاليي الخطورة، سنخسر حوالي **{revenue_at_risk:,.0f}** شهرياً.
        """)
    
    st.markdown("---")
    
    # اتجاه ARPU
    st.subheader("📉 اتجاه ARPU عبر الأشهر")
    
    if not arpu_trend.empty:
        import plotly.graph_objects as go
        
        months = ['شهر 6', 'شهر 7', 'شهر 8']
        arpu_values = [
            arpu_trend['arpu_6'].iloc[0] if 'arpu_6' in arpu_trend.columns else 0,
            arpu_trend['arpu_7'].iloc[0] if 'arpu_7' in arpu_trend.columns else 0,
            arpu_trend['arpu_8'].iloc[0] if 'arpu_8' in arpu_trend.columns else 0
        ]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=months,
                y=arpu_values,
                mode='lines+markers',
                marker=dict(size=10, color='#00d4ff'),
                line=dict(color='#00ffb3', width=3)
            )
        ])
        
        fig.update_layout(
            height=300,
            xaxis_title='الشهر',
            yaxis_title='متوسط ARPU',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8f1f5')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ لا توجد بيانات عن اتجاه ARPU.")

# ============================================
# التبويب 3: تشغيل محرك ACO
# ============================================
with tab3:
    st.subheader("⚙️ تشغيل خوارزمية مستعمرة النمل (ACO)")
    
    if ACO_AVAILABLE:
        st.markdown("""
        ### 🐜 إعدادات الخوارزمية
        قم بضبط معاملات خوارزمية ACO قبل التشغيل:
        """)
        
        # إعدادات الخوارزمية
        col1, col2, col3 = st.columns(3)
        
        with col1:
            n_clusters = st.number_input(
                "🔢 عدد العناقيد",
                min_value=2,
                max_value=10,
                value=3,
                help="عدد المجموعات التي سيتم تقسيم العملاء إليها"
            )
        
        with col2:
            n_ants = st.number_input(
                "🐜 عدد النمل",
                min_value=5,
                max_value=50,
                value=15,
                help="عدد النمل المستكشف في كل تكرار"
            )
        
        with col3:
            max_iter = st.number_input(
                "🔄 عدد التكرارات",
                min_value=10,
                max_value=100,
                value=30,
                help="الحد الأقصى لتكرارات الخوارزمية"
            )
        
        st.markdown("---")
        
        # زر التشغيل
        if st.button("🚀 تشغيل محرك ACO", use_container_width=True, type="primary"):
            with st.spinner("🐜 جاري تشغيل خوارزمية ACO... قد يستغرق ذلك بضع دقائق"):
                try:
                    # تشغيل المحرك
                    results = run_aco_engine(
                        n_clusters=int(n_clusters),
                        n_ants=int(n_ants),
                        max_iter=int(max_iter),
                        n_components=10
                    )
                    
                    if results:
                        st.success("✅ اكتمل تشغيل محرك ACO بنجاح!")
                        
                        # حفظ النتائج في session_state
                        st.session_state['processed_data'] = results['processed_data']
                        st.session_state['cluster_labels'] = results['clusters']
                        st.session_state['cluster_centers'] = results['cluster_centers']
                        st.session_state['risk_results'] = results['risk_results']
                        st.session_state['cluster_stats'] = results['cluster_stats']
                        
                        st.info("💡 يمكنك الآن الانتقال إلى صفحة **تحليل المخاطر** لاستكشاف النتائج.")
                        
                        # عرض إحصائيات سريعة
                        st.markdown("### 📊 نتائج التجميع")
                        
                        cluster_stats = results['cluster_stats']
                        if not cluster_stats.empty:
                            st.dataframe(cluster_stats, use_container_width=True)
                    else:
                        st.error("❌ فشل تشغيل المحرك. تأكد من وجود بيانات في قاعدة البيانات.")
                
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء التشغيل: {str(e)}")
        
        st.markdown("---")
        
        # عرض النتائج إذا كانت موجودة في session_state
        if 'risk_results' in st.session_state and 'cluster_stats' in st.session_state:
            st.subheader("📈 نتائج التجميع الحالية")
            
            cluster_stats = st.session_state['cluster_stats']
            
            if not cluster_stats.empty:
                st.dataframe(cluster_stats, use_container_width=True)
                
                st.info("💡 هذه النتائج محفوظة في الذاكرة الحية. يمكنك الانتقال لصفحة تحليل المخاطر للتفاعل معها.")
            else:
                st.warning("⚠️ لا توجد نتائج تجميع في الذاكرة.")
    else:
        st.error("❌ محرك ACO غير متاح. تأكد من تثبيت جميع المكتبات المطلوبة.")
