from pydantic import BaseModel, Field


class TipPath(BaseModel):
    tip_id: int


class TipTranslationPath(BaseModel):
    tip_id: int
    language: str


class TipQuery(BaseModel):
    language: str | None = Field(None, description="Language code for translations (e.g., 'es', 'en')")


class TipCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    order: int = 0
    is_active: bool = True


class TipUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    order: int | None = None
    is_active: bool | None = None


class TipTranslationCreate(BaseModel):
    language: str = Field(..., max_length=5)
    title: str = Field(..., max_length=255)
    description: str


class TipReorderItem(BaseModel):
    id: int = Field(..., description="ID of the tip")
    order: int = Field(..., description="New order position")


class TipReorderRequest(BaseModel):
    items: list[TipReorderItem] = Field(..., description="List of tips with their new order positions")
