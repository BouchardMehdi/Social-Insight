from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

WorkspaceRole = Literal["owner", "admin", "member"]
AssignableWorkspaceRole = Literal["admin", "member"]


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=100)
    workspace_name: str | None = Field(default=None, min_length=2, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.casefold().strip()
        if normalized.count("@") != 1 or "." not in normalized.rsplit("@", 1)[1]:
            raise ValueError("A valid email address is required.")
        return normalized


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.casefold().strip()


class CreateWorkspaceRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class AddWorkspaceMemberRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    role: AssignableWorkspaceRole = "member"

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.casefold().strip()


class UserRead(BaseModel):
    id: str
    email: str
    display_name: str
    created_at: datetime


class WorkspaceRead(BaseModel):
    id: str
    name: str
    role: WorkspaceRole
    created_at: datetime


class SessionResponse(BaseModel):
    user: UserRead
    workspaces: list[WorkspaceRead]
    active_workspace_id: str


class AuthResponse(SessionResponse):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserRecord(UserRead):
    password_hash: str


class WorkspaceRecord(BaseModel):
    id: str
    name: str
    created_at: datetime


class MembershipRecord(BaseModel):
    user_id: str
    workspace_id: str
    role: WorkspaceRole
    created_at: datetime


class WorkspaceMemberRead(BaseModel):
    user_id: str
    email: str
    display_name: str
    role: WorkspaceRole
    joined_at: datetime


class WorkspaceContext(BaseModel):
    user: UserRead
    workspace: WorkspaceRead
