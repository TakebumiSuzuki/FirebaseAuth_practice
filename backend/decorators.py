from functools import wraps
from flask import request, g, jsonify, current_app
from firebase_admin import auth


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Authorizationヘッダーの存在確認
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "Authorization header is missing", "code": "auth/missing-header"}), 401

        # 2. 'Bearer ' プレフィックスの確認とトークンの抽出
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({"message": "Invalid Authorization header format", "code": "auth/invalid-header"}), 401

        id_token = parts[1]

        # 3. IDトークンの検証
        try:
            # Firebase Admin SDKを使ってIDトークンを検証
            decoded_token = auth.verify_id_token(id_token)

            # gオブジェクトにユーザー情報を格納し、後続のビュー関数で利用できるようにする
            g.user = decoded_token

        except auth.ExpiredIdTokenError:
            # トークンの有効期限切れ
            return jsonify({"message": "ID token has expired", "code": "auth/id-token-expired"}), 401
        except auth.InvalidIdTokenError as e:
            # トークンが無効（不正な形式、署名が違うなど）
            current_app.logger.warning(f"Invalid ID token received: {e}")
            return jsonify({"message": "Invalid ID token", "code": "auth/invalid-id-token"}), 401
        except Exception as e:
            # その他の予期せぬエラー
            current_app.logger.error(f"Unexpected error during token verification: {e}")
            return jsonify({"message": "An unexpected error occurred during authentication"}), 500


        # 4. 検証成功後、元のビュー関数を実行
        return f(*args, **kwargs)

    return decorated_function