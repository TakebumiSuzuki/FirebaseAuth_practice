from flask import Blueprint, g, current_app
from firebase_admin import auth
from backend.decorators import login_required
from backend.utils import error_response

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# ログアウトの際のトークンのrevoke
@auth_bp.post("/revoke-refresh-token")
@login_required
def revoke_refresh_token():
    uid = g.user.get('uid')

    try:
        # サーバーサイドでリフレッシュトークンを無効化
        auth.revoke_refresh_tokens(uid)
        return {"message": f"Successfully revoked refresh tokens for user: {uid}"}, 200

    except auth.UserNotFoundError:
        return error_response("auth/user-not-found", "User not found.", 404)

    except auth.AuthError as e:
        current_app.logger.error(f"Firebase Auth Error on revoke: {e.code} - {e.default_message}", exc_info=True)
        return error_response(e.code, "An internal error occurred with the authentication service.", 500)

    except Exception as e:
        current_app.logger.error(f"Unexpected error on revoke: {e}", exc_info=True)
        return error_response("internal/unexpected-server-error", "An unexpected server error occurred.", 500)
