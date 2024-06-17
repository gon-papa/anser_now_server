

import re

def length_1to100_validator(cls, value):
    if len(value) < 1:
        raise ValueError("1文字以上で入力してください")
    if len(value) >= 100:
        raise ValueError("100文字以下で入力してください")
    return value

def email_validator(cls, value):
    email_regex = r"^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    if not re.match(email_regex, value):
        raise ValueError("メールアドレスの形式が正しくありません")
    return value

def password_validator(cls, value):
    if len(value) < 8:
        raise ValueError("8文字以上で入力してください")
    if len(value) >= 20:
        raise ValueError("20文字以下で入力してください")
    # 半角英数字と記号のみ
    if not re.match(r"^[@?$%!#0-9a-zA-Z]+$", value):
        raise ValueError("半角英数字と記号(@?$%!)のみで入力してください")
    return value

