class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Lima22Alpha@localhost/mechanic_db'
    DEBUG = True 
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
class TestingConfig:
    #SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Lima22Alpha@localhost/testing_db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    TESTING = True
    CACHE_DEFAULT_TIMEOUT = 300

class prodconfig:
    pass