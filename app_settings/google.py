from pydantic import Field
from pydantic_settings import BaseSettings


class GoogleCloudSettings(BaseSettings):
    service_account_json: str = Field(default=..., alias="GOOGLE_SERVICE_ACCOUNT_JSON")
    storage_bucket: str = Field(default=..., alias="GOOGLE_STORAGE_BUCKET")
