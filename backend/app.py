from flask import Flask
from backend.extensions import db, migrate
from backend.config import DevelopmentConfig, ProductionConfig, TestingConfig
# from blueprints.admin import admin_bp
from backend.blueprints.auth import auth_bp
from backend.blueprints.users import users_bp
from backend.blueprints.admin_users import admin_users_bp
from backend.blueprints.test import test_bp
from backend.errors import setup_errorhandlers

import firebase_admin
from firebase_admin import credentials


def create_app(config_class=DevelopmentConfig):

    app = Flask(__name__)

    app.config.from_object(config_class)

    fb_key_path = app.config.get('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')

    print('test')
    if fb_key_path:
        try:
            # アプリがすでに初期化されていないかチェック
            if not firebase_admin._apps:
                cred = credentials.Certificate(fb_key_path)
                # firebase_admin.initialize_app(cred) により _apps辞書に「デフォルトアプリ」が登録されます
                # firebase_adminモジュール自体が、内部の _apps 辞書を通して初期化されたAppオブジェクトへの参照を保持・管理してくれる
                # auth, firestore, storage などのサブモジュールは、_apps 辞書に登録されている "[DEFAULT]" のAppを自動的に見つけて利用する
                firebase_admin.initialize_app(cred)
                app.logger.info("Firebase Admin SDKが正常に初期化されました。")

        except (FileNotFoundError, ValueError) as e:
            # パスは設定されているが、ファイルがない、または中身が不正な場合のエラーハンドリング
            app.logger.critical(f"Firebase Admin SDKの初期化に失敗しました: {e}")
            raise SystemExit("アプリケーションを起動できません。Firebaseの認証設定を確認してください。")
    else:
        # 設定がない場合は、その旨をログに出力しておくと親切
        app.logger.warning("FIREBASE_SERVICE_ACCOUNT_KEY_PATHが設定されていません。Firebaseの初期化をスキップします。")



    db.init_app(app)
    migrate.init_app(app, db)

    setup_errorhandlers(app)

    # app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(test_bp)

    return app


    # from .utils import error_response
    # @app.errorhandler(Exception)
    # def handle_exception(e):
    #     app.logger.error(f"Unhandled exception: {e}", exc_info=True)
    #     if app.config['DEBUG']:
    #         raise e  # 開発中はFlaskのデバッグ画面で例外を確認
    #     return error_response("internal-error", "An unexpected error occurred.", 500)


    # return app



