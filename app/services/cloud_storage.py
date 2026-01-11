import json
import uuid
from datetime import timedelta

from google.cloud import storage  # type: ignore[import-untyped]
from google.oauth2 import service_account  # type: ignore[import-untyped]


class CloudStorageService:
    """Service for uploading files to Google Cloud Storage."""

    def __init__(self, service_account_json: str, bucket_name: str) -> None:
        credentials_info = json.loads(service_account_json)
        self._credentials = service_account.Credentials.from_service_account_info(credentials_info)
        self._client = storage.Client(credentials=self._credentials, project=credentials_info.get("project_id"))
        self._bucket_name = bucket_name

    def generate_signed_upload_url(
        self,
        content_type: str,
        folder: str = "products",
        expiration_minutes: int = 15,
    ) -> dict[str, str]:
        """
        Generate a signed URL for uploading an image directly to Cloud Storage.

        Args:
            content_type: MIME type of the image (e.g., 'image/jpeg')
            folder: Folder path within the bucket
            expiration_minutes: How long the signed URL is valid

        Returns:
            Dict with 'upload_url' (signed URL for PUT request) and 'public_url' (final URL after upload)
        """
        bucket = self._client.bucket(self._bucket_name)

        # Generate unique filename
        extension = self._get_extension_from_content_type(content_type)
        filename = f"{folder}/{uuid.uuid4()}{extension}"

        blob = bucket.blob(filename)

        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="PUT",
            content_type=content_type,
            credentials=self._credentials,
        )

        return {
            "upload_url": signed_url,
            "public_url": f"https://storage.googleapis.com/{self._bucket_name}/{filename}",
        }

    def delete_image(self, url: str) -> bool:
        """
        Delete an image from Cloud Storage by its URL.

        Args:
            url: Public URL of the image to delete

        Returns:
            True if deleted successfully, False if not found
        """
        blob_name = self._extract_blob_name_from_url(url)
        if not blob_name:
            return False

        bucket = self._client.bucket(self._bucket_name)
        blob = bucket.blob(blob_name)

        if blob.exists():
            blob.delete()
            return True
        return False

    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Map content type to file extension."""
        mapping = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }
        return mapping.get(content_type, ".jpg")

    def _extract_blob_name_from_url(self, url: str) -> str | None:
        """Extract blob name from a Cloud Storage public URL."""
        # URL format: https://storage.googleapis.com/bucket-name/path/to/file
        prefix = f"https://storage.googleapis.com/{self._bucket_name}/"
        if url.startswith(prefix):
            return url[len(prefix) :]
        return None
