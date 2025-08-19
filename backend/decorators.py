from functools import wraps
from flask import request, g, current_app
from firebase_admin import auth
from backend.utils import error_response


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Authorizationヘッダーの存在確認
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.strip():
            current_app.logger.info("Login failed: Authorization header is missing.")
            return error_response("auth/missing-header", "Authorization header is missing.", 401)

        # 2. 'Bearer ' プレフィックスの確認とトークンの抽出
        parts = auth_header.strip().split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            current_app.logger.info("Login failed: Invalid Authorization header format.")
            return error_response("auth/invalid-header", "Invalid Authorization header format. Expected 'Bearer <token>'.", 401)

        id_token = parts[1]

        # 3. IDトークンの検証
        try:
            # check_revoked=True とすると、毎回 FB Authのサーバーに問い合わせてブロックリストに入っていないか検証する。
            decoded_token = auth.verify_id_token(id_token, check_revoked=True)

            if not decoded_token:
                current_app.logger.error("Decoded token is empty after verification.")
                return error_response(
                    "auth/invalid-id-token",
                    "Invalid ID token.",
                    401
                )

            g.user = decoded_token

        except auth.ExpiredIdTokenError:
            current_app.logger.info("Login failed: ID token has expired.")
            return error_response("auth/id-token-expired", "ID token has expired. Please login again.", 401)

        except auth.InvalidIdTokenError as e:
            current_app.logger.warning(f"Login failed: Invalid ID token received. Reason: {e}")
            return error_response("auth/invalid-id-token", "Invalid ID token provided.", 401)

        # 以下の二つのエラーは check_revoked=True とした時のみ、Firebase サーバーから送られる。
        except auth.RevokedIdTokenError:
            current_app.logger.info("Login failed: ID token has been revoked.")
            return error_response("auth/id-token-revoked", "ID token has been revoked. Please login again.", 401)

        # 対象ユーザーの状態（disabled かどうか）を Firebase サーバーに問い合わせた結果、無効化されている（disabled=True）場合。
        # Firebase のユーザーにはデフォルトで disabled という boolean フィールドが存在
        except auth.UserDisabledError:
            current_app.logger.warning("Login failed: User account is disabled.")
            return error_response("auth/user-disabled", "User account is disabled.", 403)

        except Exception as e:
            # 予期しない例外は握り潰さず再送出
            current_app.logger.error(f"Unexpected error during token verification: {e}", exc_info=True)
            raise

        # 4. 検証成功後、元のビュー関数を実行
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # login_required が先に呼ばれていることを前提にする
        if not hasattr(g, 'user') or not g.user:
            raise RuntimeError("g.user must be set by login_required before admin_required")

        user = g.user
        if not user.get('is_admin'):
            user_uid = user.get('uid', 'N/A')
            current_app.logger.warning(
                f"Forbidden access attempt: User '{user_uid}' tried to access an admin-only resource at '{request.path}'."
            )
            return error_response("auth/admin-required", "Forbidden: Administrator access is required for this resource.", 403)

        return f(*args, **kwargs)

    return decorated_function



