
class BaseConfig():
    SECRET_KEY= 'iefnawef93jf2u9ufn2'

    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    pass

class ProductionConfig(BaseConfig):
    pass

class TestingConfig(BaseConfig):
    pass