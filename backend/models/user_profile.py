from datetime import date
from sqlalchemy.orm import mapped_column, Mapped

from backend.extensions import db
from backend.enums import Gender

class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    # Firebase Authenticationが生成するユーザーID（UID）最大128文字の空でない文字列
    uid: Mapped[str] = mapped_column(db.String(128), primary_key=True)

    # unique=Trueを指定すれば、パフォーマンス向上のためのインデックスも自動的に作成されます。
    display_name: Mapped[str] = mapped_column(db.String(50))

    birthday: Mapped[date|None] = mapped_column(db.Date())

    # native_enum=Falseにより、PostgreSQLのENUMを使用せず、どのDBでも動くVARCHAR + CHECK制約という方式でENUMを再現する。
    # native_enum=False の設定の時には、Enumで定義された値のみを許可するCHECK制約が自動的に追加されます。
    # 上記のnative_enum=Falseによって作成されるCHECK制約に、ck_user_profile_genderという名前を明示的に付けています
    # validate_strings=Trueによって、SQLAlchemyがデータベースに値を送る前に別のバリデーションを行う。
    # これらの設定は全て、SQLAlchemyのEnum型に特有の設定
    gender: Mapped[Gender|None] = mapped_column(db.Enum(
        Gender,
        native_enum=False, # DB側でVARCHAR + CHECK制約でバリデーション
        constraint_name='ck_user_profile_gender',
        validate_strings=True, # Python側でのバリデーションを有効にする特別な設定
    ))

    # True/Falseのように値の種類が極端に少ない列では、インデックスが検索効率にあまり貢献しないことがある。
    is_admin: Mapped[bool] = mapped_column(db.Boolean(), default=False)


    def __repr__(self):
        gender_value = self.gender.value if self.gender else None

        return f'<UserProfile id:{self.id} name:"{self.name}" birthday:{self.birthday} gender:{gender_value} is_admin:{self.is_admin}>'



