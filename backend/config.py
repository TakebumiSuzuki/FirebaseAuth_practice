import os
class BaseConfig():
    SECRET_KEY= 'iefnawef93jf2u9ufn2'

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')


class ProductionConfig(BaseConfig):
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')


class TestingConfig(BaseConfig):
    TESTING = True # Flaskがテストモードで動作する
    # テスト専用のDBを指すようにする
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') 