
# pytestとFlaskのtest_clientを使ったテストは、デフォルトでは同期的に動作するため、awaitは不要です。
def test_admin_get_users_as_admin_first_page(client, admin_auth_headers):
    """管理者としてユーザーリストの1ページ目を正常に取得できるか"""

    response = client.get('/api/v1/admin/users', headers=admin_auth_headers)

    assert response.status_code == 200

    data = response.get_json()
    assert 'users' in data
    assert 'nextPageToken' in data

    # list_usersモックが10件返す設定なので、10件であることを確認
    assert len(data['users']) == 10
    # 最初のユーザーの情報を確認
    assert data['users'][0]['uid'] == 'test-uid-0'
    assert data['users'][0]['email'] == 'test0@example.com'
    # 次のページのトークン（開始インデックス）が正しいか確認
    assert data['nextPageToken'] == '10'


def test_admin_get_users_as_admin_second_page(client, admin_auth_headers):
    """管理者として、nextPageTokenを使って2ページ目を正常に取得できるか"""

    # 1ページ目のトークンを使って2ページ目をリクエスト
    response = client.get('/api/v1/admin/users?nextPageToken=10', headers=admin_auth_headers)

    assert response.status_code == 200

    data = response.get_json()
    assert len(data['users']) == 10
    # 2ページ目の最初のユーザーが正しいか確認
    assert data['users'][0]['uid'] == 'test-uid-10'
    assert data['nextPageToken'] == '20'


def test_admin_get_users_as_admin_last_page(client, admin_auth_headers):
    """管理者として、最後のページを取得した際にnextPageTokenがNoneになるか"""

    # 3ページ目（最後）をリクエスト
    response = client.get('/api/v1/admin/users?nextPageToken=20', headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    # 残りの5件が返される
    assert len(data['users']) == 5
    assert data['users'][0]['uid'] == 'test-uid-20'
    # 次のページがないので、トークンはNoneになることを確認
    assert data['nextPageToken'] is None


def test_admin_get_users_forbidden_for_normal_user(client, normal_user_auth_headers):
    """一般ユーザーがアクセスした際に403 Forbiddenエラーになるか"""
    # @admin_requiredデコレーターをテスト

    response = client.get('/api/v1/admin/users', headers=normal_user_auth_headers)

    assert response.status_code == 403 # Forbidden


def test_admin_get_users_unauthorized_without_token(client):
    """トークンなしでアクセスした際に401 Unauthorizedエラーになるか"""
    # @login_requiredデコレーターをテスト
    response = client.get('/api/v1/admin/users')

    assert response.status_code == 401 # Unauthorized




# tests/test_admin_users.py

# UserProfileモデルをインポートして、テストデータを作成できるようにする
from backend.models.user_profile import UserProfile

# ... (既存のテスト関数はそのまま) ...


# --- get_user_details のテスト ---

def test_get_user_details_success(client, admin_auth_headers, db_session):
    """
    【正常系】FirebaseユーザーとDBプロファイルの両方が存在する場合のテスト
    """
    # --- Arrange (準備) ---
    # conftestのモックが知っているユーザーUIDを指定
    target_uid = 'normal-uid-456'

    # このテストのために、対応するユーザープロファイルをDBに作成する
    # このレコードはテスト終了後にdb_sessionフィクスチャによって自動的にロールバックされる
    user_profile_in_db = UserProfile(
        user_id=target_uid,
        username='Normal User DB Profile',
        email='user@example.com', # Emailは重複していても良い
        bio='This is a test bio.'
    )
    db_session.add(user_profile_in_db)
    db_session.commit()

    # --- Act (実行) ---
    response = client.get(f'/api/v1/admin/users/{target_uid}', headers=admin_auth_headers)

    # --- Assert (検証) ---
    assert response.status_code == 200
    data = response.get_json()

    # 1. Firebaseからのデータが正しく含まれているか
    assert data['uid'] == target_uid
    assert data['email'] == 'user@example.com' # モックのFirebaseユーザーのEmail
    assert data['display_name'] == 'Normal User'
    assert data['disabled'] is False

    # 2. データベースからのデータが正しく含まれているか
    assert data['username'] == 'Normal User DB Profile'
    assert data['bio'] == 'This is a test bio.'


def test_get_user_details_profile_missing_raises_500(client, admin_auth_headers, db_session):
    """
    【異常系】DBプロファイルが存在しない場合に500エラーが発生するかのテスト
    """
    # --- Arrange (準備) ---
    # conftestのモックが知っているが、DBには登録しないユーザーUID
    target_uid = 'normal-uid-456'
    # このテストでは、db_session.add() を行わないことで、
    # 「Firebaseにはユーザーがいるが、DBにプロファイルがない」状況を作り出す

    # --- Act (実行) ---
    response = client.get(f'/api/v1/admin/users/{target_uid}', headers=admin_auth_headers)

    # --- Assert (検証) ---
    # 予期せぬRuntimeErrorは、Flaskによって捕捉され、
    # 500 Internal Server Error としてクライアントに返される
    assert response.status_code == 500


def test_get_user_details_firebase_user_not_found(client, admin_auth_headers):
    """
    【異常系】Firebaseにユーザーが存在しない場合に404エラーが返るかのテスト
    """
    # --- Arrange (準備) ---
    # conftestのモックが知らない、存在しないUIDを指定
    target_uid = 'non-existent-uid-999'

    # --- Act (実行) ---
    response = client.get(f'/api/v1/admin/users/{target_uid}', headers=admin_auth_headers)

    # --- Assert (検証) ---
    # auth.get_user(uid)がUserNotFoundErrorを発生させ、
    # それをエラーハンドラが404に変換することを期待する
    assert response.status_code == 404


def test_get_user_details_forbidden_for_normal_user(client, normal_user_auth_headers):
    """
    【認可テスト】一般ユーザーがアクセスした場合に403エラーになるか
    """
    target_uid = 'normal-uid-456' # 対象は誰でも良い
    response = client.get(f'/api/v1/admin/users/{target_uid}', headers=normal_user_auth_headers)
    assert response.status_code == 403


def test_get_user_details_unauthorized_without_token(client):
    """
    【認証テスト】未ログインでアクセスした場合に401エラーになるか
    """
    target_uid = 'normal-uid-456'
    response = client.get(f'/api/v1/admin/users/{target_uid}')
    assert response.status_code == 401