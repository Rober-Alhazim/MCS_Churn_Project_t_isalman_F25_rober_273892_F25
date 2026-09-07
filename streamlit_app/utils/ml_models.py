"""
نماذج التعلم الآلي للتوصيات الذكية
- Predictive Offer Matching (Random Forest)
- ML-Based Offer Composer (توليد عروض مخصصة ديناميكياً)
"""
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from scipy.optimize import minimize_scalar
import warnings
warnings.filterwarnings('ignore')

OFFER_TYPES = {
    0: " عرض باقة إنترنت إضافية + خصم 30% على البيانات",
    1: "📞 عرض دقائق مجانية + باقة مكالمات غير محدودة",
    2: "💳 عرض شحن مضاعف (اشحن 100 واحصل على 150)",
    3: "🎁 خصم 20% على جميع الخدمات + اتصال من خدمة العملاء",
    4: "📱 رسالة نصية تحفيزية + عرض خاص لمدة 7 أيام"
}

FEATURES = [
    'arpu_6', 'arpu_8', 'total_og_mou_6', 'total_og_mou_8',
    'vol_3g_mb_6', 'vol_3g_mb_8', 'total_rech_amt_6', 'total_rech_amt_8',
    'aon', 'risk_score', 'arpu_decline', 'mou_decline', 'data_decline', 'rech_decline'
]

@st.cache_resource
def generate_and_train_model():
    np.random.seed(42)
    n_samples = 15000
    data = {
        'arpu_6': np.random.uniform(50, 500, n_samples),
        'arpu_8': np.random.uniform(20, 400, n_samples),
        'total_og_mou_6': np.random.uniform(100, 1000, n_samples),
        'total_og_mou_8': np.random.uniform(50, 800, n_samples),
        'vol_3g_mb_6': np.random.uniform(100, 5000, n_samples),
        'vol_3g_mb_8': np.random.uniform(50, 4000, n_samples),
        'total_rech_amt_6': np.random.uniform(100, 1000, n_samples),
        'total_rech_amt_8': np.random.uniform(50, 800, n_samples),
        'aon': np.random.uniform(100, 3000, n_samples),
        'risk_score': np.random.uniform(50, 100, n_samples),
    }
    df = pd.DataFrame(data)
    df['arpu_decline'] = ((df['arpu_6'] - df['arpu_8']) / df['arpu_6'].replace(0, 1)) * 100
    df['mou_decline'] = ((df['total_og_mou_6'] - df['total_og_mou_8']) / df['total_og_mou_6'].replace(0, 1)) * 100
    df['data_decline'] = ((df['vol_3g_mb_6'] - df['vol_3g_mb_8']) / df['vol_3g_mb_6'].replace(0, 1)) * 100
    df['rech_decline'] = ((df['total_rech_amt_6'] - df['total_rech_amt_8']) / df['total_rech_amt_6'].replace(0, 1)) * 100
    
    def determine_offer(row):
        if row['data_decline'] > 50: return 0
        elif row['mou_decline'] > 50: return 1
        elif row['rech_decline'] > 50: return 2
        elif row['risk_score'] > 85: return 3
        else: return 4
    df['optimal_offer'] = df.apply(determine_offer, axis=1)
    
    X = df[FEATURES]
    y = df['optimal_offer']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    return model, model.score(X_test, y_test)

def get_ml_recommendation(customer_row):
    model, accuracy = generate_and_train_model()
    customer_data = customer_row.to_dict()
    for feat in FEATURES:
        if feat not in customer_data: customer_data[feat] = 0
    df_cust = pd.DataFrame([customer_data])[FEATURES]
    prediction = int(model.predict(df_cust)[0])
    probabilities = model.predict_proba(df_cust)[0]
    confidence = float(probabilities[prediction])
    
    def objective(discount):
        acceptance_prob = min(confidence + (discount * 0.4), 0.95)
        base_arpu = max(customer_data.get('arpu_8', 100), 1)
        return -((acceptance_prob * base_arpu * (1 - discount)) - (base_arpu * discount))
    result = minimize_scalar(objective, bounds=(0.05, 0.50), method='bounded')
    
    return {
        'ml_recommendation': OFFER_TYPES[prediction],
        'ml_confidence': confidence,
        'optimal_discount': float(result.x)
    }

# ============================================
# 🆕 ML-Based Offer Composer (توليد عروض مخصصة)
# ============================================

