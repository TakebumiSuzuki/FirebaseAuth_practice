from functools import wraps
from flask import Blueprint, request, g, jsonify, current_app
from firebase_admin import auth
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from backend.extensions import db
from backend.decorators import login_required, user_profile_required, payload_required
from backend.models.user_profile import UserProfile
from backend.schemas.firebase_user import UserReadFirebaseUser, UserUpdateFirebaseUser
from backend.schemas.user_profile import PublicUserProfile, UpdateUserProfile
from backend.utils import error_response

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')


@users_bp.get('/me')
@login_required
@user_profile_required
def get_me():
    user_profile = g.user_profile
    user_dic = UserReadFirebaseUser.model_validate(g.user).model_dump()
    user_profile_dic = PublicUserProfile.model_validate(user_profile).model_dump()
    return jsonify({**user_dic, **user_profile_dic}), 200


@users_bp.patch('/me')
@login_required
@user_profile_required
@payload_required
def update_me():
    uid = g.user['uid']
    user_profile = g.user_profile
    payload = g.payload

    firebase_user_updates = {}
    user_profile_updates = {}
    for key, value in payload.items():
        if key in ['email', 'display_name' ]:
            firebase_user_updates[key] = value
        if key in ['birthday', 'gender', 'display_name']:
            user_profile_updates[key] = value

    if user_profile_updates:
        user_profile_data = UpdateUserProfile.model_validate(user_profile_updates).model_dump()
        for key, value in user_profile_data.items():
            setattr(user_profile, key, value)

    try:
        if firebase_user_updates:
            firebase_user_data = UserUpdateFirebaseUser.model_validate(firebase_user_updates).model_dump()
            auth.update_user(uid, firebase_user_data)
        db.session.commit()
        return '', 204

    except SQLAlchemyError as e:
        db.session.rollback()
        # 隣接する文字列リテラル（'や"で囲まれた文字列、f-string、r-stringなど）は、自動的に一つの文字列として連結される。
        current_app.logger.critical(f'CRITICAL: Data inconsistency occurred. DB commit failed after successful Firebase update for UID: {uid}.' f' This requires manual intervention. Original DB Error: {e}')
        raise


@users_bp.delete('/me')
@login_required
@user_profile_required
def delete_me():
    uid = g.user['uid']
    user_profile = g.user_profile

    db.session.delete(user_profile)
    auth.delete_user(uid)
    try:
        db.session.commit()
        return '', 204

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.critical(f'CRITICAL: Data inconsistency occurred. UserProfile deletion failed after successful Firebase user deletion for UID: {uid}.' f' This requires manual intervention. Original DB Error: {e}')
        raise


@users_bp.errorhandler(ValidationError)
def handle_validation_error(error: ValidationError):
    # Pydanticのエラー詳細を取得
    error_details = error.errors()
    current_app.logger.warning(f"Validation Failed: {error_details}")

    # クライアントには、どのフィールドでどのようなエラーが起きたかの詳細を返す
    return error_response(
        code='validation_error',
        message='The provided data is invalid. Please check the details.',
        status=422,  # 404 から 422 に変更
        details=error_details  # 詳細情報を追加
    )

@users_bp.errorhandler(auth.UserNotFoundError)
def handle_user_not_found(error):
    db.session.rollback()
    current_app.logger.warning(f"Firebase user not found: {error}")
    return error_response(code='not_found', message='The specified user was not found.', status=404)

@users_bp.errorhandler(auth.EmailAlreadyExistsError)
def handle_email_already_exists(error):
    db.session.rollback()
    current_app.logger.warning(f"User update failed due to duplicate email.: {error}")
    return error_response(
        code='conflict/email-exists', message='The email address is already in use by another account.', status=409
    )

@users_bp.errorhandler(auth.AuthError)
def handle_firebase_auth_error(error):
    db.session.rollback()
    current_app.logger.error(f"Firebase Auth Error: {error}")
    return error_response(code='auth_error', message='An authentication error occurred with Firebase.', status=500)

@users_bp.errorhandler(SQLAlchemyError)
def handle_database_error(error):
    db.session.rollback()
    current_app.logger.error(f"Database Error: {error}")
    return error_response(code='database_error', message='A database error occurred.', status=500)

# 最も一般的なエラーとして最後に定義
@users_bp.errorhandler(Exception)
def handle_unexpected_error(error):
    db.session.rollback()
    current_app.logger.error(f"An unexpected error occurred: {error}")
    return error_response(code='internal_server_error', message='An internal server error occurred.', status=500)


"""
ValidationErrorの構造
{
  "error": {
    "code": "validation_error",
    "message": "The provided data is invalid. Please check the details.",
    "details": [
      {
        "loc": ["email"],
        "msg": "value is not a valid email address",
        "type": "value_error.email"
      },
      {
        "loc": ["age"],
        "msg": "ensure this value is greater than 18",
        "type": "value_error.number.not_gt"
      }
    ]
  }
}

"""

