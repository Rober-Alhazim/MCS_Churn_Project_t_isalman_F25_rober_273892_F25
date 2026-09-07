# aco_engine/preprocess.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.decomposition import PCA
from typing import Tuple, List

class DataPreprocessor:
    def __init__(self, n_components=10):  
        self.n_components = n_components
        self.scaler = RobustScaler()
        self.pca_scaler = StandardScaler()
        self.pca = PCA(n_components=n_components)
    
    def _remove_outliers(self, X):
        print("🔍 جاري إزالة القيم المتطرفة (Outliers)...")
        Q1 = np.percentile(X, 25, axis=0)
        Q3 = np.percentile(X, 75, axis=0)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        X_clean = np.clip(X, lower_bound, upper_bound)
        
        outliers_count = np.sum((X < lower_bound) | (X > upper_bound))
        print(f"   ✅ تم معالجة {outliers_count:,} قيمة متطرفة")
        
        return X_clean
    
    def select_features(self, df):
        feature_columns = [
            'arpu_6', 'arpu_7', 'arpu_8',
            'total_og_mou_6', 'total_og_mou_7', 'total_og_mou_8',
            'total_rech_amt_6', 'total_rech_amt_7', 'total_rech_amt_8',
            'aon', 'vol_3g_mb_8'
        ]
        
        new_features = [
            'total_ic_mou_6', 'total_ic_mou_7', 'total_ic_mou_8',
            'total_rech_num_6', 'total_rech_num_7', 'total_rech_num_8',
        ]
        
        all_features = feature_columns + new_features
        available_features = [col for col in all_features if col in df.columns]
        
        X = df[available_features].copy()
        X = X.fillna(X.median())
        X = X.replace([np.inf, -np.inf], 0)
        
        # Feature Engineering
        if 'arpu_7' in X.columns and 'arpu_8' in X.columns:
            X['arpu_trend'] = (X['arpu_8'] - X['arpu_7']) / (X['arpu_7'] + 1e-10)
        
        if 'total_og_mou_7' in X.columns and 'total_og_mou_8' in X.columns:
            X['mou_trend'] = (X['total_og_mou_8'] - X['total_og_mou_7']) / (X['total_og_mou_7'] + 1e-10)
        
        if 'total_rech_amt_7' in X.columns and 'total_rech_amt_8' in X.columns:
            X['rech_trend'] = (X['total_rech_amt_8'] - X['total_rech_amt_7']) / (X['total_rech_amt_7'] + 1e-10)
        
        if 'total_ic_mou_8' in X.columns and 'total_og_mou_8' in X.columns:
            X['ic_og_ratio'] = X['total_ic_mou_8'] / (X['total_og_mou_8'] + 1e-10)
        
        if 'total_rech_amt_8' in X.columns and 'total_rech_num_8' in X.columns:
            X['avg_rech_value'] = X['total_rech_amt_8'] / (X['total_rech_num_8'] + 1e-10)
        
        print(f"✅ تم اختيار {len(X.columns)} ميزة")
        return X, list(X.columns)
    
    def preprocess(self, df):
        print("🔄 جاري معالجة البيانات...")
        X, features = self.select_features(df)
        
        print(" جاري التطبيع الأولي (RobustScaler)...")
        X_scaled = self.scaler.fit_transform(X)
        
        X_scaled = self._remove_outliers(X_scaled)
        
        print(f"📉 جاري تقليل الأبعاد إلى {self.n_components} بعداً...")
        X_pca = self.pca.fit_transform(X_scaled)
        explained_variance = self.pca.explained_variance_ratio_.sum()
        print(f"✅ التباين المفسر بواسطة PCA: {explained_variance:.2%}")
        
        print("📏 جاري التطبيع الثاني (StandardScaler) بعد PCA...")
        X_pca_scaled = self.pca_scaler.fit_transform(X_pca)
        
        return X_pca_scaled, X_scaled, features