@st.cache_resource
def train_offer_composer_models():
    np.random.seed(42)
    n_samples = 15000
    data = {
        'arpu_decline': np.random.uniform(0, 80, n_samples),
        'data_decline': np.random.uniform(0, 80, n_samples),
        'mou_decline': np.random.uniform(0, 80, n_samples),
        'risk_score': np.random.uniform(50, 100, n_samples),
        'arpu_8': np.random.uniform(50, 500, n_samples),
    }
    df = pd.DataFrame(data)
    
    def determine_components(row):
        discount_type = 0 if row['arpu_8'] > 300 else (1 if row['arpu_8'] > 150 else 2)
        declines = [row['data_decline'], row['mou_decline'], (row['arpu_decline'] + row['data_decline'] + row['mou_decline']) / 3]
        target_service = int(np.argmax(declines))
        duration = 0 if row['risk_score'] > 85 else (1 if row['risk_score'] > 70 else 2)
        return discount_type, target_service, duration

    components_df = df.apply(determine_components, axis=1, result_type='expand')
    components_df.columns = ['discount_type', 'target_service', 'duration']
    df = pd.concat([df, components_df], axis=1)
    
    features = ['arpu_decline', 'data_decline', 'mou_decline', 'risk_score', 'arpu_8']
    X = df[features]
    models = {}
    for component in ['discount_type', 'target_service', 'duration']:
        y = df[component]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=50, max_depth=3, random_state=42)
        model.fit(X_train, y_train)
        models[component] = {'model': model, 'accuracy': model.score(X_test, y_test)}
    return models

