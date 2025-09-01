import os
from datetime import datetime, timezone
import pytest

from backend.app import create_app
from backend.extensions import db
from backend.models.user_profile import UserProfile


@pytest.fixture(scope='session')
def app():
    """テスト用のFlaskアプリケーションインスタンスを作成"""
    # テスト環境の環境変数を明示的に設定（Docker Composeの設定を上書き保証）
    os.environ['TEST_MODE'] = 1
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db_test:5432/mydatabase'

    app = create_app()
    # WSGIサーバーがスレッディングを使ってasyncioと似たような仕組みで並列処理をするときにコンテキストは必要となる。
    # Flask開発サーバーでは、基本同期的にしか動かないのでコンテキストは不要ではあるが、flaskの仕組みとして
    # コンテキストを使って個別領域でリクエストを処理していくということになっているため、これが必要、とのこと。
    # app.test_clientを使ったリクエストの場合はコンテキストを作ってくれるが、database fixture作成の場面では、
    # app.test_clientを経由しないため、db.create_all() の箇所でエラーとなる。そのため、以下の with句 が必要。
    with app.app_context():
        yield app
    #scope='session' で定義されているため、pytestのテストセッション全体が終了する直前に yield の次の行に進みます。


@pytest.fixture(scope='session')
def database(app):
    # db = SQLAlchemy(app)でSQLAlchemyインスタンスを作成すると、そのインスタンスはdb.metadataという
    # メタデータのコンテナを保持します。そして、db.Modelを継承してモデルクラスを定義すると、そのクラスの情報が
    # 自動的にdb.metadataに登録されます。db.create_all()を呼び出すと、このdb.metadataに登録されている
    # 全てのモデル定義をスキャンし、それに対応するCREATE TABLE ...というSQL文を生成します。
    # 上で作った app context の中で、以下が実行される.
    db.create_all()

    yield db

    # 全てのテーブルを削除するSQL文を発行し、後片付けを行う
    db.drop_all()


@pytest.fixture(scope='function')
def db_session(database):
    """各テスト用のデータベースセッション（トランザクション管理）"""
    # トランザクション開始
    connection = database.engine.connect()
    transaction = connection.begin() # <-- SQL: BEGIN TRANSACTION; が発行される

    # セッションをトランザクションにバインド
    session = database.create_scoped_session(
        options={'bind': connection, 'binds': {}}
    )

    # 本来は databaseのsession属性にはプロキシオブジェクトが代入されているが、
    # それを強引にテスト用の素の session にしてしまう。
    # このように、　ソフトウェアの実行中に、既存のモジュールやクラス、オブジェクトの振る舞いを動的に（その場で）
    # 変更するというテクニックをモンキーパッチという。印刷された本に、後から上からシールを貼って単語を書き換えるような
    # イメージです。元の本（ソースコード）は一切変更せず、読むその瞬間だけ、内容が変わって見えるようにする、
    # というゲリラ的な修正手法です。
    database.session = session

    yield session

    # テスト終了後にロールバック
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app, db_session):
    """
    [ test_clientとは ]
    1. HTTPリクエストをシミュレートする
        client.get('/users')やclient.post('/items')のように、コード上でHTTPリクエストを模倣します。
        これにより、URLルーティングからビュー関数の実行、レスポンスの生成まで、一連の流れをテストできます。
    2. リクエストコンテキストを自動で生成する
        test_clientはリクエストをシミュレートする際に、本番環境とほぼ同じリクエストコンテキストを自動的に作成します。
    3. requestやgオブジェクトが使える
        上記の結果として、テスト対象のビュー関数は、本番時と全く同じようにrequestオブジェクト（例：request.json）や
        gオブジェクトにアクセスできます。(これらが使えないと、ほとんどのビュー関数はテストできません。)
    """
    return app.test_client()


