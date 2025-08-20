"""
AI Predictor Module
Uses machine learning to predict system performance issues
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import joblib
import os
from typing import Dict, Optional, List
import warnings
warnings.filterwarnings('ignore')

class AIPredictor:
    def __init__(self, data_handler):
        self.data_handler = data_handler
        self.performance_model = None
        self.slowdown_classifier = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'cpu_percent', 'memory_percent', 'disk_percent',
            'memory_used_gb', 'network_bytes_sent', 'network_bytes_recv',
            'uptime_hours', 'cpu_count', 'cpu_freq'
        ]
        
        # Load existing models if available
        self.load_models()
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for machine learning"""
        if data.empty:
            return pd.DataFrame()
            
        # Ensure all required columns exist
        for col in self.feature_columns:
            if col not in data.columns:
                data[col] = 0
                
        # Create time-based features
        data['hour'] = pd.to_datetime(data['timestamp'], unit='s').dt.hour
        data['day_of_week'] = pd.to_datetime(data['timestamp'], unit='s').dt.dayofweek
        
        # Create rolling averages
        window_size = min(5, len(data))
        if window_size > 1:
            data['cpu_rolling_avg'] = data['cpu_percent'].rolling(window=window_size, min_periods=1).mean()
            data['memory_rolling_avg'] = data['memory_percent'].rolling(window=window_size, min_periods=1).mean()
            data['disk_rolling_avg'] = data['disk_percent'].rolling(window=window_size, min_periods=1).mean()
        else:
            data['cpu_rolling_avg'] = data['cpu_percent']
            data['memory_rolling_avg'] = data['memory_percent']
            data['disk_rolling_avg'] = data['disk_percent']
            
        # Create trend features
        if len(data) > 2:
            data['cpu_trend'] = data['cpu_percent'].diff().fillna(0)
            data['memory_trend'] = data['memory_percent'].diff().fillna(0)
        else:
            data['cpu_trend'] = 0
            data['memory_trend'] = 0
            
        # Create load indicators
        data['high_cpu_load'] = (data['cpu_percent'] > 80).astype(int)
        data['high_memory_load'] = (data['memory_percent'] > 85).astype(int)
        data['high_disk_load'] = (data['disk_percent'] > 90).astype(int)
        
        # System stress indicator
        data['system_stress'] = (
            data['cpu_percent'] * 0.4 + 
            data['memory_percent'] * 0.4 + 
            data['disk_percent'] * 0.2
        )
        
        return data
        
    def create_target_variables(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create target variables for prediction"""
        if len(data) < 2:
            return data
            
        # Predict future performance (next data point)
        data['future_cpu'] = data['cpu_percent'].shift(-1)
        data['future_memory'] = data['memory_percent'].shift(-1)
        data['future_system_stress'] = data['system_stress'].shift(-1)
        
        # Create slowdown indicator (high resource usage)
        data['slowdown_risk'] = (
            (data['future_cpu'] > 85) | 
            (data['future_memory'] > 90) |
            (data['future_system_stress'] > 85)
        ).astype(int)
        
        return data
        
    def train_models(self) -> bool:
        """Train the AI models with available data"""
        try:
            # Get training data
            raw_data = self.data_handler.get_training_data()
            if raw_data.empty or len(raw_data) < 10:
                print("Insufficient data for training")
                return False
                
            # Prepare features
            data = self.prepare_features(raw_data)
            data = self.create_target_variables(data)
            
            # Remove rows with NaN targets
            data = data.dropna(subset=['future_cpu', 'future_memory', 'slowdown_risk'])
            
            if len(data) < 5:
                print("Insufficient clean data for training")
                return False
                
            # Define feature columns for training
            feature_cols = self.feature_columns + [
                'hour', 'day_of_week', 'cpu_rolling_avg', 'memory_rolling_avg', 
                'disk_rolling_avg', 'cpu_trend', 'memory_trend', 'high_cpu_load',
                'high_memory_load', 'high_disk_load', 'system_stress'
            ]
            
            X = data[feature_cols].fillna(0)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train performance regression model
            y_performance = data['future_system_stress'].fillna(0)
            if len(np.unique(y_performance)) > 1:
                self.performance_model = RandomForestRegressor(
                    n_estimators=50, 
                    max_depth=10, 
                    random_state=42,
                    n_jobs=-1
                )
                self.performance_model.fit(X_scaled, y_performance)
                
            # Train slowdown classification model
            y_slowdown = data['slowdown_risk'].fillna(0)
            if len(np.unique(y_slowdown)) > 1:
                self.slowdown_classifier = RandomForestClassifier(
                    n_estimators=50, 
                    max_depth=10, 
                    random_state=42,
                    n_jobs=-1
                )
                self.slowdown_classifier.fit(X_scaled, y_slowdown)
                
            self.is_trained = True
            self.save_models()
            print(f"Models trained successfully with {len(data)} samples")
            return True
            
        except Exception as e:
            print(f"Error training models: {e}")
            return False
            
    def get_predictions(self) -> Optional[Dict]:
        """Get AI predictions for system performance"""
        try:
            # Get recent data for prediction
            recent_data = self.data_handler.get_recent_data(limit=10)
            if recent_data.empty:
                return None
                
            # Retrain models if we have enough new data
            if not self.is_trained or len(recent_data) % 20 == 0:
                self.train_models()
                
            if not self.is_trained:
                return None
                
            # Prepare features for prediction
            data = self.prepare_features(recent_data)
            if data.empty:
                return None
                
            # Get the latest data point for prediction
            latest_data = data.iloc[-1:].copy()
            
            feature_cols = self.feature_columns + [
                'hour', 'day_of_week', 'cpu_rolling_avg', 'memory_rolling_avg', 
                'disk_rolling_avg', 'cpu_trend', 'memory_trend', 'high_cpu_load',
                'high_memory_load', 'high_disk_load', 'system_stress'
            ]
            
            X = latest_data[feature_cols].fillna(0)
            X_scaled = self.scaler.transform(X)
            
            predictions = {}
            
            # Performance prediction
            if self.performance_model:
                future_stress = self.performance_model.predict(X_scaled)[0]
                predictions['future_system_stress'] = future_stress
                
            # Slowdown risk prediction
            if self.slowdown_classifier:
                slowdown_prob = self.slowdown_classifier.predict_proba(X_scaled)[0]
                predictions['slowdown_risk'] = slowdown_prob[1] if len(slowdown_prob) > 1 else 0
                
            # Add trend analysis
            if len(data) >= 3:
                cpu_trend = data['cpu_percent'].iloc[-3:].diff().mean()
                memory_trend = data['memory_percent'].iloc[-3:].diff().mean()
                
                predictions['cpu_trend'] = 'increasing' if cpu_trend > 1 else 'decreasing' if cpu_trend < -1 else 'stable'
                predictions['memory_trend'] = 'increasing' if memory_trend > 1 else 'decreasing' if memory_trend < -1 else 'stable'
                
            # Estimate time to potential slowdown
            if predictions.get('slowdown_risk', 0) > 0.5:
                current_stress = latest_data['system_stress'].iloc[0]
                if current_stress > 0:
                    # Simple linear extrapolation
                    stress_rate = data['system_stress'].diff().iloc[-3:].mean()
                    if stress_rate > 0:
                        time_to_critical = (90 - current_stress) / stress_rate
                        predictions['time_to_slowdown'] = max(1, int(time_to_critical * 2))  # Convert to minutes
                    else:
                        predictions['time_to_slowdown'] = 60  # Default to 1 hour
                        
            return predictions
            
        except Exception as e:
            print(f"Error getting predictions: {e}")
            return None
            
    def save_models(self):
        """Save trained models to disk"""
        try:
            if not os.path.exists('models'):
                os.makedirs('models')
                
            if self.performance_model:
                joblib.dump(self.performance_model, 'models/performance_model.pkl')
                
            if self.slowdown_classifier:
                joblib.dump(self.slowdown_classifier, 'models/slowdown_classifier.pkl')
                
            if hasattr(self.scaler, 'scale_'):
                joblib.dump(self.scaler, 'models/scaler.pkl')
                
        except Exception as e:
            print(f"Error saving models: {e}")
            
    def load_models(self):
        """Load trained models from disk"""
        try:
            if os.path.exists('models/performance_model.pkl'):
                self.performance_model = joblib.load('models/performance_model.pkl')
                
            if os.path.exists('models/slowdown_classifier.pkl'):
                self.slowdown_classifier = joblib.load('models/slowdown_classifier.pkl')
                
            if os.path.exists('models/scaler.pkl'):
                self.scaler = joblib.load('models/scaler.pkl')
                
            if self.performance_model or self.slowdown_classifier:
                self.is_trained = True
                print("Models loaded successfully")
                
        except Exception as e:
            print(f"Error loading models: {e}")
            
    def get_feature_importance(self) -> Dict:
        """Get feature importance from trained models"""
        importance = {}
        
        try:
            if self.performance_model and hasattr(self.performance_model, 'feature_importances_'):
                feature_cols = self.feature_columns + [
                    'hour', 'day_of_week', 'cpu_rolling_avg', 'memory_rolling_avg', 
                    'disk_rolling_avg', 'cpu_trend', 'memory_trend', 'high_cpu_load',
                    'high_memory_load', 'high_disk_load', 'system_stress'
                ]
                
                importances = self.performance_model.feature_importances_
                importance = dict(zip(feature_cols, importances))
                
                # Sort by importance
                importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
                
        except Exception as e:
            print(f"Error getting feature importance: {e}")
            
        return importance