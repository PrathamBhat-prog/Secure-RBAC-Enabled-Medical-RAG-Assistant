from pydantic import BaseModel, field_validator


ALLOWED_ROLES = ("admin", "doctor", "nurse", "patient", "other")


class SignupRequest(BaseModel):
    username: str
    password: str
    role: str

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise ValueError("username must be at least 3 characters")
        if len(cleaned) > 64:
            raise ValueError("username must be at most 64 characters")
        return cleaned

    @field_validator("password")
    @classmethod
    def password_must_be_valid(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("password must be at least 6 characters")
        return value

    @field_validator("role")
    @classmethod
    def role_must_be_allowed(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_ROLES:
            raise ValueError(f"role must be one of: {', '.join(ALLOWED_ROLES)}")
        return cleaned