@pytest.fixture
def admin_auth_headers():
    """管理者ユーザー用の認証ヘッダーを生成するフィクスチャ"""
    return {
        'Authorization': 'Bearer mock-admin-token',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def normal_user_auth_headers():
    """一般ユーザー用の認証ヘッダーを生成するフィクスチャ"""
    return {
        'Authorization': 'Bearer mock-normal-user-token',
        'Content-Type': 'application/json'
    }


# @pytest.fixture
# def sample_user(db_session):
#     """テスト用のサンプルユーザー"""
#     user = User(
#         firebase_uid='test-uid-123',
#         email='test@example.com',
#         name='Test User'
#     )
#     db_session.add(user)
#     db_session.commit()
#     return user


# @pytest.fixture
# def multiple_users(db_session):
#     """複数のテストユーザー"""
#     users = []
#     for i in range(3):
#         user = User(
#             firebase_uid=f'test-uid-{i}',
#             email=f'test{i}@example.com',
#             name=f'Test User {i}'
#         )
#         users.append(user)
#         db_session.add(user)

#     db_session.commit()
#     return users



# --- モックデータ用のヘルパークラス ---
# Firebase Admin SDKが返すオブジェクトの構造を模倣します

class MockUserMetadata:
    """user_metadata属性を模倣するクラス"""
    def __init__(self, creation_timestamp_ms, last_sign_in_timestamp_ms):
        # Pydanticバリデータがミリ秒を想定しているため、ミリ秒で設定
        self.creation_timestamp = creation_timestamp_ms
        self.last_sign_in_timestamp = last_sign_in_timestamp_ms

class MockFirebaseUser:
    """auth.get_userやlist_usersの要素が返すUserRecordを模倣するクラス"""
    def __init__(self, uid, email, display_name, disabled, custom_claims=None, metadata=None):
        self.uid = uid
        self.email = email
        self.display_name = display_name
        self.disabled = disabled
        self.custom_claims = custom_claims or {}
        self.user_metadata = metadata

class MockListPage:
    """auth.list_usersが返すページオブジェクトを模倣するクラス"""
    def __init__(self, users, next_page_token):
        self.users = users
        self.next_page_token = next_page_token



# autouse=Trueが指定されたフィクスチャは、テスト関数が引数として明示的に要求しなくても、
# そのフィクスチャが有効なスコープ内のすべてのテストで自動的に実行されます
@pytest.fixture(autouse=True)
# monkeypatchは、pytestに標準で組み込まれている、組み込みフィクスチャの一つ
# monkeypatch は 毎テストごとに新しく生成され提供される
def mock_firebase_auth(monkeypatch):
    """Firebase認証を自動的にモック"""

    # --- モック用のユーザーデータを定義 ---
    now_ms = datetime.now(timezone.utc).timestamp() * 1000

    MOCK_ADMIN_USER = MockFirebaseUser(
        uid='admin-uid-123',
        email='admin@example.com',
        display_name='Admin User',
        disabled=False,
        custom_claims={'is_admin': True},
        metadata=MockUserMetadata(now_ms - 2000000, now_ms - 100000)
    )
    MOCK_NORMAL_USER = MockFirebaseUser(
        uid='normal-uid-456',
        email='user@example.com',
        display_name='Normal User',
        disabled=False,
        custom_claims={'is_admin': False},
        metadata=MockUserMetadata(now_ms - 5000000, now_ms - 300000)
    )

    # --- list_usersで返すためのユーザーリスト ---
    # ページネーションをテストするために複数作成
    ALL_MOCK_USERS = [
        MockFirebaseUser(
            f'test-uid-{i}',
            f'test{i}@example.com',
            f'Test User {i}',
            False,
            None,
            MockUserMetadata(now_ms - (i * 100000), now_ms)
        )
        for i in range(25) # 10件区切りで3ページ分のデータを作成
    ]

    def mock_verify_id_token(token, check_revoked=False):
        """トークン検証をモック。デコレーターが最初に呼び出す"""
        if token == 'mock-admin-token':
            return {'uid': MOCK_ADMIN_USER.uid}
        if token == 'mock-normal-user-token':
            return {'uid': MOCK_NORMAL_USER.uid}
        raise ValueError('Invalid token')

    def mock_get_user(uid):
        """ユーザー情報取得をモック。デコレーターが次に呼び出す"""
        if uid == MOCK_ADMIN_USER.uid:
            return MOCK_ADMIN_USER
        if uid == MOCK_NORMAL_USER.uid:
            return MOCK_NORMAL_USER
        raise ValueError(f"Mock user not found for uid: {uid}")

    def mock_list_users(max_results=10, page_token=None):
        """ユーザーリスト取得をモック。View関数本体が呼び出す"""
        start_index = int(page_token) if page_token else 0
        end_index = start_index + max_results

        users_on_page = ALL_MOCK_USERS[start_index:end_index]

        next_page_token = str(end_index) if end_index < len(ALL_MOCK_USERS) else ''

        return MockListPage(users_on_page, next_page_token)

    # このフィクスチャは、monkeypatchを使ってfirebase_admin.authモジュールのverify_id_tokenとget_user関数を、
    # テスト用のモック関数に置き換えています。この「置き換え」という副作用がフィクスチャの主目的であり、
    # 何か値を返す必要はありません。
    # Pythonのメモリ空間でfirebase_admin.authモジュールが持っているverify_id_tokenという名前が指し示す先が、
    # オリジナルの関数から、あなたが定義したmock_verify_id_token関数へと一時的に変更されます。
    monkeypatch.setattr('firebase_admin.auth.verify_id_token', mock_verify_id_token)
    monkeypatch.setattr('firebase_admin.auth.get_user', mock_get_user)
    monkeypatch.setattr('firebase_admin.auth.list_users', mock_list_users)
    # monkeypatchは有効なスコープ（通常はテスト関数ごと）が終了すると、行った変更をすべて自動的に元に戻してくれます。
    # そのため、このケースでは開発者が明示的に後処理を書く必要がなく、yieldも不要になります。



"""
開発・本番環境におけるデータベースセッション管理の流れ（時系列順）

前提：アプリケーションの初期化時
まず、あなたのアプリケーションコードで db = SQLAlchemy(app) が実行された時点で、Flask-SQLAlchemyは db.session という名前の特別なオブジェクトを準備します。 これこそが、SQLAlchemyが提供する scoped_session という仕組みを利用したプロキシ（代理）オブジェクトです。この時点では、まだ実際のデータベースセッションは存在しません。db.session は、来るべきリクエストに備えて「いつでも適切なセッションを用意・提供できる代理人」として待機している状態です。


あるHTTPリクエストが発生してから完了するまで

ステップ1：リクエストの受信
クライアント（Webブラウザなど）からサーバーに対してHTTPリクエストが送信されます。

ステップ2：Flaskによるコンテキストの生成
Flaskアプリケーションがリクエストを受け取ります。URLルーティングに従って、処理を担当するビュー関数を決定します。そして、そのビュー関数を実行する直前に、Flaskは**「リクエストコンテキスト」**を生成します。このコンテキストの中には、requestオブジェクト（リクエスト情報）やgオブジェクト（リクエスト中の一時的なデータストア）などが用意されます。

ステップ3：db.sessionへの最初のアクセス
ビュー関数の中で、user = User(...) の後に db.session.add(user) のように、あなたが初めて db.session にアクセスします。

ステップ4：scoped_session プロキシの仕事
ここで待機していた代理人、db.session（scoped_session）が動き出します。
まず、「現在のリクエストコンテキストに紐付いたデータベースセッションは既に存在するか？」をチェックします。
（このリクエストでは初めてのアクセスなので）存在しないことを確認すると、Flask-SQLAlchemyはデータベースへの接続プールから接続を取得し、このリクエスト専用の新しいデータベースセッションを作成します。 同時に、このセッションに対するトランザクションも開始されます。
作成した新しいセッションを、現在のリクエストコンテキストに紐付けて保存します。
そして、その新しいセッションをあなたのコード（db.session.add()を呼び出した場所）に返します。

ステップ5：データベース操作の実行
あなたのビュー関数内のコード（db.session.add(), db.session.commit(), db.session.get() など）は、ステップ4で提供された、このリクエスト専用のセッションを使って実行されます。もし同じビュー関数内で再度 db.session を呼び出しても、scoped_session は「既にこのリクエスト用のセッションがあるな」と判断し、ステップ4で作成した全く同じセッションを返します。これにより、リクエスト処理中は常に一貫したセッションが利用されることが保証されます。

ステップ6：ビュー関数からレスポンスが返される
ビュー関数の処理がすべて完了し、クライアントに返すためのレスポンスが生成されます。

ステップ7：リクエストの終了と自動的な後処理
Flaskはリクエストの処理が終わったので、ステップ2で作成したリクエストコンテキストを破棄しようとします。その直前、Flaskの**teardown_appcontext**という仕組み（フック）が作動します。
Flask-SQLAlchemyは、初期化の段階で「リクエストコンテキストが終了する際には、必ずこの関数を呼び出してください」という後処理関数をこのフックに登録しています。

ステップ8：セッションのクリーンアップ
teardown_appcontextフックによって、Flask-SQLAlchemyの後処理関数が自動的に呼び出されます。この関数は以下の処理を行います。
ビュー関数の実行中にエラー（例外）が発生していなければ、db.session.commit() を実行して、そのリクエスト内で行われた全てのデータベース変更を確定させます。
エラーが発生していた場合は、db.session.rollback() を実行し、全ての変更を無かったことにします。
最後に、セッションを remove() または close() して、データベース接続を接続プールに返却します。

結論
この一連の自動化された流れ、いわば「Flask-SQLAlchemyの魔法」のおかげで、開発者はセッションの生成、コミット、ロールバック、クローズといった煩雑な管理を一切意識する必要がありません。ただ db.session という便利な代理人を呼び出すだけで、リクエストごとに適切に管理されたセッションを通じて安全にデータベースを操作できるのです。


"""

"""
テストにおけるSAVEPOINTの役割と全体戦略

テストにおけるデータベース管理は、**「データの永続化」を目的とする開発・本番環境とは異なり、「各テストの独立性と再現性の確保」**を最優先とします。この目的を達成するために、以下の仕組みが連携して機能しています。

1. 基本はSQLの標準機能
まず、トランザクションの途中に中間的な保存ポイントを作る**SAVEPOINT**という概念は、PythonやSQLAlchemyの発明ではなく、多くのデータベースシステムが標準で持っている基本的な機能です。

2. SQLAlchemyの賢い抽象化
SQLAlchemyは、このSAVEPOINT機能を抽象化し、開発者が意識しなくても済むようにしています。開発者がdb.session.commit()を呼び出すと、SQLAlchemyは現在の状況を判断します。
通常の状況下では: COMMITというSQLを発行します。
既に大きなトランザクションの中にいる状況下では（テストフィクスチャなど）: COMMITの代わりに**SAVEPOINT**を発行します。
これにより、開発者はいつでも同じdb.session.commit()というコードを書くだけで、SQLAlchemyが裏側で最適なSQLを使い分けてくれます。

3. テスト戦略における役割分担
この仕組みを利用したテスト戦略は、明確な役割分担で成り立っています。
主役：transaction.rollback()
クリーンなデータベースを保証する真の主役は、テストフィクスチャの最後に実行される、巨大なトランザクション全体を無かったことにするrollback()です。これがあるからこそ、データベースの状態はテストの前後で完全に元通りになります。
助演：SAVEPOINT
SAVEPOINTは、この主役の戦略を成功させるための、最高のサポーターです。テストコードの内部でdb.session.commit()が呼ばれても、それが本物のCOMMITとなって巨大なトランザクションを破壊してしまわないように、**一時的な保存ポイントとして「受け流す」**役割を担います。これにより、テストコードの自由度を保ちつつ、全体の戦略は守られます。

結論
この**「テスト全体を一つの巨大なトランザクションで囲み、最後に必ずロールバックする」という基本戦略と、それを陰で支える「SQLAlchemyによるSAVEPOINTの賢い活用」**という二つの要素が組み合わさることで、各テストが他のテストの影響を受けない、理想的でクリーンなテスト環境が実現されているのです。
"""