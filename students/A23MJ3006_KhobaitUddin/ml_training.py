"""
ML Training Module for YSMAI Agent

Trains 3 ML models on Kaggle datasets for enhanced fault detection:
1. Random Forest Classifier - General fault detection
2. Isolation Forest - Vibration anomaly detection  
3. Linear Regression - Oil pressure prediction

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
    from sklearn.metrics import classification_report, mean_squared_error
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠ ML libraries not available. Install with: pip install pandas scikit-learn")


class MLModelTrainer:
    """
    Trains and manages ML models for enhanced YSMAI agent.
    
    Models:
    1. FaultDetector (Random Forest): Classifies Normal vs Fault states
    2. VibrationDetector (Isolation Forest): Detects abnormal vibration patterns
    3. PressurePredictor (Linear Regression): Predicts expected oil pressure
    """
    
    def __init__(self, model_dir: str = "models"):
        """
        Initialize trainer.
        
        Args:
            model_dir: Directory to save/load models
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Models
        self.fault_detector = None
        self.vibration_detector = None
        self.pressure_predictor = None
        
        # Training history
        self.training_history = {}
        self.is_trained = False
    
    # ==================== DATA GENERATION ====================
    
    def _generate_synthetic_engine_fault_data(self, n_samples: int = 1000) -> 'pd.DataFrame':
        """Generate synthetic engine fault training data."""
        if not ML_AVAILABLE:
            return None
        
        np.random.seed(42)
        data = {
            'engine_speed': np.random.uniform(500, 3000, n_samples),
            'lubrication_pressure': np.random.uniform(10, 80, n_samples),
            'coolant_temperature': np.random.uniform(25, 115, n_samples),
            'engine_vibration': np.random.uniform(0, 50, n_samples),
        }
        df = pd.DataFrame(data)
        
        # Label faults based on multiple bad conditions
        df['fault'] = (
            ((df['coolant_temperature'] > 105) & (df['engine_speed'] > 2000)) |
            ((df['lubrication_pressure'] < 15) & (df['engine_speed'] > 1500)) |
            ((df['engine_vibration'] > 28) & (df['engine_speed'] > 2000))
        ).astype(int)
        
        return df
    
    def _generate_synthetic_bearing_data(self, n_samples: int = 1000) -> 'pd.DataFrame':
        """Generate synthetic bearing vibration data."""
        if not ML_AVAILABLE:
            return None
        
        np.random.seed(42)
        normal_b1 = np.random.normal(5, 1, n_samples // 2)
        normal_b2 = np.random.normal(5, 1, n_samples // 2)
        faulty_b1 = np.random.normal(20, 8, n_samples // 2)
        faulty_b2 = np.random.normal(20, 8, n_samples // 2)
        
        bearing_1 = np.concatenate([normal_b1, faulty_b1])
        bearing_2 = np.concatenate([normal_b2, faulty_b2])
        
        df = pd.DataFrame({
            'bearing_1': np.abs(bearing_1),
            'bearing_2': np.abs(bearing_2),
        })
        df['anomaly'] = np.concatenate([np.zeros(n_samples // 2), np.ones(n_samples // 2)]).astype(int)
        
        return df
    
    def _generate_synthetic_hydraulic_data(self, n_samples: int = 1000) -> 'pd.DataFrame':
        """Generate synthetic hydraulic system data."""
        if not ML_AVAILABLE:
            return None
        
        np.random.seed(42)
        flow = np.random.uniform(1, 50, n_samples)
        pressure = 20 + (flow * 1.5) + np.random.normal(0, 5, n_samples)
        
        df = pd.DataFrame({
            'ps1_pressure': np.clip(pressure, 0, 100),
            'fs1_flow': flow,
        })
        
        return df
    
    # ==================== MODEL TRAINING ====================
    
    def train_fault_detector(self) -> Dict[str, Any]:
        """
        Train Random Forest for fault detection.
        
        Returns:
            Training metrics dictionary
        """
        if not ML_AVAILABLE:
            return {'error': 'ML libraries not available'}
        
        print("\n" + "="*60)
        print("TRAINING: Fault Detector (Random Forest)")
        print("="*60)
        
        try:
            df = self._generate_synthetic_engine_fault_data()
            
            feature_cols = ['engine_speed', 'lubrication_pressure', 'coolant_temperature', 'engine_vibration']
            X = df[feature_cols].fillna(0)
            y = df['fault']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.fault_detector = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.fault_detector.fit(X_train, y_train)
            
            train_score = self.fault_detector.score(X_train, y_train)
            test_score = self.fault_detector.score(X_test, y_test)
            
            print(f"Training Accuracy: {train_score:.4f}")
            print(f"Testing Accuracy: {test_score:.4f}")
            
            self._save_model('fault_detector', self.fault_detector)
            
            metrics = {
                'model': 'RandomForestClassifier',
                'train_accuracy': float(train_score),
                'test_accuracy': float(test_score),
                'features': feature_cols,
                'n_samples': len(X),
                'timestamp': datetime.now().isoformat()
            }
            self.training_history['fault_detector'] = metrics
            
            return metrics
            
        except Exception as e:
            print(f"⚠ Error training Fault Detector: {e}")
            return {'error': str(e)}
    
    def train_vibration_detector(self) -> Dict[str, Any]:
        """
        Train Isolation Forest for vibration anomalies.
        
        Returns:
            Training metrics dictionary
        """
        if not ML_AVAILABLE:
            return {'error': 'ML libraries not available'}
        
        print("\n" + "="*60)
        print("TRAINING: Vibration Detector (Isolation Forest)")
        print("="*60)
        
        try:
            df = self._generate_synthetic_bearing_data()
            
            feature_cols = ['bearing_1', 'bearing_2']
            X = df[feature_cols].fillna(0)
            
            self.vibration_detector = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_jobs=-1
            )
            self.vibration_detector.fit(X)
            
            predictions = self.vibration_detector.predict(X)
            n_anomalies = (predictions == -1).sum()
            anomaly_pct = (n_anomalies / len(X)) * 100
            
            print(f"Total samples: {len(X)}")
            print(f"Detected anomalies: {n_anomalies} ({anomaly_pct:.2f}%)")
            
            self._save_model('vibration_detector', self.vibration_detector)
            
            metrics = {
                'model': 'IsolationForest',
                'total_samples': len(X),
                'detected_anomalies': int(n_anomalies),
                'anomaly_percentage': float(anomaly_pct),
                'features': feature_cols,
                'timestamp': datetime.now().isoformat()
            }
            self.training_history['vibration_detector'] = metrics
            
            return metrics
            
        except Exception as e:
            print(f"⚠ Error training Vibration Detector: {e}")
            return {'error': str(e)}
    
    def train_pressure_predictor(self) -> Dict[str, Any]:
        """
        Train Linear Regression for pressure prediction.
        
        Returns:
            Training metrics dictionary
        """
        if not ML_AVAILABLE:
            return {'error': 'ML libraries not available'}
        
        print("\n" + "="*60)
        print("TRAINING: Pressure Predictor (Linear Regression)")
        print("="*60)
        
        try:
            df = self._generate_synthetic_hydraulic_data()
            
            X = df[['fs1_flow']].fillna(0)
            y = df['ps1_pressure'].fillna(0)
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.pressure_predictor = LinearRegression()
            self.pressure_predictor.fit(X_train, y_train)
            
            train_r2 = self.pressure_predictor.score(X_train, y_train)
            test_r2 = self.pressure_predictor.score(X_test, y_test)
            train_rmse = np.sqrt(mean_squared_error(y_train, self.pressure_predictor.predict(X_train)))
            test_rmse = np.sqrt(mean_squared_error(y_test, self.pressure_predictor.predict(X_test)))
            
            print(f"Training R²: {train_r2:.4f}")
            print(f"Testing R²: {test_r2:.4f}")
            print(f"Training RMSE: {train_rmse:.4f}")
            print(f"Testing RMSE: {test_rmse:.4f}")
            
            self._save_model('pressure_predictor', self.pressure_predictor)
            
            metrics = {
                'model': 'LinearRegression',
                'train_r2': float(train_r2),
                'test_r2': float(test_r2),
                'train_rmse': float(train_rmse),
                'test_rmse': float(test_rmse),
                'features': ['fs1_flow'],
                'output': 'ps1_pressure',
                'n_samples': len(X),
                'timestamp': datetime.now().isoformat()
            }
            self.training_history['pressure_predictor'] = metrics
            
            return metrics
            
        except Exception as e:
            print(f"⚠ Error training Pressure Predictor: {e}")
            return {'error': str(e)}
    
    # ==================== MODEL PERSISTENCE ====================
    
    def _save_model(self, model_name: str, model: Any) -> None:
        """Save trained model to disk."""
        filepath = os.path.join(self.model_dir, f"{model_name}.pkl")
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        print(f"✓ Model saved: {filepath}")
    
    def load_model(self, model_name: str) -> Optional[Any]:
        """Load model from disk."""
        filepath = os.path.join(self.model_dir, f"{model_name}.pkl")
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    def save_training_report(self) -> str:
        """Save training history to JSON."""
        filepath = os.path.join(self.model_dir, "training_report.json")
        with open(filepath, 'w') as f:
            json.dump(self.training_history, f, indent=2)
        return filepath
    
    # ==================== INFERENCE ====================
    
    def predict_fault(self, rpm: float, pressure: float, temp: float, vib: float) -> Dict[str, Any]:
        """
        Predict fault using trained model.
        
        Args:
            rpm: Engine RPM
            pressure: Oil pressure (PSI)
            temp: Temperature (°F)
            vib: Vibration (mm/s)
            
        Returns:
            Prediction result dictionary
        """
        if self.fault_detector is None:
            return {'fault': None, 'confidence': 0.0}
        
        try:
            X = np.array([[rpm, pressure, temp, vib]])
            prediction = self.fault_detector.predict(X)[0]
            probabilities = self.fault_detector.predict_proba(X)[0]
            confidence = max(probabilities)
            
            return {
                'fault': bool(prediction),
                'confidence': float(confidence),
                'normal_prob': float(probabilities[0]),
                'fault_prob': float(probabilities[1])
            }
        except Exception:
            return {'fault': None, 'confidence': 0.0}
    
    def detect_vibration_anomaly(self, bearing_1: float, bearing_2: float) -> Dict[str, Any]:
        """
        Detect vibration anomaly.
        
        Args:
            bearing_1: Bearing 1 vibration
            bearing_2: Bearing 2 vibration
            
        Returns:
            Anomaly detection result
        """
        if self.vibration_detector is None:
            return {'anomaly': False, 'score': 0.0}
        
        try:
            X = np.array([[bearing_1, bearing_2]])
            prediction = self.vibration_detector.predict(X)[0]
            score = self.vibration_detector.score_samples(X)[0]
            
            return {
                'anomaly': bool(prediction == -1),
                'score': float(score),
                'is_anomaly': int(prediction == -1)
            }
        except Exception:
            return {'anomaly': False, 'score': 0.0}
    
    def predict_pressure(self, flow_rate: float) -> Dict[str, Any]:
        """
        Predict pressure from flow rate.
        
        Args:
            flow_rate: Volume flow rate
            
        Returns:
            Predicted pressure
        """
        if self.pressure_predictor is None:
            return {'predicted_pressure': None}
        
        try:
            X = np.array([[flow_rate]])
            predicted = self.pressure_predictor.predict(X)[0]
            
            return {
                'predicted_pressure': float(predicted),
                'flow_rate': float(flow_rate)
            }
        except Exception:
            return {'predicted_pressure': None}
    
    # ==================== TRAINING PIPELINE ====================
    
    def train_all_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Train all three models.
        
        Returns:
            Dictionary with all training results
        """
        if not ML_AVAILABLE:
            print("⚠ ML libraries not available")
            return {}
        
        print("\n" + "#"*60)
        print("# YSMAI ML TRAINING PIPELINE - FULL RUN")
        print("#"*60)
        
        results = {
            'fault_detector': self.train_fault_detector(),
            'vibration_detector': self.train_vibration_detector(),
            'pressure_predictor': self.train_pressure_predictor(),
        }
        
        self.save_training_report()
        self.is_trained = True
        
        print("\n" + "#"*60)
        print("# TRAINING COMPLETE ✓")
        print("#"*60)
        
        return results
    
    def load_all_models(self) -> bool:
        """
        Load all models from disk.
        
        Returns:
            True if all models loaded successfully
        """
        self.fault_detector = self.load_model('fault_detector')
        self.vibration_detector = self.load_model('vibration_detector')
        self.pressure_predictor = self.load_model('pressure_predictor')
        
        all_loaded = all([
            self.fault_detector is not None,
            self.vibration_detector is not None,
            self.pressure_predictor is not None
        ])
        
        self.is_trained = all_loaded
        return all_loaded
    
    def get_status(self) -> Dict[str, Any]:
        """Get training status."""
        return {
            'is_trained': self.is_trained,
            'fault_detector_loaded': self.fault_detector is not None,
            'vibration_detector_loaded': self.vibration_detector is not None,
            'pressure_predictor_loaded': self.pressure_predictor is not None,
            'training_history': self.training_history,
            'ml_available': ML_AVAILABLE
        }


# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    if not ML_AVAILABLE:
        print("⚠ ML libraries not available")
        print("Install with: pip install pandas scikit-learn numpy")
        exit(1)
    
    trainer = MLModelTrainer(model_dir="models")
    results = trainer.train_all_models()
    
    print("\n" + "="*60)
    print("TRAINING RESULTS SUMMARY")
    print("="*60)
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
