from functools import wraps
# g は flask.g という特殊なオブジェクト（プロキシ）で、通常のPythonオブジェクトのように、
# ドット (.) を使った属性の読み書きができるように設計されています。
from flask import request, g, current_app
from firebase_admin import auth
from werkzeug.exceptions import BadRequest

from backend.extensions import db
from backend.models.user_profile import UserProfile
from backend.utils import error_response


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
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
                return error_response("auth/invalid-id-token", "Invalid ID token.", 401)
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
        # Firebase のユーザーにはデフォルトで disabled というbooleanフィールドが存在。これもcheck_revoked=Trueにする必要あり。
        # 403 は、クライアントの身元は確認できている（認証済み）ものの、そのリソースへのアクセス 権限 (Authorization) がない状態。
        except auth.UserDisabledError:
            current_app.logger.warning("Login failed: User account is disabled.")
            return error_response("auth/user-disabled", "User account is disabled.", 403)

        except Exception as e:
            # 予期しない例外は握り潰さず再送出
            current_app.logger.error(f"Unexpected error during token verification: {e}", exc_info=True)
            raise

        # 4. 検証成功後、元のビュー関数を実行
        return f(*args, **kwargs)

    return wrapper


def user_profile_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            # このようなビジネスロジック層で捕捉されなかったあらゆる予期せぬ例外を最終的に@app.errorhandler(Exception)
            # で受け止める。
            raise RuntimeError("g.user must be set by login_required before user_profile_required")

        # firebaseにより 'uid' の存在は保証されているので、エラーハンドリングは不要
        uid = g.user['uid']
        user_profile = db.session.get(UserProfile, uid)
        if not user_profile:
            # データの不整合はサーバー側の問題。つまりビジネスロジック上、あってはいけない状態。
            # このエラーは、ログに記録され、開発者が調査すべき問題となる。
            raise RuntimeError(f'CRITICAL: Data inconsistency. UserProfile not found for authenticated user UID: {uid}')
        g.user_profile = user_profile
        return f(*args, **kwargs)
    return wrapper


def payload_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # 1. JSONのパースを試みる
            payload = request.get_json()

            # 2. パースは成功したが、ペイロードが空（None）だった場合
            if payload is None:
                current_app.logger.info("Request failed: JSON payload is missing or empty.")
                return error_response(
                    "request/missing-payload",
                    "Request body must contain a JSON payload.",
                    400
                )

        except BadRequest as e:
            # 3. JSONの形式が不正、またはContent-Typeヘッダーが不適切だった場合
            # BadRequestのデフォルトメッセージは開発者向けなので、クライアントには汎用的なメッセージを返す
            current_app.logger.info(f"Request failed: Could not parse JSON. Reason: {e}")
            return error_response(
                "request/invalid-json",
                "Failed to decode JSON object. Please check the syntax and Content-Type header.",
                400
            )

        # 4. 成功した場合、gにペイロードを格納
        g.payload = payload
        return f(*args, **kwargs)
    return wrapper



def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # login_required が先に呼ばれていることを前提にする
        if not hasattr(g, 'user') or not g.user:
            raise RuntimeError("g.user must be set by login_required before admin_required")

        user = g.user
        # auth.verify_id_token() が返すデコード済みIDトークンにはトップレベルに is_admin キーが追加されている。
        if not user.get('is_admin'):
            user_uid = user.get('uid', 'N/A')
            current_app.logger.warning(
                f"Forbidden access attempt: User '{user_uid}' tried to access an admin-only resource at '{request.path}'."
            )
            return error_response("auth/admin-required", "Forbidden: Administrator access is required for this resource.", 403)

        return f(*args, **kwargs)

    return wrapper



