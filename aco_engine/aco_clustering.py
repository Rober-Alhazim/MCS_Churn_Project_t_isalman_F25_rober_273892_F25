# aco_engine/aco_clustering.py
import numpy as np
from sklearn.cluster import KMeans
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class AntColonyClustering:
    """
    خوارزمية ACO محسّنة مع معاملات أفضل
    """
    
    def __init__(
        self, 
        n_clusters: int = 3, 
        n_ants: int = 15,  
        max_iter: int = 3,  
        evaporation_rate: float = 0.2,  # تقليل من 0.4 إلى 0.2 (فيرومون يبقى أطول)
        alpha: float = 2.0,  # زيادة من 1.0 إلى 2.0 (فيرومون أقوى)
        beta: float = 1.5,   # تقليل من 2.0 إلى 1.5 (مسافة أضعف)
        random_state: int = 42,
        convergence_threshold: float = 0.0001,
        exploration_rate: float = 0.2  # زيادة من 0.1 إلى 0.2 (استكشاف أكثر)
    ):
        self.n_clusters = n_clusters
        self.n_ants = n_ants
        self.max_iter = max_iter
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.random_state = random_state
        self.convergence_threshold = convergence_threshold
        self.exploration_rate = exploration_rate
        
        self.labels_: Optional[np.ndarray] = None
        self.cluster_centers_: Optional[np.ndarray] = None
        self.history_: List[Dict] = []
        
        np.random.seed(random_state)
    
    def _compute_inertia_vectorized(self, X: np.ndarray, labels: np.ndarray, 
                                     centers: np.ndarray) -> float:
        distances = np.sum((X - centers[labels]) ** 2, axis=1)
        return float(np.sum(distances))
    
    def _build_solution_vectorized(self, X: np.ndarray, centers: np.ndarray, 
                                    pheromone: np.ndarray) -> np.ndarray:
        n_samples = X.shape[0]
        
        distances = np.linalg.norm(X[:, np.newaxis] - centers, axis=2)
        distances = np.clip(distances, 1e-10, 1e10)
        heuristic = 1.0 / distances
        
        # Softmax مستقر
        log_probabilities = (
            self.alpha * np.log(np.clip(pheromone, 1e-10, None)) + 
            self.beta * np.log(heuristic)
        )
        
        log_probabilities -= log_probabilities.max(axis=1, keepdims=True)
        probabilities = np.exp(log_probabilities)
        
        row_sums = probabilities.sum(axis=1, keepdims=True)
        probabilities = probabilities / (row_sums + 1e-10)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        
        probabilities = np.nan_to_num(
            probabilities, 
            nan=1.0/self.n_clusters, 
            posinf=1.0/self.n_clusters, 
            neginf=0.0
        )
        
        # استكشاف عشوائي
        if np.random.random() < self.exploration_rate:
            labels = np.random.randint(0, self.n_clusters, n_samples)
        else:
            labels = np.array([
                np.random.choice(self.n_clusters, p=prob)
                for prob in probabilities
            ])
        
        return labels
    
    def _update_centers_vectorized(self, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
        centers = np.zeros((self.n_clusters, X.shape[1]))
        for k in range(self.n_clusters):
            mask = (labels == k)
            if mask.any():
                centers[k] = X[mask].mean(axis=0)
            else:
                centers[k] = X[np.random.choice(X.shape[0])]
        return centers
    
    def _initialize_with_kmeans_plus_noise(self, X: np.ndarray):
        print("📊 استخدام KMeans++ مع ضوضاء للاستكشاف...")
        
        kmeans = KMeans(
            n_clusters=self.n_clusters, 
            random_state=self.random_state, 
            n_init=5,  # تقليل من 10 إلى 5 (حل أقل مثالية)
            init='k-means++'
        )
        kmeans.fit(X)
        
        # ضوضاء أكبر (±20%)
        noise = np.random.normal(0, 0.2, kmeans.cluster_centers_.shape)
        initial_centers = kmeans.cluster_centers_ * (1 + noise)
        
        distances = np.linalg.norm(X[:, np.newaxis] - initial_centers, axis=2)
        initial_labels = np.argmin(distances, axis=1)
        
        inertia = self._compute_inertia_vectorized(X, initial_labels, initial_centers)
        
        print(f"   ✅ Inertia الابتدائي (KMeans + Noise): {inertia:.2e}")
        return initial_centers, initial_labels, inertia
    
    def fit(self, X: np.ndarray) -> 'AntColonyClustering':
        logger.info(f"🐜 بدء خوارزمية ACO المحسّنة...")
        n_samples, n_features = X.shape
        
        print(f"🐜 بدء خوارزمية مستعمرة النمل المحسّنة...")
        print(f"   عدد العينات: {n_samples:,}")
        print(f"   عدد الأبعاد: {n_features}")
        print(f"   عدد العناقيد: {self.n_clusters}")
        print(f"   عدد النمل: {self.n_ants}")
        print(f"   عدد التكرارات: {self.max_iter}")
        print(f"   معاملات ACO: alpha={self.alpha}, beta={self.beta}, evaporation={self.evaporation_rate}")
        print(f"   معدل الاستكشاف: {self.exploration_rate}")
        
        print("\n📊 الخطوة 1: التهيئة المبدئية...")
        best_centers, best_labels, best_inertia = self._initialize_with_kmeans_plus_noise(X)
        
        pheromone = np.ones((n_samples, self.n_clusters))
        prev_best_inertia = best_inertia
        
        print("\n🔄 الخطوة 2: بدء دورة النمل...")
        for iteration in range(self.max_iter):
            ant_labels = np.zeros((self.n_ants, n_samples), dtype=int)
            ant_inertias = np.zeros(self.n_ants)
            
            for ant in range(self.n_ants):
                ant_labels[ant] = self._build_solution_vectorized(X, best_centers, pheromone)
                ant_centers = self._update_centers_vectorized(X, ant_labels[ant])
                ant_inertias[ant] = self._compute_inertia_vectorized(X, ant_labels[ant], ant_centers)
            
            pheromone *= (1.0 - self.evaporation_rate)
            
            best_ant_idx = int(np.argmin(ant_inertias))
            for ant in range(self.n_ants):
                reward = 1.0 / (ant_inertias[ant] + 1e-10)
                for i in range(n_samples):
                    chosen_cluster = ant_labels[ant, i]
                    pheromone[i, chosen_cluster] += reward
            
            if ant_inertias[best_ant_idx] < best_inertia:
                improvement_pct = (best_inertia - ant_inertias[best_ant_idx]) / best_inertia * 100
                best_inertia = ant_inertias[best_ant_idx]
                best_labels = ant_labels[best_ant_idx].copy()
                best_centers = self._update_centers_vectorized(X, best_labels)
                print(f"   🎯 تحسن عند التكرار {iteration + 1}: {improvement_pct:.2f}% (Inertia: {best_inertia:.2e})")
            
            self.history_.append({
                'iteration': iteration + 1,
                'best_inertia': best_inertia
            })
            
            improvement = abs(prev_best_inertia - best_inertia) / (prev_best_inertia + 1e-10)
            if improvement < self.convergence_threshold and iteration > 30:
                print(f"\n⚡ Early Stopping عند التكرار {iteration + 1} (تحسن: {improvement:.6f})")
                break
            
            prev_best_inertia = best_inertia
            
            if (iteration + 1) % 20 == 0 or iteration == 0:
                print(f"   التكرار {iteration + 1}/{self.max_iter} - Inertia: {best_inertia:.2e}")
        
        self.labels_ = best_labels
        self.cluster_centers_ = best_centers
        
        print(f"\n✅ اكتمل التجميع!")
        print(f"   Inertia النهائية: {best_inertia:.2e}")
        print(f"   عدد التكرارات الفعلية: {len(self.history_)}")
        
        return self
    
    def get_cluster_sizes(self) -> Dict[int, int]:
        if self.labels_ is None:
            return {}
        unique, counts = np.unique(self.labels_, return_counts=True)
        return dict(zip(unique, counts))