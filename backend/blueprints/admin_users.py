from functools import wraps
from flask import Blueprint, request, jsonify, current_app, g
from firebase_admin import auth
from sqlalchemy.exc import SQLAlchemyError
from backend.schemas.user_profile import ReadUserProfile
from backend.schemas.firebase_user import AdminReadFirebaseUser

from backend.extensions import db
from backend.decorators import login_required, admin_required, payload_required
from backend.utils import error_response
from backend.models.user_profile import UserProfile



# from datetime import datetime, timezone
# タイムスタンプ（ミリ秒）をISO 8601形式の文字列に変換するヘルパー関数
# def format_timestamp(ts_ms):
#     if not ts_ms:
#         return None
#     # ミリ秒を秒に変換
#     return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).isoformat()

admin_users_bp = Blueprint('admin_users', __name__, url_prefix='/api/v1/admin/users')

def uid_required_in_payload(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'payload') or not g.payload:
            raise RuntimeError("g.payload must be set by payload_required before admin_required")
        # get() を使って安全にuidを取得
        uid = g.payload.get('uid')
        if not uid:
            return error_response(code='bad_request', message='User ID (uid) is missing in the payload.', status=400)
        g.uid = uid
        return func(*args, **kwargs)
    return wrapper


@admin_users_bp.get('')
@login_required
@admin_required
def admin_get_users():
    # nextPageToken が存在しなければ、戻り値は None になるので、Noneは書かなくても良い。
    page_token = request.args.get('nextPageToken', None)

    # max_resultsで取得件数を10件に指定。page_tokenがあれば、その続きから取得する
    # page_tokenは、Firebaseが生成する、非常に長い暗号化されたような文字列
    page = auth.list_users(max_results=10, page_token=page_token)

    # pageの内容が何もない場合、つまり要素数が0の場合には、空のリストが返る
    users_list = [AdminReadFirebaseUser.model_validate(user).model_dump() for user in page]

    response = {
        'users': users_list,
        'nextPageToken': page.next_page_token or None # 空文字列の場合もNoneに統一
    }
    return jsonify(response), 200


@admin_users_bp.get('/<str:uid>')
@login_required
@admin_required
def get_user_details(uid):
    user = auth.get_user(uid)

    user_data = AdminReadFirebaseUser.model_validate(user).model_dump()

    user_profile = db.session.get(UserProfile, uid)

    if not user_profile:
        # データ不整合：認証ユーザーが存在するのにプロファイルがない
        # これはサーバー側の問題なので、RuntimeErrorを発生させる
        raise RuntimeError(f"CRITICAL: User Profile missing for authenticated Firebase user: {uid}")

    user_profile_data = ReadUserProfile.model_validate(user_profile).model_dump()

    # {**A, **B} と書くことで、AとBのキーと値をすべて含む新しい辞書が作成される
    merged_data = {**user_data, **user_profile_data}

    return jsonify(merged_data), 200


@admin_users_bp.post('/change-disable')
@login_required
@admin_required
@payload_required
@uid_required_in_payload
def admin_change_user_disable():
    uid = g.uid
    user = auth.get_user(uid)

    auth.update_user(uid, disabled= not user.disabled)

    return jsonify({
        'uid': uid,
        'disabled': not user.disabled
    }), 200


@admin_users_bp.post('/change-role')
@login_required
@admin_required
@payload_required
@uid_required_in_payload
def admin_change_user_role():
    uid = g.uid
    user = auth.get_user(uid)

    # 1. custom_claims 辞書から現在の 'admin' 状態を取得 (存在しない場合は False)
    current_is_admin = user.custom_claims.get('is_admin', False)

    #    第一引数: uid, 第二引数: 更新したいクレームをすべて含んだ辞書
    auth.set_custom_user_claims(uid, {'is_admin': not current_is_admin})

    # 成功レスポンスとして、更新後の状態を返す
    return jsonify({
        'uid': uid,
        'is_admin': not current_is_admin # フロントエンドの命名規則に合わせてキャメルケースにすることも
    }), 200


