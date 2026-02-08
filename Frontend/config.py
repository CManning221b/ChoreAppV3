# -*- coding: utf-8 -*-
"""
config.py
Created on 06/02/2026
@author: Callum
"""
import os
import secrets

from datetime import timedelta


class Config:
    DEBUG = False
    JSON_AS_ASCII = False


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


file_names = {
    'UserFile': '../Data/users.json',
    'ChoreFile': '../Data/chores.json',
    'InstanceFile': '../Data/instances.json'
}


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
