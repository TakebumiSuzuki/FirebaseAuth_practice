from flask import Blueprint, request, jsonify, current_app, g
from firebase_admin import auth
from ..decorators import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


# ログアウトの際のrevoke
@auth_bp.post("/revoke-refresh-token")
@login_required
def revoke_refresh_token():
    uid = g.user.get('uid')

    # ここで if not uid: のように書くこともできるが、そもそも @login_required で検証済みの後にuidキーが存在しないことは
    # ありえないので、ここではエラーハンドリングせず、バグとしてクラッシュさせる。

    try:
        # サーバーサイドでリフレッシュトークンを無効化
        auth.revoke_refresh_tokens(uid)
        return jsonify({"message": f"Successfully revoked refresh tokens for user: {uid}"}), 200

    except auth.UserNotFoundError:
        # このエラーは、トークン発行後にFirebase上でユーザーが削除された場合などに起こりうる
        return jsonify({"message": "User not found", "code": "auth/user-not-found"}), 404

    except auth.AuthError as e:
        # Firebaseからのその他の認証エラー
        current_app.logger.error(f"Firebase Auth Error on revoke: {e.code} - {e.default_message}")
        # クライアントには詳細すぎる情報は返さず、サーバー側でログを取る
        return jsonify({"message": "An internal error occurred with the authentication service.", "code": e.code}), 500

    except Exception as e:
        # 予期せぬその他のエラー
        current_app.logger.error(f"An unexpected error on revoke: {e}")
        return jsonify({"message": "An unexpected server error occurred.", "code": "internal/unexpected-server-error"}), 500