from flask import Blueprint, request, jsonify, current_app, g
from firebase_admin import auth
from sqlalchemy.exc import SQLAlchemyError
from backend.schemas.user_profile import ReadUserProfile
from backend.schemas.firebase_user import AdminReadFirebaseUser
from pydantic import ValidationError
from backend.extensions import db
from backend.decorators import login_required, admin_required, payload_required, target_user_required_in_payload
from backend.models.user_profile import UserProfile



# from datetime import datetime, timezone
# タイムスタンプ（ミリ秒）をISO 8601形式の文字列に変換するヘルパー関数
# def format_timestamp(ts_ms):
#     if not ts_ms:
#         return None
#     # ミリ秒を秒に変換
#     return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).isoformat()

admin_users_bp = Blueprint('admin_users', __name__, url_prefix='/api/v1/admin/users')


@admin_users_bp.get('')
# @login_required
# @admin_required
def admin_get_users():
    # nextPageToken が存在しなければ、戻り値は None になるので、Noneは書かなくても良い。
    page_token = request.args.get('nextPageToken', None)

    # max_resultsで取得件数を10件に指定。page_tokenがあれば、その続きから取得する
    # page_tokenは、Firebaseが生成する、非常に長い暗号化されたような文字列
    page = auth.list_users(max_results=10, page_token=page_token)

    users_list = [
        AdminReadFirebaseUser.model_validate(user).model_dump()
        for user in page.users
    ]

    response = {
        'users': users_list,
        'nextPageToken': page.next_page_token or None # 空文字列の場合もNoneに統一
    }
    return jsonify(response), 200


@admin_users_bp.get('/<string:uid>')
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


@admin_users_bp.post('/change-disabled')
@login_required
@admin_required
@payload_required
@target_user_required_in_payload
def admin_change_user_disable():

    auth.update_user(g.target_user.uid, disabled = not g.target_user.disabled)

    return jsonify({
        'uid': g.target_user.uid,
        'disabled': not g.target_user.disabled
    }), 200


@admin_users_bp.post('/change-role')
@login_required
@admin_required
@payload_required
@target_user_required_in_payload
def admin_change_user_role():

    custom_claims = g.target_user.custom_claims or {}

    current_is_admin = custom_claims.get('is_admin', False)

    user_profile = db.session.get(UserProfile, g.target_user.uid)
    user_profile.is_admin = not current_is_admin

    #    第一引数: uid, 第二引数: 更新したいクレームをすべて含んだ辞書
    auth.set_custom_user_claims(g.target_user.uid, {'is_admin': not current_is_admin})

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.critical(f"CRITICAL: Data inconsistency detected for user UID '{g.target_user.uid}'. "
    f"The Firebase user is_admin field was changed, but the corresponding database profile is_admin could not be changed. "
    f"Manual modification of the UserProfile is required. DB Error: {e}")
        raise

    return jsonify({
        'uid': g.target_user.uid,
        'is_admin': not current_is_admin # フロントエンドの命名規則に合わせてキャメルケースにすることも
    }), 200


@admin_users_bp.post('/delete-user')
@login_required
@admin_required
@payload_required
@target_user_required_in_payload
def delete_user():
    print('ここです1')
    user_profile = db.session.get(UserProfile, g.target_user.uid)
    print('ここです')
    if user_profile:
        db.session.delete(user_profile)
    # 存在しない場合は何もしないでOK。最終的な目標はユーザーが消えることだから。
    auth.delete_user(g.target_user.uid)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.critical(f"CRITICAL: Data inconsistency detected for user UID '{g.target_user.uid}'. "
    f"The Firebase user was deleted, but the corresponding database profile could not be committed. "
    f"Manual cleanup of the UserProfile is required. DB Error: {e}")
        raise

    return jsonify({}), 204



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

