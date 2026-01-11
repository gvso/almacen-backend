from dependency_injector import containers, providers

from app.services.cloud_storage import CloudStorageService
from app_settings import settings


class ServiceContainer(containers.DeclarativeContainer):
    """Container for third-party service integrations."""

    cloud_storage = providers.Singleton(
        CloudStorageService,
        service_account_json=settings.google.service_account_json,
        bucket_name=settings.google.storage_bucket,
    )
