# coding:utf-8

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'har to guess string'

class DevelopmentConfig(Config):
    DEBUG = True
    TOKEN = 'kepler'

config = {
        'default':DevelopmentConfig
        }
