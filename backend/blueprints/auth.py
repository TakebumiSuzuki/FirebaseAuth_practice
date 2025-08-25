from flask import Blueprint, g, current_app, jsonify
from firebase_admin import auth
from backend.decorators import login_required, payload_required
from backend.utils import error_response
from backend.extensions import db
from backend.models.user_profile import UserProfile

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# ログアウトの際のトークンのrevokeだが、多くの場合、これは必要なく、ローカルのトークンを消去するだけで済ませることが多い
@auth_bp.post("/revoke-refresh-token")
@login_required
def revoke_refresh_token():
    uid = g.user.get('uid')

    try:
        # ユーザーがログインしているすべてのデバイスのリフレッシュトークンを一斉に無効化
        # 全てのデバイスで、IDトークンの有効期限つまり、最大1時間後に、リフレッシュできなくなる。
        # また、この時同時に、Firebase内部でtokensValidAfterTimeがアップデートされる。
        # これは auth.verify_id_token(id_token, check_revoked=True)と書いて厳密な検証をする時に使える。
        auth.revoke_refresh_tokens(uid)
        current_app.logger.info(f"Successfully revoked refresh tokens for user: {uid}")
        return {"message": f"Successfully revoked refresh tokens for user: {uid}"}, 200

    except auth.UserNotFoundError:
        current_app.logger.warning(f"User not found during token revoke: {uid}")
        return error_response("auth/user-not-found", "User not found.", 404)

    except auth.AuthError as e:
        current_app.logger.error(f"Firebase Auth Error on revoke for user {uid}: {e.code} - {e.default_message}", exc_info=True)
        return error_response(e.code, "An internal error occurred with the authentication service.", 500)

    except Exception as e:
        current_app.logger.error(f"Unexpected error on revoke for user {uid}: {e}", exc_info=True)
        return error_response("internal/unexpected-server-error", "An unexpected server error occurred.", 500)


# ユーザーの新規登録の際に必ずこのエンドポイントを使う
@auth_bp.post("create-user-profile")
@login_required
@payload_required
def create_user_profile():
    try:
        uid = g.user['uid']
    except (AttributeError, KeyError):
        # g.userが存在しない、またはuidキーがないという万が一の事態に備える
        current_app.logger.error("g.user or uid is not found after login_required decorator.")
        return {"error": "An unexpected authentication error occurred."}, 500

    display_name = g.payload.get('display_name', '')

    if display_name == 'admin':
        user_profile = UserProfile(uid=uid, display_name=display_name, is_admin=True)
    else:
        user_profile = UserProfile(uid=uid, display_name=display_name, is_admin=False)

    try:
        db.session.add(user_profile)
        db.session.commit()
        return jsonify('User profile data was successfully saved.'), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.critical(f"Faild to save user profile data. Database error occured while creating user profile for {uid}: {e}")
        return error_response("database-error", "A database error occurred.", 500)
