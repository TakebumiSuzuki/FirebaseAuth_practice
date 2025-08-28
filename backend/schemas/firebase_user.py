from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from datetime import datetime, timezone

class CustomClaims(BaseModel):
    # デフォルト値 False は、フィールドが存在しない場合に適用されます。よって,フィールドがなくてもバリエーションエラーにならない。
    # Pydanticは「型の強制（type coercion）」を行い、bool型に変換可能な値は自動で変換しようと試みます。
    # 0はFalseに変換され、1はTrueに変換されるが、nullはbool型と互換性がないため、バリデーションエラーを引き起こす。
    is_admin: bool = False

class Metadata(BaseModel):
    # Pydanticは入力された数値（intやfloat）をUnixタイムスタンプと解釈し、自動でdatetimeオブジェクトに変換しようとします。
    # Firebase Admin SDK for Pythonは、日時データを**Unixタイムスタンプ（float型）**として返します、が、しかし、
    # Firebase Admin SDKはミリ秒単位のUnixタイムスタンプを返してくるので、バリデーターが必要になる。
    creation_timestamp: datetime
    # last_sign_in_timestampはユーザーが一度もログインしていない場合 None になる可能性があるため、| None を追加するのが安全です。
    last_sign_in_timestamp: datetime | None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('creation_timestamp', 'last_sign_in_timestamp', mode='before')
    @classmethod
    def convert_ms_to_datetime(cls, v: int | float | None) -> datetime | None:
        if v is None:
            return None
        # Firebaseから返されるのはミリ秒単位のタイムスタンプなので、1000で割って秒単位に変換する
        # さらに、tz=timezone.utc を明示的に指定することで、アウェアな（Aware）datetimeオブジェクトにしている
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc)


class UserReadFirebaseUser(BaseModel):
    uid: str
    email: EmailStr | None
    display_name: str | None
    user_metadata: Metadata
    # from_attributes=True を設定することで、auth.get_user(uid) のような
    # オブジェクトの属性 (user.uid, user.emailなど) からデータを読み込めるようになる
    model_config = ConfigDict(from_attributes=True)


class AdminReadFirebaseUser(BaseModel):
    uid: str
    email: EmailStr | None
    display_name: str | None
    custom_claims: CustomClaims | None
    disabled: bool
    user_metadata: Metadata | None

    model_config = ConfigDict(from_attributes=True)

class UserUpdateFirebaseUser(BaseModel):
    email: EmailStr | None = None
    display_name: str | None = None

    model_config = ConfigDict(from_attributes=True)

"""
バリデーターが使われるタイミング: @field_validatorは、基本的にデータの入力時（デシリアライズ）にのみ機能します。
つまり、APIから受け取ったデータ（JSONなど）や辞書からPydanticモデルのインスタンスを作成する際に使われます。
Pythonオブジェクトから辞書やJSONへ変換する際（シリアライズ）には、このバリデーターは呼び出されません。

Pydanticモデルのインスタンスを作成する時、辞書データーには model_validate を使い、jsonには model_validate_json を使う。
ただし、model_config = ConfigDict(from_attributes=True)の設定がある場合、
model_validateには、属性を持つ'任意のPythonオブジェクト'も入れられるようになる。

Firebase Admin SDK for Python (firebase-admin)が返すユーザーデータはUserRecordという名前のPythonのオブジェクト。
よって、model_config = ConfigDict(from_attributes=True)の記述があれば model_validate を使える。
"""

"""
FB authからのレスポンスの形式はこんな感じになっている。
[重要]これは、auth.get_user() などでサーバーから直接ユーザー情報を取得した際のもの。UserRecord オブジェクト。
で、これは、auth.verify_id_token() が返すデコード済みIDトークンとは構造が多少異なる。
{
  "uid": "some-uid",
  "email": "user@example.com",
  "display_name": "Taro Yamada",
  "photo_url": "https://example.com/photo.jpg",
  "phone_number": "+819012345678",
  "email_verified": true,
  "disabled": false,
  "custom_claims": {
    "admin": true,
    "role": "moderator"
  },
  "user_metadata": {
    "creation_timestamp": 1627812000000,
    "last_sign_in_timestamp": 1692600000000
  },
  "provider_data": [
    {
      "uid": "user@example.com",
      "provider_id": "password",
      "email": "user@example.com",
      "display_name": null,
      "photo_url": null
    }
  ]
}
"""










