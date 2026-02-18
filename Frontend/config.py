# -*- coding: utf-8 -*-
"""
config.py
Created on 06/02/2026
@author: Callum
"""
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

from datetime import timedelta


class Config:
    DEBUG = False
    JSON_AS_ASCII = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    SUMMARY_EMAIL_HOUR = 6
    SUMMARY_EMAIL_MINUTE = 00


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = "teeth"


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = secrets.token_hex(32)


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SECRET_KEY = "teeth"


# Use absolute paths based on project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')

file_names = {
    'UserFile': os.path.join(DATA_DIR, 'users.json'),
    'ChoreFile': os.path.join(DATA_DIR, 'chores.json'),
    'InstanceFile': os.path.join(DATA_DIR, 'instances.json'),
    'HistoryFile': os.path.join(DATA_DIR, 'history.json'),
    'RecentlyAssigned': os.path.join(DATA_DIR, 'recentlyAssigned.json')
}


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

