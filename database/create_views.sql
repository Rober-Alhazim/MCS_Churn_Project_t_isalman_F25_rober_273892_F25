-- View لحساب مؤشرات التراجع السلوكي
CREATE OR REPLACE VIEW churn_indicators AS
SELECT 
    id,
    -- تراجع ARPU
    (arpu_7 - arpu_6) AS arpu_decline_6_to_7,
    (arpu_8 - arpu_7) AS arpu_decline_7_to_8,
    CASE 
        WHEN arpu_6 > 0 THEN ((arpu_6 - arpu_8) / arpu_6) * 100 
        ELSE 0 
    END AS arpu_decline_percentage,
    
    -- تراجع المكالمات الصادرة
    (total_og_mou_7 - total_og_mou_6) AS og_mou_decline_6_to_7,
    (total_og_mou_8 - total_og_mou_7) AS og_mou_decline_7_to_8,
    
    -- تراجع المكالمات الواردة
    (total_ic_mou_7 - total_ic_mou_6) AS ic_mou_decline_6_to_7,
    (total_ic_mou_8 - total_ic_mou_7) AS ic_mou_decline_7_to_8,
    
    -- تراجع الشحنات
    (total_rech_amt_7 - total_rech_amt_6) AS rech_decline_6_to_7,
    (total_rech_amt_8 - total_rech_amt_7) AS rech_decline_7_to_8,
    
    -- تراجع استخدام البيانات
    (vol_3g_mb_7 - vol_3g_mb_6) AS data_decline_6_to_7,
    (vol_3g_mb_8 - vol_3g_mb_7) AS data_decline_7_to_8,
    
    -- مؤشر خطر عام (مجمع)
    (COALESCE((arpu_8 - arpu_7), 0) + 
     COALESCE((total_rech_amt_8 - total_rech_amt_7), 0) +
     COALESCE((total_og_mou_8 - total_og_mou_7), 0)) / 3 AS composite_risk_score
    
FROM customers;

-- View لتوزيع العملاء حسب مستويات الخطورة
CREATE OR REPLACE VIEW risk_distribution AS
SELECT 
    id,
    arpu_8,
    total_rech_amt_8,
    total_og_mou_8,
    CASE 
        WHEN (arpu_8 < 50 AND total_rech_amt_8 < 50) THEN 'High Risk'
        WHEN (arpu_8 < 100 AND total_rech_amt_8 < 100) THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_level
FROM customers;

-- View للإحصائيات العامة السريعة
CREATE OR REPLACE VIEW general_statistics AS
SELECT 
    COUNT(*) AS total_customers,
    AVG(arpu_8) AS avg_arpu,
    AVG(total_rech_amt_8) AS avg_recharge,
    AVG(total_og_mou_8) AS avg_mou,
    SUM(CASE WHEN arpu_8 < 50 THEN 1 ELSE 0 END) AS high_risk_count,
    SUM(CASE WHEN arpu_8 BETWEEN 50 AND 100 THEN 1 ELSE 0 END) AS medium_risk_count,
    SUM(CASE WHEN arpu_8 > 100 THEN 1 ELSE 0 END) AS low_risk_count
FROM customers;