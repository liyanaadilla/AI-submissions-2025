"""
ML Training Module for YSMAI Agent - Real Kaggle Dataset Version

Trains 3 ML models on real Kaggle datasets for enhanced fault detection:
1. Engine Fault Detection Data → Random Forest Classifier
2. NASA Bearing Dataset → Isolation Forest (Vibration Anomaly)
3. Hydraulic Systems Data → Linear Regression (Pressure Prediction)

Models are persisted as .pkl files for inference.
"""

import os
import json
import pickle
import numpy as np
from typing import Tuple, Dict, Any, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Optional ML Libraries
try:
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, mean_squared_error, r2_score, accuracy_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML libraries not available. Install with: pip install pandas scikit-learn")

# Kaggle Support
try:
    import kagglehub
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False
    print("⚠️  Kaggle integration not available. Install with: pip install kagglehub")


class MLModelTrainer:
    """
    Trains and manages ML models for enhanced YSMAI agent using real Kaggle datasets.
    
    Models:
    1. FaultDetector (Random Forest): Engine fault detection from real data
    2. VibrationDetector (Isolation Forest): Bearing anomaly detection
    3. PressurePredictor (Linear Regression): Hydraulic pressure prediction
    """
    
    def __init__(self, model_dir: str = None):
        """Initialize trainer."""
        if model_dir is None:
            # Use workspace root models directory
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            model_dir = os.path.join(workspace_root, "models")
        
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.fault_detector = None
        self.vibration_detector = None
        self.pressure_predictor = None
        
        self.training_history = {}
        self.is_trained = False
        
        self.fault_detector_path = os.path.join(model_dir, "fault_detector.pkl")
        self.vibration_detector_path = os.path.join(model_dir, "vibration_detector.pkl")
        self.pressure_predictor_path = os.path.join(model_dir, "pressure_predictor.pkl")
    
    # ========== DATASET LOADING ==========
    
    def load_engine_fault_data(self) -> Optional[pd.DataFrame]:
        """Load Engine Fault Detection data from Kaggle."""
        if not KAGGLE_AVAILABLE:
            print("⚠️  Kaggle not available, using synthetic data for Fault Detector")
            return None
        
        try:
            print("\n📥 Downloading Engine Fault Detection data from Kaggle...")
            df = kagglehub.load_dataset(
                "ziya07/engine-fault-detection-data",
                path=""
            )
            print(f"✓ Loaded {len(df)} records from Engine Fault Detection dataset")
            return df
        except Exception as e:
            print(f"⚠️  Failed to load from Kaggle: {e}")
            print("   Using synthetic data fallback...")
            return None
    
    def load_bearing_data(self) -> Optional[pd.DataFrame]:
        """Load NASA Bearing dataset from Kaggle."""
        if not KAGGLE_AVAILABLE:
            print("⚠️  Kaggle not available, using synthetic data for Vibration Detector")
            return None
        
        try:
            print("\n📥 Downloading NASA Bearing dataset from Kaggle...")
            path = kagglehub.dataset_download("vinayak123tyagi/bearing-dataset")
            print(f"✓ Downloaded to: {path}")
            
            # Load CSV files from the downloaded path
            csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
            if csv_files:
                df = pd.read_csv(os.path.join(path, csv_files[0]))
                print(f"✓ Loaded {len(df)} records from Bearing dataset")
                return df
            return None
        except Exception as e:
            print(f"⚠️  Failed to load from Kaggle: {e}")
            print("   Using synthetic data fallback...")
            return None
    
    def load_hydraulic_data(self) -> Optional[pd.DataFrame]:
        """Load Hydraulic Systems Condition Monitoring data from Kaggle."""
        if not KAGGLE_AVAILABLE:
            print("⚠️  Kaggle not available, using synthetic data for Pressure Predictor")
            return None
        
        try:
            print("\n📥 Downloading Hydraulic Systems dataset from Kaggle...")
            path = kagglehub.dataset_download("jjacostupa/condition-monitoring-of-hydraulic-systems")
            print(f"✓ Downloaded to: {path}")
            
            # Load data files
            csv_files = [f for f in os.listdir(path) if f.endswith('.txt') or f.endswith('.csv')]
            if csv_files:
                df = pd.read_csv(os.path.join(path, csv_files[0]), sep='\t' if csv_files[0].endswith('.txt') else ',')
                print(f"✓ Loaded {len(df)} records from Hydraulic Systems dataset")
                return df
            return None
        except Exception as e:
            print(f"⚠️  Failed to load from Kaggle: {e}")
            print("   Using synthetic data fallback...")
            return None
    
    # ========== SYNTHETIC DATA FALLBACK ==========
    
    def generate_synthetic_fault_data(self, n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic engine fault data."""
        print(f"   Generating {n_samples} synthetic fault detection samples...")
        
        X = np.random.rand(n_samples, 4) * np.array([3000, 80, 115, 50])  # RPM, Pressure, Temp, Vib
        
        # Fault rules: High temp + high vibration = fault
        y = ((X[:, 2] > 90) & (X[:, 3] > 30)).astype(int)
        
        return X, y
    
    def generate_synthetic_vibration_data(self, n_samples: int = 1000) -> np.ndarray:
        """Generate synthetic bearing vibration data."""
        print(f"   Generating {n_samples} synthetic vibration detection samples...")
        
        # 90% normal, 10% anomalous
        normal_count = int(n_samples * 0.9)
        anomaly_count = n_samples - normal_count
        
        normal_data = np.random.normal(5, 2, (normal_count, 2))
        anomaly_data = np.random.normal(25, 5, (anomaly_count, 2))
        
        return np.vstack([normal_data, anomaly_data])
    
    def generate_synthetic_pressure_data(self, n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic pressure prediction data."""
        print(f"   Generating {n_samples} synthetic pressure prediction samples...")
        
        X = np.random.rand(n_samples, 1) * 50  # Flow rate
        y = 30 + (X.flatten() * 0.8) + np.random.normal(0, 5, n_samples)
        
        return X, y
    
    # ========== DATA PREPARATION ==========
    
    def prepare_fault_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare fault detection training data from Kaggle or synthetic."""
        df = self.load_engine_fault_data()
        
        if df is not None:
            try:
                # Map common column names
                column_mapping = {
                    'rpm': ['engine_speed', 'rpm', 'speed'],
                    'pressure': ['oil_pressure', 'pressure', 'lubrication_oil_pressure'],
                    'temp': ['coolant_temperature', 'temperature', 'temp'],
                    'vibration': ['vibration', 'engine_vibration'],
                    'fault': ['fault', 'target', 'label', 'is_fault']
                }
                
                cols = {k: None for k in column_mapping}
                for target, options in column_mapping.items():
                    for col in df.columns:
                        if any(opt.lower() in col.lower() for opt in options):
                            cols[target] = col
                            break
                
                if all(cols.values()):
                    X = df[[cols['rpm'], cols['pressure'], cols['temp'], cols['vibration']]].values
                    y = df[cols['fault']].astype(int).values
                    
                    print(f"✓ Prepared {len(X)} real fault detection samples from Kaggle")
                    return X, y
            except Exception as e:
                print(f"⚠️  Error preparing Kaggle data: {e}")
        
        return self.generate_synthetic_fault_data()
    
    def prepare_vibration_data(self) -> np.ndarray:
        """Prepare vibration detection training data from Kaggle or synthetic."""
        df = self.load_bearing_data()
        
        if df is not None:
            try:
                # Look for bearing columns
                bearing_cols = [col for col in df.columns if 'bearing' in col.lower()]
                if len(bearing_cols) >= 2:
                    X = df[bearing_cols[:2]].values
                    print(f"✓ Prepared {len(X)} real vibration detection samples from Kaggle")
                    return X
            except Exception as e:
                print(f"⚠️  Error preparing Kaggle data: {e}")
        
        return self.generate_synthetic_vibration_data()
    
    def prepare_pressure_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare pressure prediction training data from Kaggle or synthetic."""
        df = self.load_hydraulic_data()
        
        if df is not None:
            try:
                # Look for flow and pressure columns
                flow_cols = [col for col in df.columns if 'flow' in col.lower() or 'fs' in col.lower()]
                pressure_cols = [col for col in df.columns if 'pressure' in col.lower() or 'ps' in col.lower()]
                
                if flow_cols and pressure_cols:
                    X = df[flow_cols[0]].values.reshape(-1, 1)
                    y = df[pressure_cols[0]].values
                    
                    print(f"✓ Prepared {len(X)} real pressure prediction samples from Kaggle")
                    return X, y
            except Exception as e:
                print(f"⚠️  Error preparing Kaggle data: {e}")
        
        return self.generate_synthetic_pressure_data()
    
    # ========== MODEL TRAINING ==========
    
    def train_fault_detector(self) -> Dict[str, Any]:
        """Train Random Forest fault detector."""
        print("\n🔧 Training Fault Detector (Random Forest)...")
        
        X, y = self.prepare_fault_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.fault_detector = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.fault_detector.fit(X_train, y_train)
        
        train_acc = accuracy_score(y_train, self.fault_detector.predict(X_train))
        test_acc = accuracy_score(y_test, self.fault_detector.predict(X_test))
        
        self._save_model(self.fault_detector, self.fault_detector_path)
        
        result = {
            'model': 'Fault Detector',
            'type': 'Random Forest',
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'n_samples': len(X),
            'n_features': X.shape[1]
        }
        
        print(f"  Training Accuracy:  {train_acc:.4f}")
        print(f"  Testing Accuracy:   {test_acc:.4f}")
        print(f"  Samples: {len(X)} | Features: {X.shape[1]}")
        
        return result
    
    def train_vibration_detector(self) -> Dict[str, Any]:
        """Train Isolation Forest vibration anomaly detector."""
        print("\n🔧 Training Vibration Detector (Isolation Forest)...")
        
        X = self.prepare_vibration_data()
        
        self.vibration_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_jobs=-1
        )
        
        self.vibration_detector.fit(X)
        
        predictions = self.vibration_detector.predict(X)
        anomaly_count = np.sum(predictions == -1)
        anomaly_rate = anomaly_count / len(X)
        
        self._save_model(self.vibration_detector, self.vibration_detector_path)
        
        result = {
            'model': 'Vibration Detector',
            'type': 'Isolation Forest',
            'n_samples': len(X),
            'anomalies_detected': int(anomaly_count),
            'anomaly_rate': anomaly_rate,
            'n_features': X.shape[1]
        }
        
        print(f"  Total Samples:      {len(X)}")
        print(f"  Anomalies Detected: {anomaly_count} ({anomaly_rate:.1%})")
        print(f"  Features: {X.shape[1]}")
        
        return result
    
    def train_pressure_predictor(self) -> Dict[str, Any]:
        """Train Linear Regression pressure predictor."""
        print("\n🔧 Training Pressure Predictor (Linear Regression)...")
        
        X, y = self.prepare_pressure_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.pressure_predictor = LinearRegression()
        self.pressure_predictor.fit(X_train, y_train)
        
        train_rmse = np.sqrt(mean_squared_error(y_train, self.pressure_predictor.predict(X_train)))
        test_rmse = np.sqrt(mean_squared_error(y_test, self.pressure_predictor.predict(X_test)))
        train_r2 = r2_score(y_train, self.pressure_predictor.predict(X_train))
        test_r2 = r2_score(y_test, self.pressure_predictor.predict(X_test))
        
        self._save_model(self.pressure_predictor, self.pressure_predictor_path)
        
        result = {
            'model': 'Pressure Predictor',
            'type': 'Linear Regression',
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'n_samples': len(X),
            'n_features': X.shape[1]
        }
        
        print(f"  Training R²:        {train_r2:.4f}")
        print(f"  Testing R²:         {test_r2:.4f}")
        print(f"  Training RMSE:      {train_rmse:.2f} PSI")
        print(f"  Testing RMSE:       {test_rmse:.2f} PSI")
        print(f"  Samples: {len(X)} | Features: {X.shape[1]}")
        
        return result
    
    def train_all_models(self) -> Dict[str, Any]:
        """Train all models and return results."""
        if not ML_AVAILABLE:
            print("❌ ML libraries not available. Cannot train models.")
            return {}
        
        print("=" * 60)
        print("YSMAI ML Model Training - Kaggle Datasets")
        print("=" * 60)
        print(f"Kaggle integration: {'✓ Available' if KAGGLE_AVAILABLE else '✗ Not available (synthetic data)'}")
        
        results = {}
        
        try:
            results['fault_detector'] = self.train_fault_detector()
        except Exception as e:
            print(f"❌ Error training Fault Detector: {e}")
        
        try:
            results['vibration_detector'] = self.train_vibration_detector()
        except Exception as e:
            print(f"❌ Error training Vibration Detector: {e}")
        
        try:
            results['pressure_predictor'] = self.train_pressure_predictor()
        except Exception as e:
            print(f"❌ Error training Pressure Predictor: {e}")
        
        self.training_history = results
        self.is_trained = True
        
        self._save_training_report(results)
        
        print("\n" + "=" * 60)
        print("✓ Training Complete")
        print("=" * 60)
        
        return results
    
    # ========== INFERENCE ==========
    
    def predict_fault(self, rpm: float, pressure: float, temp: float, vib: float) -> Dict[str, Any]:
        """Predict fault from sensor data."""
        if self.fault_detector is None:
            self.load_all_models()
        
        # Use simple heuristic if model not available
        if self.fault_detector is None:
            # Fault detection: high temp + high vibration = fault
            fault_detected = (temp > 90) and (vib > 30)
            confidence = min(0.95, (temp / 120.0) * (vib / 50.0)) if fault_detected else max(0.0, 1.0 - (temp / 100.0))
            return {
                'fault': fault_detected,
                'confidence': float(confidence)
            }
        
        try:
            X = np.array([[rpm, pressure, temp, vib]])
            prediction = self.fault_detector.predict(X)[0]
            confidence = np.max(self.fault_detector.predict_proba(X)[0])
            
            return {
                'fault': bool(prediction),
                'confidence': float(confidence)
            }
        except Exception as e:
            return {'fault': False, 'confidence': 0.0, 'error': str(e)}
    
    def detect_vibration_anomaly(self, bearing_1: float, bearing_2: float) -> Dict[str, Any]:
        """Detect vibration anomalies."""
        if self.vibration_detector is None:
            self.load_all_models()
        
        # Use simple heuristic if model not available
        if self.vibration_detector is None:
            # Vibration anomaly: if values are too high or unusual
            anomaly_detected = (bearing_1 > 20) or (bearing_2 > 20)
            score = max(bearing_1, bearing_2) / 30.0
            return {
                'anomaly': anomaly_detected,
                'score': float(min(1.0, score))
            }
        
        try:
            X = np.array([[bearing_1, bearing_2]])
            prediction = self.vibration_detector.predict(X)[0]
            score = abs(self.vibration_detector.score_samples(X)[0])
            
            return {
                'anomaly': bool(prediction == -1),
                'score': float(score)
            }
        except Exception as e:
            return {'anomaly': False, 'score': 0.0, 'error': str(e)}
    
    def predict_pressure(self, flow_rate: float) -> Dict[str, Any]:
        """Predict pressure from flow rate."""
        if self.pressure_predictor is None:
            self.load_all_models()
        
        # Use simple linear model if not available
        if self.pressure_predictor is None:
            # Simple heuristic: pressure = base + (flow * coefficient)
            predicted_pressure = 30 + (flow_rate * 0.8) + np.random.normal(0, 2)
            return {
                'predicted_pressure': float(max(0, predicted_pressure)),
                'flow_rate': float(flow_rate)
            }
        
        try:
            X = np.array([[flow_rate]])
            prediction = self.pressure_predictor.predict(X)[0]
            
            return {
                'predicted_pressure': float(prediction),
                'flow_rate': float(flow_rate)
            }
        except Exception as e:
            return {'predicted_pressure': 0.0, 'error': str(e)}
    
    # ========== MODEL PERSISTENCE ==========
    
    def _save_model(self, model: Any, path: str) -> None:
        """Save model to disk."""
        try:
            with open(path, 'wb') as f:
                pickle.dump(model, f)
        except Exception as e:
            print(f"⚠️  Failed to save model: {e}")
    
    def _save_training_report(self, results: Dict[str, Any]) -> None:
        """Save training report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'kaggle_available': KAGGLE_AVAILABLE
        }
        
        report_path = os.path.join(self.model_dir, "training_report.json")
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✓ Training report saved to {report_path}")
        except Exception as e:
            print(f"⚠️  Failed to save training report: {e}")
    
    def load_all_models(self) -> bool:
        """Load all models from disk."""
        try:
            with open(self.fault_detector_path, 'rb') as f:
                self.fault_detector = pickle.load(f)
            with open(self.vibration_detector_path, 'rb') as f:
                self.vibration_detector = pickle.load(f)
            with open(self.pressure_predictor_path, 'rb') as f:
                self.pressure_predictor = pickle.load(f)
            
            self.is_trained = True
            return True
        except FileNotFoundError:
            # Models not trained yet - will use synthetic fallbacks
            return False
        except Exception as e:
            # Other errors also fall back to synthetic
            return False


if __name__ == "__main__":
    print("YSMAI ML Training Module")
    print("This module requires: pip install pandas scikit-learn")
    print("For Kaggle datasets: pip install kagglehub")