def generate_custom_offer(customer_row, composer_models=None):
    """
    🎁 توليد عرض مخصص وواقعي لكل عميل
    
    القواعد المنطقية:
    - العرض يتناسب مع نوع التراجع الفعلي
    - ملخص التراجع يعكس فقط التراجعات الحقيقية
    - لا تناقض بين حالة العميل والعرض المقدم
    """
    if composer_models is None:
        composer_models = train_offer_composer_models()
    
    customer_data = customer_row.to_dict()
    
    # حساب نسب التراجع
    arpu_6 = customer_data.get('arpu_6', 0) or 1
    arpu_8 = customer_data.get('arpu_8', 100) or 100
    mou_6 = customer_data.get('total_og_mou_6', 0) or 1
    mou_8 = customer_data.get('total_og_mou_8', 0) or 0
    data_6 = customer_data.get('vol_3g_mb_6', 0) or 1
    data_8 = customer_data.get('vol_3g_mb_8', 0) or 0
    rech_6 = customer_data.get('total_rech_amt_6', 0) or 1
    rech_8 = customer_data.get('total_rech_amt_8', 0) or 0
    
    arpu_decline = max(0, ((arpu_6 - arpu_8) / arpu_6) * 100)
    mou_decline = max(0, ((mou_6 - mou_8) / mou_6) * 100)
    data_decline = max(0, ((data_6 - data_8) / data_6) * 100)
    rech_decline = max(0, ((rech_6 - rech_8) / rech_6) * 100)
    
    risk_score = customer_data.get('risk_score', 50)
    
    # ============================================
    # 1. تحديد نوع التراجع الفعلي (الأكثر أهمية)
    # ============================================
    
    declines = {
        'data': data_decline,
        'mou': mou_decline,
        'rech': rech_decline,
        'arpu': arpu_decline
    }
    
    # ترتيب التراجعات من الأكبر للأصغر
    sorted_declines = sorted(declines.items(), key=lambda x: x[1], reverse=True)
    max_decline_type = sorted_declines[0][0]
    max_decline_value = sorted_declines[0][1]
    
    # ============================================
    # 2. بناء ملخص التراجع الدقيق
    # ============================================
    
    active_declines = []
    if data_decline > 30:
        active_declines.append(f"بيانات {data_decline:.0f}%")
    if mou_decline > 30:
        active_declines.append(f"مكالمات {mou_decline:.0f}%")
    if rech_decline > 30:
        active_declines.append(f"شحن {rech_decline:.0f}%")
    if arpu_decline > 20 and not active_declines:
        active_declines.append(f"ARPU {arpu_decline:.0f}%")
    
    if len(active_declines) >= 3:
        decline_summary = f"📉 تراجع شامل: {', '.join(active_declines)}"
    elif len(active_declines) == 2:
        decline_summary = f"📉 تراجع في: {', '.join(active_declines)}"
    elif len(active_declines) == 1:
        decline_summary = f"📉 تراجع في {active_declines[0]}"
    else:
        decline_summary = "📉 تراجع عام في النشاط"
    
    # ============================================
    # 3. تحديد العرض بناءً على نوع التراجع الفعلي
    # ============================================
    
    # تحديد المدة بناءً على درجة الخطورة
    if risk_score > 85:
        duration = "أسبوع"
        duration_days = 7
    elif risk_score > 70:
        duration = "شهر"
        duration_days = 30
    else:
        duration = "3 أشهر"
        duration_days = 90
    
    # ============================================
    # 4. بناء العرض المنطقي
    # ============================================
    
    if max_decline_type == 'data' and data_decline > 40:
        # ✅ تراجع في البيانات → عرض بيانات
        gb_options = [1, 2, 3, 5, 8, 10]
        gb_index = min(int(data_decline / 15), len(gb_options) - 1)
        gb_amount = gb_options[max(0, gb_index)]
        
        offer_text = f"✅ باقة {gb_amount} GB بيانات مجانية | ⏰ لمدة {duration} |  بدون رسوم تفعيل"
        discount_type = "باقة مجانية"
        target_service = "البيانات والإنترنت"
        bonus = "بدون رسوم تفعيل"
        
    elif max_decline_type == 'mou' and mou_decline > 40:
        # ✅ تراجع في المكالمات → عرض مكالمات
        minutes_options = [100, 200, 300, 500, 750, 1000]
        minutes_index = min(int(mou_decline / 10), len(minutes_options) - 1)
        minutes_amount = minutes_options[max(0, minutes_index)]
        
        offer_text = f"✅ باقة {minutes_amount} دقيقة مجانية | ⏰ لمدة {duration} | 🎉 مكالمات لجميع الشبكات"
        discount_type = "باقة مجانية"
        target_service = "المكالمات"
        bonus = "مكالمات لجميع الشبكات"
        
    elif max_decline_type == 'rech' and rech_decline > 40:
        # ✅ تراجع في الشحن → عرض رصيد أو خصم
        credit_amount = arpu_8 * 0.25
        credit_amount = max(20, min(credit_amount, 150))
        credit_amount = round(credit_amount / 10) * 10
        
        offer_text = f"✅ رصيد مجاني بقيمة ₹{credit_amount:.0f} | ⏰ صالح لمدة شهر | 💳 يُضاف عند الشحن التالي"
        discount_type = "رصيد مجاني"
        target_service = "جميع الخدمات"
        bonus = "يُضاف عند الشحن التالي"
        
    elif max_decline_type == 'arpu' and arpu_decline > 25:
        # ✅ تراجع في ARPU → خصم عام
        discount_pct = 15 + ((risk_score - 50) / 50) * 25
        discount_pct = min(max(discount_pct, 15), 40)
        discount_pct = round(discount_pct / 5) * 5
        
        offer_text = f"✅ خصم {discount_pct:.0f}% على جميع الخدمات | ⏰ لمدة {duration} | 🎁 يشمل البيانات والمكالمات"
        discount_type = "نسبة مئوية"
        target_service = "جميع الخدمات"
        bonus = "يشمل البيانات والمكالمات"
        
    else:
        # ✅ تراجع عام → عرض مختلط
        gb_amount = max(1, int(data_decline / 20))
        minutes_amount = max(50, int(mou_decline * 2))
        
        offer_text = f"✅ باقة مختلطة ({gb_amount} GB + {minutes_amount} دقيقة) | ⏰ لمدة شهر |  100 SMS مجانية"
        discount_type = "باقة مجانية"
        target_service = "جميع الخدمات"
        bonus = "100 SMS مجانية"
    
    # ============================================
    # 5. إرجاع العرض مع جميع التفاصيل
    # ============================================
    
    return {
        'offer_text': offer_text,
        'discount_type': discount_type,
        'target_service': target_service,
        'duration': duration,
        'duration_days': duration_days,
        'bonus': bonus,
        'decline_summary': decline_summary,
        'max_decline_type': max_decline_type,
        'arpu_decline': arpu_decline,
        'data_decline': data_decline,
        'mou_decline': mou_decline,
        'rech_decline': rech_decline
    }