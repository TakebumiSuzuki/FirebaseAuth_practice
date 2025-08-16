from pydantic import BaseModel, Field, field_validator
from typing import Annotated
from datetime import date
from ..enums import Gender


# バリデーションが成功した場合、入力をGender.MALEのようなEnumオブジェクトに変換してくれる。
class UpdateUserProfile(BaseModel):
    birthday: Annotated[date|None, Field(description="The user's date of birth in ISO 8601 format (YYYY-MM-DD).")]
    gender: Annotated[Gender|None, Field(description="The user's gender.")]

    @field_validator('birthday')
    @classmethod
    def validate_age(cls, value: date | None) -> date | None:
        """誕生日が入力された場合、18歳以上であることを確認する"""
        if value is None:
            return None

        today = date.today()

        # 年齢を計算する
        # (今年の年 - 誕生年) から、
        # まだ今年の誕生日を迎えていない場合は1を引く
        # (today.month, today.day) < (value.month, value.day) は True(1) or False(0) を返す
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

        if age < 18:
            raise ValueError("18歳未満のユーザーは登録できません")

        return value




class ReadUserProfile(BaseModel):
    pass

class PublicUserProfile(BaseModel):
    pass
