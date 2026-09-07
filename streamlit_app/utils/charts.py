import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_risk_distribution_pie(risk_df):
    if risk_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="لا توجد بيانات", showarrow=False)
        return fig
    
    fig = px.pie(
        risk_df, 
        values='count', 
        names='risk_level',
        title='توزيع العملاء حسب مستوى المخاطرة',
        color='risk_level',
        color_discrete_map={
            'High Risk': '#ff4b4b',
            'Medium Risk': '#ffa500',
            'Low Risk': '#00cc66'
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(title_x=0.5, font=dict(size=14), showlegend=True)
    return fig

def create_arpu_trend_line(arpu_df):
    """
    📈 دالة مطورة: تحسب متوسط تراجع العوائد العام للمجموعة بدلاً من رسم خطوط مزدحمة لكل عميل
    """
    if arpu_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="لا توجد بيانات ARPU كافية", showarrow=False)
        return fig
    
    try:
        target_months = list(['arpu_6', 'arpu_7', 'arpu_8'])
        available_months = [col for col in target_months if col in arpu_df.columns]
        
        if not available_months:
            return go.Figure()
            
        # 1. حساب المتوسط الحسابي للـ ARPU عبر العينة لكل شهر لحساب النزعة العامة
        mean_values = arpu_df[available_months].mean().reset_index()
        mean_values.columns = list(['month', 'Average_ARPU'])
        
        # 2. تحويل أسماء الأعمدة البرمجية إلى أسماء شهور واضحة بالعربية
        month_labels = {'arpu_6': 'الشهر الأول (يونيو)', 'arpu_7': 'الشهر الثاني (يوليو)', 'arpu_8': 'الشهر الثالث (أغسطس)'}
        mean_values['month'] = mean_values['month'].map(month_labels)
        
        # 3. رسم خط بياني موحد يوضح التراجع العام
        fig = px.line(
            mean_values, 
            x='month', 
            y='Average_ARPU', 
            markers=True,
            title='متوسط مسار تراجع ARPU العام للعملاء المستهدفين',
            labels={'Average_ARPU': 'متوسط الإيرادات العام (ARPU)', 'month': 'الفترة الزمنية'}
        )
        
        fig.update_traces(line=dict(color='#ff4b4b', width=4), marker=dict(size=10, color='darkred'))
        fig.update_layout(title_x=0.5, font=dict(size=14), yaxis_title="متوسط العائد لكل مستخدم")
        return fig
    except:
        return go.Figure()

def create_risk_gauge(risk_score):
    """
    🎯 دالة مؤشر قياس المخاطرة بدون أي أقواس مربعة مباشرة لتفادي خطأ الاختفاء
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={'text': "درجة المخاطرة"},
        domain={'x': list([0, 1]), 'y': list([0, 1])},
        gauge={
            'axis': {'range': list([0, 100]), 'tickwidth': 1},
            'bar': {'color': "darkred"},
            'steps': list([
                {'range': list([0, 33]), 'color': "green"},
                {'range': list([33, 66]), 'color': "orange"},
                {'range': list([66, 100]), 'color': "red"}
            ]),
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': risk_score
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(t=50, b=10, l=10, r=10))
    return fig


    


