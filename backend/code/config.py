# App Config File

from flask import Flask
import os

class Config(object):
# App Config
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'thisisbananana'

    # Redis Env
    redis_host = os.getenv('redishost', '127.0.0.1')
    redis_port = os.getenv('redisport', '7001')
    redis_db = "Zinger"

     # Debug settings
    print ("Node: {0}, Redis Host: {1} , Redis Port: {2}, Redis DB: {3}".format(os.uname()[1], redis_host, redis_port,redis_db))
    

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