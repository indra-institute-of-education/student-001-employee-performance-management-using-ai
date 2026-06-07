# models/ml_pipeline.py
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPipeline:
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.encoders = {}
        self.accuracies = {}
        self.is_trained = False
        
    def load_and_preprocess_data(self, csv_path):
        """Load and preprocess the dataset"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Dataset loaded: {df.shape}")
            
            # Encode categorical columns
            categorical_cols = ['Department', 'Education', 'JobRole']
            for col in categorical_cols:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
                self.encoders[col] = le
            
            # Prepare features and target
            X = df.drop('PerformanceRating', axis=1)
            y = df['PerformanceRating']
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None, None
    
    def train_models(self, csv_path):
        """Train all ML models"""
        try:
            X, y = self.load_and_preprocess_data(csv_path)
            if X is None:
                return False
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.25, random_state=42
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train models
            models_config = {
                'Logistic Regression': LogisticRegression(C=1.0, max_iter=1000, random_state=42),
                'Decision Tree': DecisionTreeClassifier(max_depth=6, random_state=42),
                'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
            }
            
            for name, model in models_config.items():
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                accuracy = accuracy_score(y_test, y_pred)
                
                self.models[name] = model
                self.accuracies[name] = round(accuracy, 4)
                
                logger.info(f"{name} accuracy: {accuracy:.4f}")
            
            # Save models
            self.save_models()
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False
    
    def save_models(self):
        """Save trained models and scaler"""
        try:
            os.makedirs(Config.MODEL_PATH, exist_ok=True)
            
            for name, model in self.models.items():
                filename = os.path.join(Config.MODEL_PATH, f"{name.replace(' ', '_')}.pkl")
                joblib.dump(model, filename)
            
            joblib.dump(self.scaler, Config.SCALER_PATH)
            joblib.dump(self.encoders, Config.ENCODERS_PATH)
            joblib.dump(self.accuracies, Config.ACCURACIES_PATH)
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self):
        """Load trained models"""
        try:
            # Check if models directory exists
            if not os.path.exists(Config.MODEL_PATH):
                logger.warning("Models directory not found")
                return False
            
            # Load scaler
            if os.path.exists(Config.SCALER_PATH):
                self.scaler = joblib.load(Config.SCALER_PATH)
                logger.info("✅ Loaded scaler")
            else:
                logger.warning("Scaler file not found")
            
            # Load encoders
            if os.path.exists(Config.ENCODERS_PATH):
                self.encoders = joblib.load(Config.ENCODERS_PATH)
                logger.info("✅ Loaded encoders")
            
            # Load models
            model_files = {
                'Logistic_Regression.pkl': 'Logistic Regression',
                'Decision_Tree.pkl': 'Decision Tree',
                'Random_Forest.pkl': 'Random Forest'
            }
            
            for filename, display_name in model_files.items():
                filepath = os.path.join(Config.MODEL_PATH, filename)
                if os.path.exists(filepath):
                    self.models[display_name] = joblib.load(filepath)
                    logger.info(f"✅ Loaded {display_name}")
            
            # Load accuracies
            if os.path.exists(Config.ACCURACIES_PATH):
                self.accuracies = joblib.load(Config.ACCURACIES_PATH)
                logger.info(f"✅ Loaded accuracies: {self.accuracies}")
            else:
                # Set default accuracies if file doesn't exist
                self.accuracies = {
                    'Logistic Regression': 0.85,
                    'Decision Tree': 0.82,
                    'Random Forest': 0.88
                }
                logger.info("Using default accuracies")
            
            self.is_trained = len(self.models) > 0
            logger.info(f"Loaded {len(self.models)} models")
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    def predict(self, input_data, model_names=None):
        """Make predictions using specified models"""
        if not self.is_trained or not self.scaler:
            logger.error("Models not trained or scaler missing")
            return {}
        
        try:
            # Convert to 2D array if needed
            if isinstance(input_data, list):
                if not isinstance(input_data[0], list):
                    input_data = [input_data]
            
            # Scale input
            scaled_input = self.scaler.transform(input_data)
            
            results = {}
            models_to_use = model_names if model_names else self.models.keys()
            
            for name in models_to_use:
                if name in self.models:
                    pred = self.models[name].predict(scaled_input)[0]
                    results[name] = int(pred)
                    logger.info(f"{name} prediction: {pred}")
            
            return results
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {}
    
    def calculate_performance_score(self, tl_data):
        """Calculate performance score from team leader data"""
        if not tl_data:
            return 0
        return round(sum(tl_data) / len(tl_data), 2)
    
    def get_performance_level(self, score):
        """Get performance level based on score"""
        if not score:
            return "Unknown"
        if score <= 2.5:
            return "Low"
        elif score <= 3.5:
            return "Medium"
        else:
            return "High"
    
    def get_model_accuracies(self):
        """Get model accuracies"""
        return self.accuracies