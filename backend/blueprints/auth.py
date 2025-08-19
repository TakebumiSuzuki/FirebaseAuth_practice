from flask import Blueprint, g, current_app, request
from firebase_admin import auth
from backend.decorators import login_required
from backend.utils import error_response
from backend.extensions import db
from backend.models.user_profile import UserProfile

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# ログアウトの際のトークンのrevoke
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



@auth_bp.post("create-user-profile")
@login_required
def create_user_profile():
    # 1. デコレータによって g.user に保存された、検証済みのUIDを取得
    try:
        uid = g.user['uid']
    except (AttributeError, KeyError):
        # g.userが存在しない、またはuidキーがないという万が一の事態に備える
        current_app.logger.error("g.user or uid is not found after login_required decorator.")
        return {"error": "An unexpected authentication error occurred."}, 500

    # 2. ペイロードからプロファイル情報を取得
    payload = request.get_json()
    if not payload:
        return {"error": "Request body is missing"}, 400

    display_name = payload.get('display_name', '')

    # 3. データベースに保存
    # (モデルのフィールド名が display_name であることを想定)
    user_profile = UserProfile(uid=uid, display_name=display_name, is_admin=False)

    try:
        db.session.add(user_profile)
        db.session.commit()
        return {"message": f"Successfully created the user_profile for this user: {uid}"}, 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Database error while creating profile for {uid}: {e}")
        # error_response は自作のヘルパー関数と想定
        return error_response("database-error", "A database error occurred.", 500)
