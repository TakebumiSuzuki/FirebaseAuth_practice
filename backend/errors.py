from firebase_admin import auth, exceptions
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from backend.extensions import db
from backend.utils import error_response


def setup_errorhandlers(app):

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        # Pydanticのエラー詳細を取得
        error_details = error.errors()
        app.logger.warning(f"Validation Failed: {error_details}")

        # クライアントには、どのフィールドでどのようなエラーが起きたかの詳細を返す
        return error_response(
            code='validation_error',
            message='The provided data is invalid. Please check the details.',
            status=422,  # 404 から 422 に変更
            details=error_details  # 詳細情報を追加
        )

    @app.errorhandler(auth.UserNotFoundError)
    def handle_user_not_found(error):
        db.session.rollback()
        app.logger.warning(f"Firebase user not found: {error}")
        return error_response(code='not_found', message='The specified user was not found.', status=404)

    @app.errorhandler(auth.EmailAlreadyExistsError)
    def handle_email_already_exists(error):
        db.session.rollback()
        app.logger.warning(f"User update failed due to duplicate email.: {error}")
        return error_response(
            code='conflict/email-exists', message='The email address is already in use by another account.', status=409
        )
    # Firebaseとの通信エラーなどが発生した場合
    @app.errorhandler(exceptions.FirebaseError)
    def handle_firebase_auth_error(error):
        db.session.rollback()
        app.logger.error(f"Firebase Auth Error: {error}")
        return error_response(code='auth_error', message='An authentication error occurred with Firebase.', status=500)

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        db.session.rollback()
        app.logger.error(f"Database Error: {error}")
        return error_response(code='database_error', message='A database error occurred.', status=500)

    # 最も一般的なエラーとして最後に定義
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        app.logger.error(f"An unexpected error occurred: {error}")
        return error_response(code='internal_server_error', message='An internal server error occurred.', status=500)

