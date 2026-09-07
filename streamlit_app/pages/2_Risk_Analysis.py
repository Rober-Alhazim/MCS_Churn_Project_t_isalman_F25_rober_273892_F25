# streamlit_app/pages/2_Risk_Analysis.py
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.styles import inject_styles
from utils.db_connector import (
    get_total_customers,
    get_avg_arpu,
    get_high_risk_count,
    get_medium_risk_count,
    get_low_risk_count,
    get_risk_distribution,
    get_high_risk_customers,
    get_arpu_trend,
    get_revenue_at_risk,
    get_avg_risk_score,
    get_critical_accounts,  # ✅ إضافة هذه الدالة
    test_connection
)
from aco_engine.risk_scoring import RiskScorer

st.set_page_config(
    page_title="تحليل المخاطر",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
st.title("️ تحليل المخاطر والمؤشرات المالية")
st.markdown("---")

# ============================================
# منطق تحميل البيانات (ACO vs DB)
# ============================================
has_aco_data = 'processed_data' in st.session_state and 'cluster_labels' in st.session_state

if has_aco_data:
    df_aco = st.session_state['processed_data']
    labels_aco = st.session_state['cluster_labels']
    
    # ✅ إزالة قسم محاكاة أوزان العناقيد (لم يعد موجوداً)
    
    # إعادة حساب المخاطر ديناميكياً
    scorer = RiskScorer()
    calculated_results = scorer.calculate_risk_scores(df_aco, labels_aco)
    
    total = len(calculated_results)
    high_risk_df = calculated_results[calculated_results['risk_level'] == 'High Risk']
    medium_risk_df = calculated_results[calculated_results['risk_level'] == 'Medium Risk']
    
    high_risk_count = len(high_risk_df)
    medium_risk_count = len(medium_risk_df)
    low_risk_count = len(calculated_results[calculated_results['risk_level'] == 'Low Risk'])
    
    avg_arpu = df_aco['arpu_8'].mean() if 'arpu_8' in df_aco.columns else 0
    
    # حساب متوسط شدة الخطورة لكل فئة
    avg_high_risk_score = high_risk_df['risk_score'].mean() if not high_risk_df.empty else 0
    avg_medium_risk_score = medium_risk_df['risk_score'].mean() if not medium_risk_df.empty else 0
    
    revenue_at_risk = high_risk_df['arpu_8'].sum() if 'arpu_8' in high_risk_df.columns else 0
    
    # ✅ حساب عدد الحسابات الحرجة من نتائج ACO
    critical_accounts_count = len(calculated_results[calculated_results['risk_score'] > 85])
    
    # دمج ARPU للعرض
    high_risk_display = high_risk_df.merge(df_aco[['id', 'arpu_8']], on='id', how='left')
    
else:
    st.info("ℹ️ لم يتم تشغيل محرك ACO في هذه الجلسة. يتم عرض البيانات الافتراضية من قاعدة البيانات.")
    
    total = get_total_customers()
    avg_arpu = get_avg_arpu()
    high_risk_count = get_high_risk_count()
    medium_risk_count = get_medium_risk_count()
    low_risk_count = get_low_risk_count()
    risk_dist_dict = get_risk_distribution()
    high_risk_display = get_high_risk_customers(20)
    arpu_trend_df = get_arpu_trend()
    revenue_at_risk = get_revenue_at_risk()
    
    avg_high_risk_score = get_avg_risk_score('High Risk')
    avg_medium_risk_score = get_avg_risk_score('Medium Risk')
    
    # ✅ استخدام الدالة الصحيحة لحساب الحسابات الحرجة
    critical_accounts_count = get_critical_accounts(85)

# ============================================
# لوحة الإنذار المالي المبكر (Financial Risk Dashboard)
# ============================================
st.subheader("💸 لوحة الإنذار المالي المبكر")
st.markdown("تحليل فوري للأثر المالي لمغادرة العملاء وتوزيع شدة الخطورة")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label=" الإيرادات المعرضة للخطر",
        value=f"{revenue_at_risk:,.0f}",
        delta="خسارة متوقعة ",
        delta_color="inverse"
    )

with col2:
    # ✅ إصلاح: استخدام العدد الفعلي بدلاً من الحساب من high_risk_display
    st.metric(
        label="🔴 حسابات حرجة جداً",
        value=f"{critical_accounts_count:,}",
        delta="درجة خطر > 85",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label=" متوسط شدة الخطورة (عالي)",
        value=f"{avg_high_risk_score:.1f}/100",
        delta="فئة High Risk",
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="📊 متوسط شدة الخطورة (متوسط)",
        value=f"{avg_medium_risk_score:.1f}/100",
        delta="فئة Medium Risk",
        delta_color="inverse"
    )

st.markdown("---")

# ============================================
# الرسوم البيانية
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 توزيع مستويات المخاطرة")
    
    if has_aco_data:
        dist = calculated_results['risk_level'].value_counts()
    else:
        dist = pd.Series(risk_dist_dict)
    
    if not dist.empty:
        fig = go.Figure(data=[
            go.Pie(
                labels=dist.index,
                values=dist.values,
                marker_colors=['#ff4d4d', '#ffd700', '#00d4ff'],
                hole=0.4,
                textinfo='label+percent'
            )
        ])
        fig.update_layout(
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8f1f5')
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader(" مسار تراجع العائد (ARPU)")
    
    if not has_aco_data and 'arpu_trend_df' in locals() and not arpu_trend_df.empty:
        months = ['شهر 6', 'شهر 7', 'شهر 8']
        vals = [
            arpu_trend_df['arpu_6'].iloc[0] if 'arpu_6' in arpu_trend_df.columns else 0,
            arpu_trend_df['arpu_7'].iloc[0] if 'arpu_7' in arpu_trend_df.columns else 0,
            arpu_trend_df['arpu_8'].iloc[0] if 'arpu_8' in arpu_trend_df.columns else 0
        ]
        fig = go.Figure(data=[
            go.Scatter(
                x=months,
                y=vals,
                mode='lines+markers',
                marker=dict(size=10, color='#00d4ff'),
                line=dict(color='#00ffb3', width=3)
            )
        ])
        fig.update_layout(
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8f1f5')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ بيانات الاتجاه متاحة فقط في الوضع الافتراضي.")

st.markdown("---")

# ============================================
# قائمة العملاء الأكثر خطورة
# ============================================
st.subheader(" قائمة العملاء الأكثر خطورة")

if not high_risk_display.empty:
    display_cols = ['id', 'risk_score', 'risk_level', 'arpu_8']
    available_cols = [c for c in display_cols if c in high_risk_display.columns]
    
    st.dataframe(
        high_risk_display[available_cols].head(20).round(2),
        use_container_width=True
    )
else:
    st.warning("⚠️ لا يوجد عملاء ذو خطورة عالية.")
