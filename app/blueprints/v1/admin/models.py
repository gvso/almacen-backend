from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.order import OrderStatus
from app.models.product import ProductType


class OrderPath(BaseModel):
    order_id: str


class OrderStatusUpdate(BaseModel):
    status: OrderStatus = Field(..., description="New order status")


class OrderUpdate(BaseModel):
    label: str | None = Field(None, max_length=100, description="Custom label for the order")


class LoginRequest(BaseModel):
    password: str = Field(..., description="Admin password")


class LoginResponse(BaseModel):
    token: str = Field(..., description="JWT access token")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    error_description: str = Field(..., description="Error description")


# Product models
class AdminProductQuery(BaseModel):
    search: str | None = None
    type: ProductType | None = None
    tag_ids: str | None = Field(None, description="Comma-separated list of tag IDs to filter by")


class ProductPath(BaseModel):
    product_id: int


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    price: Decimal
    image_url: str | None = None
    order: int = 0
    is_active: bool = True
    type: ProductType = ProductType.product


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    image_url: str | None = None
    order: int | None = None
    is_active: bool | None = None
    type: ProductType | None = None


# Translation models
class TranslationPath(BaseModel):
    product_id: int
    language: str


class TranslationCreate(BaseModel):
    language: str = Field(..., max_length=5)
    name: str = Field(..., max_length=255)
    description: str | None = None


# Variation models
class VariationPath(BaseModel):
    product_id: int
    variation_id: int


class VariationCreate(BaseModel):
    name: str = Field(..., max_length=255)
    price: Decimal | None = None
    image_url: str | None = None
    order: int | None = None
    is_active: bool = True


class VariationUpdate(BaseModel):
    name: str | None = None
    price: Decimal | None = None
    image_url: str | None = None
    order: int | None = None
    is_active: bool | None = None


# Variation translation models
class VariationTranslationPath(BaseModel):
    product_id: int
    variation_id: int


class VariationTranslationDeletePath(BaseModel):
    product_id: int
    variation_id: int
    language: str


class VariationTranslationCreate(BaseModel):
    language: str = Field(..., max_length=5)
    name: str = Field(..., max_length=255)


# Reorder models
class ReorderItem(BaseModel):
    id: int = Field(..., description="ID of the item")
    order: int = Field(..., description="New order position")


class ReorderRequest(BaseModel):
    items: list[ReorderItem] = Field(..., description="List of items with their new order positions")


# Image upload models
class ImageUploadRequest(BaseModel):
    content_type: str = Field(..., description="MIME type of the image (e.g., 'image/jpeg')")


class SignedUploadUrlResponse(BaseModel):
    upload_url: str = Field(..., description="Signed URL for uploading via PUT request")
    public_url: str = Field(..., description="Public URL of the image after upload")