@admin_users_bp.delete('/delete-user')
@login_required
@admin_required
@payload_required
@uid_required_in_payload
def delete_user():
    uid = g.uid
    user_profile = db.session.get(UserProfile, uid)

    if user_profile:
        db.session.delete(user_profile)
        db.session.flush()
    # 存在しない場合は何もしないでOK。最終的な目標はユーザーが消えることだから。
    auth.delete_user(uid)
    db.session.commit()
    return jsonify({}), 204


@admin_users_bp.errorhandler(auth.UserNotFoundError)
def handle_user_not_found(error):
    db.session.rollback()
    current_app.logger.warning(f"Firebase user not found: {error}")
    return error_response(code='not_found', message='The specified user was not found.', status=404)

# Firebaseとの通信エラーなどが発生した場合
@admin_users_bp.errorhandler(auth.AuthError)
def handle_firebase_auth_error(error):
    db.session.rollback()
    current_app.logger.error(f"Firebase Auth Error: {error}")
    return error_response(code='auth_error', message='An authentication error occurred with Firebase.', status=500)

@admin_users_bp.errorhandler(SQLAlchemyError)
def handle_database_error(error):
    db.session.rollback()
    current_app.logger.error(f"Database Error: {error}")
    return error_response(code='database_error', message='A database error occurred.', status=500)

# 最も一般的なエラーとして最後に定義
@admin_users_bp.errorhandler(Exception)
def handle_unexpected_error(error):
    db.session.rollback()
    current_app.logger.error(f"An unexpected error occurred: {error}")
    return error_response(code='internal_server_error', message='An internal server error occurred.', status=500)


"""
[ auth.AuthErrorの主なサブクラス ]

auth.EmailAlreadyExistsError: create_user()やupdate_user()を呼び出す際に指定したメールアドレスが、既存のユーザーによって既に使用されている場合に発生します。[1][2]

auth.PhoneNumberAlreadyExistsError:create_user()やupdate_user()で指定した電話番号が、既に他のユーザーに使用されている場合に発生します。

auth.UidAlreadyExistsError: create_user()を呼び出す際に指定したuidが、既存のユーザーによって既に使用されている場合に発生します。[3]

auth.EmailNotFoundError: get_user_by_email()を呼び出した際に、指定されたメールアドレスを持つユーザーが存在しない場合に発生します。

auth.UserNotFoundError: get_user()、update_user()、delete_user()などで指定されたuidを持つユーザーが存在しない場合に発生します。

auth.ExpiredIdTokenError: verify_id_token()で検証したIDトークンの有効期限が切れている場合に発生します。[4]

auth.RevokedIdTokenError: IDトークンが無効にされている（例：ユーザーのセッションがリセットされた）場合に発生します。[4]

auth.InvalidIdTokenError: IDトークンの形式が正しくない、または署名が無効であるなど、トークン自体に問題がある場合に発生します。[4]

auth.ExpiredSessionCookieError: verify_session_cookie()で検証したセッションクッキーの有効期限が切れている場合に発生します。[5]

auth.RevokedSessionCookieError: セッションクッキーが無効にされている場合に発生します。[5]

auth.InvalidSessionCookieError: セッションクッキーの形式が正しくない場合に発生します。

auth.InsufficientPermissionError: Admin SDKの初期化に使用された認証情報（サービスアカウント）に、要求された操作を実行するための十分な権限がない場合に発生します。[1][3]

auth.CertificateFetchError: IDトークンやセッションクッキーを検証するために必要な公開鍵証明書の取得に失敗した場合に発生します。[4]


これらの具体的なエラーを個別にハンドルしたい場合は、@admin_users_bp.errorhandler()デコレータをそれぞれのエラークラスに対して追加することで、より詳細なエラーハンドリングを実装できます。
"""

