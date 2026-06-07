# config.py
import os

# Simple config without dotenv
class Config:
    # Database configuration
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''  # Change this if you have a MySQL password
    MYSQL_DB = 'employee_system'
    
    # Email configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'divyadharshini04.hr@gmail.com'
    MAIL_PASSWORD = 'fhhp tfuk jeto albi'
    
    # Application settings
    SECRET_KEY = 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # Model paths
    MODEL_PATH = 'trained_models/'
    SCALER_PATH = 'trained_models/scaler.pkl'
    ENCODERS_PATH = 'trained_models/encoders.pkl'
    ACCURACIES_PATH = 'trained_models/accuracies.pkl'
    
    # Department mapping
    DEPT_MAP = {
        'sales': 0, 'hr': 1, 'it': 2, 'operation': 3, 'finance': 4
    }
    
    # Education mapping
    EDU_MAP = {
        'diploma': 0, 'bachelors': 1, 'masters': 2, 'mba': 3
    }
    
    # Job role mapping
    ROLE_MAP = {
        'executive': 0, 'analyst': 1, 'scientist': 2, 'manager': 3
    }
    
    # Reverse mappings for display
    DEPT_NAMES = {v: k.capitalize() for k, v in DEPT_MAP.items()}
    EDU_NAMES = {v: k.capitalize() for k, v in EDU_MAP.items()}
    ROLE_NAMES = {v: k.capitalize() for k, v in ROLE_MAP.items()}
    