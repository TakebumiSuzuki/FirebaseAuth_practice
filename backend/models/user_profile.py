from ..extensions import db
from sqlalchemy.orm import mapped_column, Mapped
from datetime import date
from ..enums import Gender


class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    # Firebase Authenticationが生成するユーザーID（UID）最大128文字の空でない文字列
    id: Mapped[str] = mapped_column(db.String(128), primary_key=True)

    # unique=Trueを指定すれば、パフォーマンス向上のためのインデックスも自動的に作成されます。
    name: Mapped[str] = mapped_column(db.String(50))

    birthday: Mapped[date|None] = mapped_column(db.Date())

    # native_enum=Falseにより、どのDBでも動くVARCHAR + CHECK制約という方式でENUMを再現する。
    # native_enum=Falseという前提の下、constraint_nameパラメータは、このCHECK制約の名前を指定するために使われます
    # validate_strings=Trueによって、アプリケーション側で事前にチェックを行う。
    gender: Mapped[Gender|None] = mapped_column(db.Enum(
        Gender,
        native_enum=False,
        constraint_name='ck_user_profile_gender',
        validate_strings=True,
    ))

    # True/Falseのように値の種類が極端に少ない列では、インデックスが検索効率にあまり貢献しないことがある。
    is_admin: Mapped[bool] = mapped_column(db.Boolean(), default=False)


    def __repr__(self):
        gender_value = self.gender.value if self.gender else None
        return f'<UserProfile id:{self.id} name:"{self.name}" birthday:{self.birthday} gender:{gender_value} is_admin:{self.is_admin}>'



