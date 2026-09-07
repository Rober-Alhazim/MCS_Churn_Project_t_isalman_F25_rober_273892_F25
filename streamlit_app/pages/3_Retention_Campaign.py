# streamlit_app/pages/3_Retention_Campaign.py
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# استيراد الأنماط الموحدة
from utils.styles import inject_styles

# استيراد دوال قاعدة البيانات
from utils.db_connector import (
    get_high_risk_count,
    get_medium_risk_count,
    get_low_risk_count,
    get_total_customers,
    get_avg_arpu,
    get_avg_aon,
    get_revenue_at_risk,
    get_critical_accounts,
    get_high_risk_customers,
    get_avg_risk_score,
    test_connection
)

# استيراد نماذج ML
try:
    from utils.ml_models import (
        train_offer_composer_models,
        generate_custom_offer
    )
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# إعداد الصفحة
st.set_page_config(
    page_title="حملات الحفاظ على العملاء",
    page_icon="🎯",
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
st.title("🎯 حملات الحفاظ على العملاء")
st.markdown("---")

# ============================================
# منطق تحميل البيانات (ACO vs DB)
# ============================================
has_aco_session = 'risk_results' in st.session_state and 'processed_data' in st.session_state

if has_aco_session:
    # وضع ACO مباشر من الجلسة الحالية
    recommendations_df = st.session_state['risk_results']
    df_aco = st.session_state['processed_data']
    
    merged_df = recommendations_df.merge(
        df_aco[['id', 'arpu_8', 'total_og_mou_8', 'aon']],
        on='id',
        how='left'
    )
    
    st.info("✅ يتم استخدام بيانات ACO من الجلسة الحالية (محدّثة)")
    
else:
    # وضع قاعدة البيانات (Fallback)
    st.info("ℹ️ يتم استخدام البيانات المحفوظة في قاعدة البيانات. لتشغيل ACO مباشرة، انتقل إلى صفحة إدارة البيانات.")
    
    try:
        from sqlalchemy import text
        from database.db_config import get_db_connection
        
        engine = get_db_connection()
        
        # جلب نتائج التجميع من قاعدة البيانات
        query = """
            SELECT 
                cr.id,
                cr.cluster_id,
                cr.risk_score,
                cr.risk_level,
                cr.arpu_decline,
                cr.mou_decline,
                cr.rech_decline,
                c.arpu_8,
                c.total_og_mou_8,
                c.aon
            FROM clustering_results cr
            JOIN customers c ON cr.id = c.id
            ORDER BY cr.risk_score DESC
        """
        
        merged_df = pd.read_sql(query, engine)
        
        if merged_df.empty:
            st.warning("⚠️ لا توجد بيانات في جدول clustering_results. يرجى تشغيل محرك ACO أولاً من صفحة إدارة البيانات.")
            if st.button(" الانتقال إلى إدارة البيانات", use_container_width=True, type="primary"):
                st.switch_page("pages/1_Data_Management.py")
            st.stop()
        
    except Exception as e:
        st.error(f"❌ خطأ في جلب البيانات من قاعدة البيانات: {e}")
        st.stop()

# ============================================
# حساب الإحصائيات
# ============================================
high_risk_df = merged_df[merged_df['risk_level'] == 'High Risk']
medium_risk_df = merged_df[merged_df['risk_level'] == 'Medium Risk']
low_risk_df = merged_df[merged_df['risk_level'] == 'Low Risk']

high_count = len(high_risk_df)
medium_count = len(medium_risk_df)
low_count = len(low_risk_df)
total_target = high_count + medium_count + low_count

revenue_at_risk = high_risk_df['arpu_8'].sum() if 'arpu_8' in high_risk_df.columns and not high_risk_df.empty else get_revenue_at_risk()
critical_accounts_count = len(merged_df[merged_df['risk_score'] > 85]) if 'risk_score' in merged_df.columns else get_critical_accounts(85)

avg_high_risk_score = high_risk_df['risk_score'].mean() if 'risk_score' in high_risk_df.columns and not high_risk_df.empty else get_avg_risk_score('High Risk')
avg_medium_risk_score = medium_risk_df['risk_score'].mean() if 'risk_score' in medium_risk_df.columns and not medium_risk_df.empty else get_avg_risk_score('Medium Risk')

# ============================================
# المؤشرات الرئيسية (ROI Dashboard)
# ============================================
# ============================================
# المؤشرات الرئيسية (ROI Dashboard - واقعي)
# ============================================
st.subheader("💰 مؤشرات فعالية الحملة والعائد على الاستثمار")
st.markdown("تقدير ذكي لتكلفة الحفاظ على العملاء مقابل الإيرادات التي سيتم إنقاذها")

# 1. استهداف High Risk فقط (الأكثر كفاءة)
target_count = high_count

# 2. تكلفة واقعية (15-25 وحدة/عميل حسب نوع الحملة)
estimated_cost_per_customer = 20  # تكلفة متوسطة
estimated_budget = target_count * estimated_cost_per_customer

# 3. نسبة نجاح واقعية بناءً على الدراسات
# في الواقع، أفضل حملات الاحتفاظ تحقق 20-40% نجاح
if avg_high_risk_score > 90:
    # عملاء شديدو الخطورة - نسبة نجاح منخفضة (صعب إنقاذهم)
    success_rate = 0.25  # 25% فقط
elif avg_high_risk_score > 80:
    success_rate = 0.30  # 30%
else:
    success_rate = 0.35  # 35%

# 4. خصم العملاء الذين كانوا سيبقون anyway (Natural Retention)
natural_retention_rate = 0.10  # 10% كانوا سيبقون بدون حملة
effective_success_rate = success_rate - natural_retention_rate

# 5. حساب الإيراد المتوقع
expected_saved_revenue = revenue_at_risk * effective_success_rate

# 6. حساب ROI
roi_percentage = ((expected_saved_revenue - estimated_budget) / estimated_budget * 100) if estimated_budget > 0 else 0

# 7. حساب فترة استرداد التكلفة (Payback Period)
monthly_saved_revenue = expected_saved_revenue / 12
payback_months = estimated_budget / monthly_saved_revenue if monthly_saved_revenue > 0 else 0

# 8. حساب أفضل حالة وأسوأ حالة (Scenario Analysis)
best_case_rate = success_rate + 0.10  # +10%
worst_case_rate = success_rate - 0.10  # -10%

best_case_roi = ((revenue_at_risk * best_case_rate - estimated_budget) / estimated_budget) * 100
worst_case_roi = ((revenue_at_risk * worst_case_rate - estimated_budget) / estimated_budget) * 100

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🎯 حجم الجمهور المستهدف",
        value=f"{target_count:,}",
        delta="عملاء High Risk فقط",
        help="إجمالي العملاء المستهدفين بالحملة"
    )

