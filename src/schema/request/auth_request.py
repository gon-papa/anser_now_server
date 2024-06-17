from pydantic import BaseModel, Field, field_validator

from src.schema.request.common_request import email_validator, length_1to100_validator, password_validator


class SignUpRequest(BaseModel):
    account_name: str = Field(
        ...,
        title="アカウント名",
        description="アカウント名",
    )
    email: str = Field(
        ...,
        title="メールアドレス",
        description="メールアドレス",
    )
    password: str = Field(
        ...,
        title="パスワード",
        description="パスワード",
    )

    @field_validator("account_name", "email")
    def name_length_validator(cls, value):
        return length_1to100_validator(cls, value)

    @field_validator("email")
    def email_validator(cls, value):
        return email_validator(cls, value)

    @field_validator("password")
    def password_validator(cls, value):
        return password_validator(cls, value)
    
    
class SignInRequest(BaseModel):
    email: str = Field(
        ...,
        title="メールアドレス",
        description="メールアドレス",
    )
    password: str = Field(
        ...,
        title="パスワード",
        description="パスワード",
    )

    @field_validator("email")
    def email_validator(cls, value):
        return email_validator(cls, value)

    @field_validator("password")
    def password_validator(cls, value):
        return password_validator(cls, value)
