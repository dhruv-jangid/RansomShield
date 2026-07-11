import joblib
import os
import numpy as np
import warnings
warnings.filterwarnings("ignore")

class MLDetector:
    def __init__(self, model_path="./"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self._load()

    def _load(self):
        try:
            model_file = os.path.join(self.model_path, "ransomware_model.pkl")
            scaler_file = os.path.join(self.model_path, "scaler.pkl")
            if os.path.exists(model_file) and os.path.exists(scaler_file):
                self.model = joblib.load(model_file)
                self.model.n_jobs = 1
                for est in self.model.estimators_:
                    est.n_jobs = 1
                self.scaler = joblib.load(scaler_file)
                print("[MLDetector] Loaded model + scaler from", self.model_path)
            else:
                print("[MLDetector] WARNING: model files not found")
        except Exception as e:
            print(f"[MLDetector] ERROR: {e}")

    def predict(self, features):
        try:
            if self.model is None or self.scaler is None:
                return "UNKNOWN", 0
            x = np.array(features, dtype=np.float64).reshape(1, -1)
            x_scaled = self.scaler.transform(x)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pred = self.model.predict(x_scaled)[0]
                proba = self.model.predict_proba(x_scaled)[0]
            confidence = int(max(proba) * 100)
            labels = {0:"NORMAL", 1:"WANNACRY", 2:"LOCKBIT", 3:"RYUK", 4:"PETYA"}
            return labels.get(int(pred), "UNKNOWN"), confidence
        except Exception as e:
            print(f"[MLDetector] predict error: {e}")
            return "UNKNOWN", 0