with col2:
    st.metric(
        label="💰 الميزانية التقديرية",
        value=f"{estimated_budget:,.0f}",
        delta=f"{estimated_cost_per_customer} وحدة/عميل",
        delta_color="inverse",
        help="التكلفة المتوقعة للحملة"
    )

with col3:
    st.metric(
        label=" الإيراد المتوقع إنقاذه",
        value=f"{expected_saved_revenue:,.0f}",
        delta=f"نسبة نجاح {effective_success_rate*100:.0f}% (واقعي)",
        help=f"الإيرادات التي يمكن حفظها (بعد خصم {natural_retention_rate*100:.0f}% الذين كانوا سيبقون)"
    )

with col4:
    delta_color = "normal" if roi_percentage > 0 else "inverse"
    st.metric(
        label="📈 العائد على الاستثمار (ROI)",
        value=f"{roi_percentage:.0f}%",
        delta=f"من {worst_case_roi:.0f}% إلى {best_case_roi:.0f}%",
        delta_color=delta_color,
        help="نسبة العائد على الاستثمار المتوقع (النطاق يعكس السيناريوهات المختلفة)"
    )

# عرض معلومات إضافية
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **📊 نسبة النجاح المتوقعة**
    - الأساس: {success_rate*100:.0f}%
    - الصافي: {effective_success_rate*100:.0f}%
    - (بعد خصم {natural_retention_rate*100:.0f}% Natural Retention)
    """)

with col2:
    st.info(f"""
    **⏱️ فترة استرداد التكلفة**
    - {payback_months:.1f} شهر
    - (إذا كان ROI موجب)
    """)

with col3:
    st.info(f"""
    **🎯 السيناريوهات**
    - الأفضل: {best_case_roi:.0f}%
    - المتوقع: {roi_percentage:.0f}%
    - الأسوأ: {worst_case_roi:.0f}%
    """)

# ============================================
# الأولويات التشغيلية
# ============================================
st.subheader("🚨 الأولويات التشغيلية")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🔴 عملاء خطرين",
        value=f"{high_count:,}",
        delta="اتصال فوري",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="🟡 عملاء متوسطين",
        value=f"{medium_count:,}",
        delta="مراقبة",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="🟢 عملاء آمنين",
        value=f"{low_count:,}",
        delta="ولاء",
        delta_color="normal"
    )

with col4:
    st.metric(
        label="🚨 يحتاجون تدخلاً فورياً",
        value=f"{critical_accounts_count:,}",
        delta="درجة خطر > 85",
        delta_color="inverse"
    )

st.markdown("---")

# ============================================
# التبويبات
# ============================================
tab1, tab2, tab3 = st.tabs([
    " العروض المخصصة (AI Composer)",
    " تصدير الحملة",
    "🔗 الربط مع المساعد الذكي"
])

# ============================================
# التبويب 1: العروض المخصصة ديناميكياً
# ============================================
with tab1:
    st.subheader("🎁 العروض المخصصة ديناميكياً (ML-Based Offer Composer)")
    
    if ML_AVAILABLE:
        st.info(f"📊 إجمالي العملاء المستهدفين: **{total_target:,}** عميل ({high_count:,} عالي الخطورة + {medium_count:,} متوسط الخطورة)")
        
        # زر توليد العروض
        if st.button("🎯 توليد عروض مخصصة لكل عميل", type="primary", use_container_width=True):
            with st.spinner("🤖 جاري توليد عروض مخصصة بواسطة خوارزمية Offer Composer..."):
                try:
                    # تدريب النماذج
                    composer_models = train_offer_composer_models()
                    
                    custom_offers = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    total = len(merged_df)
                    
                    for idx, (_, row) in enumerate(merged_df.iterrows()):
                        offer = generate_custom_offer(row, composer_models)
                        custom_offers.append(offer)
                        
                        if (idx + 1) % 100 == 0 or idx == total - 1:
                            progress = (idx + 1) / total
                            progress_bar.progress(progress)
                            status_text.text(f"⏳ جاري توليد العرض للعميل {idx + 1} من {total}...")
                    
                    progress_bar.progress(1.0)
                    status_text.text(f"✅ اكتمل توليد {total} عرض مخصص!")
                    
                    # إضافة العروض للـ DataFrame
                    merged_df['custom_offer'] = [o['offer_text'] for o in custom_offers]
                    merged_df['discount_type'] = [o['discount_type'] for o in custom_offers]
                    merged_df['target_service'] = [o['target_service'] for o in custom_offers]
                    merged_df['duration'] = [o['duration'] for o in custom_offers]
                    merged_df['bonus'] = [o['bonus'] for o in custom_offers]
                    
                    # حفظ في session_state
                    st.session_state['generated_offers'] = merged_df
                    
                    st.success(f"✅ تم توليد **{total:,}** عرض مخصص وفريد لكل عميل!")
                    
                    # فلترة حسب مستوى الخطر
                    risk_filter = st.multiselect(
                        "🔍 فلترة حسب مستوى الخطر",
                        options=merged_df["risk_level"].unique(),
                        default=["High Risk"]
                    )
                    
                    filtered_df = merged_df[merged_df["risk_level"].isin(risk_filter)]
                    
                    # عرض الجدول
                    display_cols = ["id", "risk_score", "risk_level", "custom_offer"]
                    display_df = filtered_df[display_cols].copy()
                    display_df["risk_score"] = display_df["risk_score"].round(1)
                    
                    column_names = {
                        "id": "رقم العميل",
                        "risk_score": "درجة الخطر",
                        "risk_level": "مستوى الخطر",
                        "custom_offer": "🎁 العرض المخصص"
                    }
                    
                    display_df = display_df.rename(columns=column_names)
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                    st.caption(f"📊 عرض **{len(display_df):,}** عرض مخصص")
                    
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء توليد العروض: {str(e)}")
                    st.exception(e)  # لعرض تفاصيل الخطأ
        
        # عرض العروض المولدة إذا وجدت
        if 'generated_offers' in st.session_state:
            st.markdown("---")
            st.subheader("🔍 تفاصيل العرض لعميل محدد")
            
            sample_df = st.session_state['generated_offers']
            
            selected_id = st.selectbox(
                "اختر عميلاً لرؤية تفاصيل عرضه المخصص:",
                options=sample_df['id'].tolist(),
                format_func=lambda x: f"عميل رقم {int(x)}"
            )
            
            if selected_id:
                idx = sample_df[sample_df['id'] == selected_id].index[0]
                offer = {
                    'offer_text': sample_df.iloc[idx]['custom_offer'],
                    'discount_type': sample_df.iloc[idx]['discount_type'],
                    'target_service': sample_df.iloc[idx]['target_service'],
                    'duration': sample_df.iloc[idx]['duration'],
                    'bonus': sample_df.iloc[idx]['bonus']
                }
                row = sample_df.iloc[idx]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📊 حالة العميل")
                    st.metric("مستوى الخطر", row['risk_level'])
                    st.metric("درجة الخطر", f"{row['risk_score']:.1f}")
                
                with col2:
                    st.markdown("###  مكونات العرض المولد")
                    st.success(f"**نوع الخصم:** {offer['discount_type']}")
                    st.success(f"**الخدمة المستهدفة:** {offer['target_service']}")
                    st.success(f"**مدة العرض:** {offer['duration']}")
                    st.success(f"**الهدية الإضافية:** {offer['bonus']}")
                
                st.markdown("---")
                st.markdown(f"""
                ###  نص العرض النهائي (جاهز للإرسال للعميل):
                > **{offer['offer_text']}**
                """)
                
                # زر الانتقال للمساعد الذكي
                if st.button("💬 اسأل المساعد الذكي عن هذا العرض", use_container_width=True):
                    st.session_state['campaign_context'] = {
                        'customer_id': int(selected_id),
                        'offer_text': offer['offer_text'],
                        'risk_level': row['risk_level'],
                        'risk_score': float(row['risk_score'])
                    }
                    st.switch_page("pages/4_AI_Assistant.py")
    
    else:
        st.error("❌ نماذج ML غير متوفرة. تأكد من تثبيت المكتبات المطلوبة.")

# ============================================
# التبويب 2: تصدير الحملة
# ============================================
with tab2:
    st.subheader("📤 تصدير الحملة الذكية")
    
    if 'generated_offers' in st.session_state:
        export_df = st.session_state['generated_offers'].copy()
        
        # تحديد الأعمدة للتصدير
        export_cols = [
            "id", "risk_score", "risk_level",
            "discount_type", "target_service", "duration", "bonus",
            "custom_offer"
        ]
        
        export_df = export_df[export_cols].copy()
        
        # تسمية الأعمدة بالعربية
        column_names = {
            "id": "رقم_العميل",
            "risk_score": "درجة_الخطر",
            "risk_level": "مستوى_الخطر",
            "discount_type": "نوع_الخصم",
            "target_service": "الخدمة_المستهدفة",
            "duration": "مدة_العرض",
            "bonus": "الهدية_الإضافية",
            "custom_offer": "العرض_المخصص"
        }
        
        export_df = export_df.rename(columns=column_names)
        
        # تحويل إلى CSV
        csv_data = export_df.to_csv(index=False).encode('utf-8-sig')
        
        # زر التحميل
        st.download_button(
            label="📥 تحميل ملف CSV للحملة الذكية",
            data=csv_data,
            file_name=f"ai_campaign_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
        
        st.markdown("---")
        st.subheader(" معاينة البيانات قبل التصدير")
        st.dataframe(export_df.head(10), use_container_width=True, hide_index=True)
        st.info(f"📄 الملف يحتوي على **{len(export_df):,}** عميل مع عروض مخصصة ديناميكياً")
        
    else:
        st.warning("⚠️ لا توجد عروض مولدة للتصدير. يرجى توليد العروض في التبويب الأول أولاً.")

# ============================================
# التبويب 3: الربط مع المساعد الذكي
# ============================================
with tab3:
    st.subheader(" الربط الذكي مع المساعد الذكي (Gemini AI)")
    
    st.markdown("""
    ### 🔍 كيف يعمل الربط؟
    
    يمكنك نقل سياق الحملة الحالية إلى **المساعد الذكي** للحصول على:
    - 📊 **تحليل متعمق** لفعالية الحملة
    -  **إجابات على أسئلتك** حول العملاء المستهدفين
    - 📝 **توليد نصوص تسويقية** مخصصة
    - 💡 **اقتراحات لتحسين** استراتيجية الاحتفاظ
    
    ### 🚀 خطوات الاستخدام:
    1. قم بتوليد العروض في التبويب الأول
    2. اختر عميلاً محدداً لعرض تفاصيل عرضه
    3. اضغط على زر **"اسأل المساعد الذكي عن هذا العرض"**
    4. سيتم نقلك تلقائياً لصفحة المساعد الذكي مع السياق الكامل
    """)
    
    if 'generated_offers' in st.session_state:
        st.success("✅ العروض متاحة! يمكنك الآن الانتقال للمساعد الذكي من التبويب الأول.")
        
        if st.button("🤖 الانتقال إلى المساعد الذكي", use_container_width=True, type="primary"):
            st.switch_page("pages/4_AI_Assistant.py")
    else:
        st.info("ℹ️ قم بتوليد العروض أولاً لتمكين الربط مع المساعد الذكي.")

# ============================================
# نصائح للحملة (Sidebar)
# ============================================
with st.sidebar:
    st.markdown("### 📌 نصائح لنجاح الحملة")
    
    st.markdown("""
    #### 🔴 العملاء الخطرين (High Risk):
    - اتصل بهم خلال **24 ساعة**
    - قدم لهم العرض المخصص مباشرة
    - تابع معهم بعد **أسبوع**
    
    #### 🟡 العملاء متوسطي الخطورة (Medium Risk):
    - 📱 أرسل لهم رسالة نصية بالعرض المخصص
    -  تابع معهم بعد **3 أيام**
    
    #### 🟢 العملاء الآمنين (Low Risk):
    - أرسل رسائل ترويجية دورية
    - قدم مكافآت الولاء
    
    #### 📊 تتبع الأداء:
    - سجل العملاء الذين استجابوا
    - قارن ARPU قبل وبعد الحملة
    - 🎯 احسب ROI للحملة بشكل دوري
    """)
    
