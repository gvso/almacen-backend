from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    password: str = Field(..., description="Admin password")


class LoginResponse(BaseModel):
    token: str = Field(..., description="JWT access token")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    error_description: str = Field(..., description="Error description")
