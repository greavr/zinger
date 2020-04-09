# App Config File

from flask import Flask
import os

class Config(object):
# App Config
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'thisisbanananas'
    

class Production(Config):
    print ("--Production Mode--")

class Debug(Config):
    print ("--Debug Mode--")
    DEBUG = True
    if os.getenv('gcp_project') is not None and os.getenv('GOOGLE_APPLICATION_CREDENTIALS') is not None:
        EnableDebugTools = True

class TestingConfig(Config):
    print ("--Testing Mode--")
    TESTING = True