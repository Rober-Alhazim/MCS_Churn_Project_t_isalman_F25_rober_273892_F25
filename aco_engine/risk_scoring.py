# aco_engine/risk_scoring.py
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class RiskScorer:
    def __init__(self):
        self.risk_levels = ['Low Risk', 'Medium Risk', 'High Risk']
        self.cluster_risk_mapping = {}
    
    def _profile_clusters(self, df, cluster_labels):
        """
        تحليل خصائص كل عنقود وتحديد مستوى الخطورة
        باستخدام مؤشر مركب (Composite Risk Index)
        """
        df_temp = df.copy()
        df_temp['cluster_id'] = cluster_labels
        
        # حساب مؤشرات التراجع
        df_temp['arpu_decline'] = (df_temp['arpu_8'] - df_temp['arpu_7']).fillna(0)
        df_temp['mou_decline'] = (df_temp['total_og_mou_8'] - df_temp['total_og_mou_7']).fillna(0)
        df_temp['rech_decline'] = (df_temp['total_rech_amt_8'] - df_temp['total_rech_amt_7']).fillna(0)
        
        # حساب متوسط المؤشرات لكل عنقود
        cluster_profiles = df_temp.groupby('cluster_id').agg({
            'arpu_8': 'mean',
            'total_og_mou_8': 'mean',
            'total_rech_amt_8': 'mean',
            'arpu_decline': 'mean',
            'mou_decline': 'mean',
            'rech_decline': 'mean'
        }).reset_index()
        
        print("\n📊 تحليل خصائص العناقيد (Cluster Profiling):")
        print(cluster_profiles)
        
        # ✅ حساب مؤشر الخطورة المركب (Composite Risk Index)
        # كل عامل يساهم بنسبة معينة في الخطورة
        # التطبيع (Normalization) لجعل القيم قابلة للمقارنة
        
        # 1. تطبيع ARPU (أقل = أخطر)
        arpu_min, arpu_max = cluster_profiles['arpu_8'].min(), cluster_profiles['arpu_8'].max()
        cluster_profiles['arpu_risk'] = 1 - (cluster_profiles['arpu_8'] - arpu_min) / (arpu_max - arpu_min + 1e-10)
        
        # 2. تطبيع MOU (أقل = أخطر)
        mou_min, mou_max = cluster_profiles['total_og_mou_8'].min(), cluster_profiles['total_og_mou_8'].max()
        cluster_profiles['mou_risk'] = 1 - (cluster_profiles['total_og_mou_8'] - mou_min) / (mou_max - mou_min + 1e-10)
        
        # 3. تطبيع ARPU Decline (تراجع أكبر = أخطر)
        decline_min, decline_max = cluster_profiles['arpu_decline'].min(), cluster_profiles['arpu_decline'].max()
        cluster_profiles['decline_risk'] = (cluster_profiles['arpu_decline'] - decline_min) / (decline_max - decline_min + 1e-10)
        cluster_profiles['decline_risk'] = 1 - cluster_profiles['decline_risk']  # عكس: التراجع السلبي = خطر أعلى
        
        # 4. حساب المؤشر المركب (أوزان مختلفة)
        cluster_profiles['composite_risk'] = (
            0.4 * cluster_profiles['arpu_risk'] +      # ARPU الحالي (40%)
            0.3 * cluster_profiles['mou_risk'] +        # MOU الحالي (30%)
            0.3 * cluster_profiles['decline_risk']      # التراجع (30%)
        )
        
        print("\n📈 مؤشر الخطورة المركب لكل عنقود:")
        print(cluster_profiles[['cluster_id', 'composite_risk', 'arpu_risk', 'mou_risk', 'decline_risk']])
        
        # ترتيب العناقيد حسب الخطورة
        cluster_profiles = cluster_profiles.sort_values('composite_risk', ascending=False)
        
        # تعيين المستويات
        if len(cluster_profiles) >= 3:
            self.cluster_risk_mapping = {
                cluster_profiles.iloc[0]['cluster_id']: 'High Risk',
                cluster_profiles.iloc[1]['cluster_id']: 'Medium Risk',
                cluster_profiles.iloc[2]['cluster_id']: 'Low Risk'
            }
        elif len(cluster_profiles) == 2:
            self.cluster_risk_mapping = {
                cluster_profiles.iloc[0]['cluster_id']: 'High Risk',
                cluster_profiles.iloc[1]['cluster_id']: 'Low Risk'
            }
        
        print(f"\n🎯 تعيين مستويات الخطورة:")
        for cluster_id, risk_level in self.cluster_risk_mapping.items():
            print(f"   العنقود {cluster_id} -> {risk_level}")
        
        return self.cluster_risk_mapping
    
    def calculate_risk_scores(self, df, cluster_labels):
        """
        حساب درجات الخطورة بناءً على تحليل العناقيد
        """
        # 1. تحليل العناقيد وتحديد المستويات
        risk_mapping = self._profile_clusters(df, cluster_labels)
        
        # 2. إنشاء DataFrame النتائج
        results = pd.DataFrame()
        results['id'] = df['id'].values
        results['cluster_id'] = cluster_labels
        
        # حساب مؤشرات التراجع
        results['arpu_decline'] = (df['arpu_8'] - df['arpu_7']).fillna(0)
        results['mou_decline'] = (df['total_og_mou_8'] - df['total_og_mou_7']).fillna(0)
        results['rech_decline'] = (df['total_rech_amt_8'] - df['total_rech_amt_7']).fillna(0)
        
        # 3. تعيين مستويات الخطورة
        results['risk_level'] = results['cluster_id'].map(risk_mapping).fillna('Low Risk')
        
        # 4. حساب Risk Score لكل عميل (0-100)
        results['risk_score'] = 0.0
        
        for risk_level in ['High Risk', 'Medium Risk', 'Low Risk']:
            mask = results['risk_level'] == risk_level
            if mask.any():
                if risk_level == 'High Risk':
                    base, max_score = 70, 30
                elif risk_level == 'Medium Risk':
                    base, max_score = 40, 30
                else:
                    base, max_score = 0, 40
                
                # حساب الدرجة بناءً على التراجع
                decline_factor = (
                    0.4 * np.clip(-results.loc[mask, 'arpu_decline'] / 50, 0, 1) +
                    0.3 * np.clip(results.loc[mask, 'mou_decline'] / 200, 0, 1) +
                    0.3 * np.clip(results.loc[mask, 'rech_decline'] / 100, 0, 1)
                )
                
                results.loc[mask, 'risk_score'] = base + (max_score * decline_factor)
        
        return results
    
    def get_high_risk_customers(self, results, threshold=66):
        high_risk = results[results['risk_level'] == 'High Risk']
        return high_risk.sort_values('risk_score', ascending=False)
    
    def get_risk_distribution(self, results):
        distribution = results['risk_level'].value_counts()
        ordered_levels = [lvl for lvl in self.risk_levels if lvl in distribution.index]
        distribution = distribution.reindex(ordered_levels).fillna(0).astype(int)
        percentages = (distribution / len(results)) * 100
        return distribution, percentages