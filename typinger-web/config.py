# config.py
# Typinger Web - 設定ファイル

import os
from datetime import timedelta

class Config:
    """基本設定"""
    DEBUG = False
    TESTING = False
    
    # Flask設定
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # ディレクトリ設定
    SCENARIO_DIR = os.environ.get('SCENARIO_DIR', 'scenario')
    OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'output')
    
    # サーバー設定
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """テスト環境設定"""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False

# 環境に応じて設定を選択
def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
