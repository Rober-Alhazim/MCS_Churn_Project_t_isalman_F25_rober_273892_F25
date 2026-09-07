-- حذف الجدول إذا كان موجوداً
DROP TABLE IF EXISTS customers CASCADE;

-- إنشاء جدول العملاء الرئيسي
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    circle_id INTEGER,
    arpu_6 FLOAT,
    arpu_7 FLOAT,
    arpu_8 FLOAT,
    total_og_mou_6 FLOAT,
    total_og_mou_7 FLOAT,
    total_og_mou_8 FLOAT,
    total_ic_mou_6 FLOAT,
    total_ic_mou_7 FLOAT,
    total_ic_mou_8 FLOAT,
    total_rech_amt_6 FLOAT,
    total_rech_amt_7 FLOAT,
    total_rech_amt_8 FLOAT,
    total_rech_num_6 INTEGER,
    total_rech_num_7 INTEGER,
    total_rech_num_8 INTEGER,
    aon INTEGER,
    vol_3g_mb_6 FLOAT,
    vol_3g_mb_7 FLOAT,
    vol_3g_mb_8 FLOAT
);

-- إنشاء فهارس لتحسين الأداء
CREATE INDEX idx_customers_id ON customers(id);
CREATE INDEX idx_customers_arpu_8 ON customers(arpu_8);