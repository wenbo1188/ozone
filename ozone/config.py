class Config(object):
    pass

class ProdConfig(Config):
    DEBUG=True
    DATABASE='/home/wenbo1188/message.db'

class DevConfig(Config):
    pass
