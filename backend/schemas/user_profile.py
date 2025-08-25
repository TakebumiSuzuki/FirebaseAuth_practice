from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Annotated
from datetime import date
from backend.enums import Gender


class PublicUserProfile(BaseModel):
    id: Annotated[str, Field(description="The unique identifier for the user (Firebase UID).")]
    display_name: Annotated[str, Field(description="The user's display name.")]
    birthday: Annotated[date | None, Field(description="The user's date of birth in ISO 8601 format (YYYY-MM-DD).")]
    gender: Annotated[Gender | None, Field(description="The user's gender.")]

    model_config = ConfigDict(from_attributes=True)



class ReadUserProfile(BaseModel):
    id: Annotated[str, Field(description="The unique identifier for the user (Firebase UID).")]
    display_name: Annotated[str, Field(description="The user's display name.")]
    birthday: Annotated[date | None, Field(description="The user's date of birth in ISO 8601 format (YYYY-MM-DD).")]
    gender: Annotated[Gender | None, Field(description="The user's gender.")]
    is_admin: Annotated[bool, Field(description="A boolean flag indicating if the user has administrator privileges.")]

    model_config = ConfigDict(from_attributes=True)


class UpdateUserProfile(BaseModel):
    display_name: Annotated[str, Field(description="The user's display name.")]
    birthday: Annotated[date | None, Field(
        description="The user's date of birth in ISO 8601 format (YYYY-MM-DD)."
    )]
    gender: Annotated[Gender | None, Field(
        description="The user's gender."
    )]

    @field_validator('birthday')
    @classmethod
    def validate_age(cls, value: date | None) -> date | None:
        if value is None:
            return None
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise ValueError("User must be 18 years or older to register.")
        return value