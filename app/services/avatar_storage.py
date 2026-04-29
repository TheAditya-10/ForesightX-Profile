from __future__ import annotations

import re

from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from app.utils.config import ProfileServiceSettings


class AvatarStorageError(RuntimeError):
    """Raised when avatar upload or signed URL generation fails."""


class S3AvatarStorage:
    _EXTENSIONS = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    def __init__(self, settings: ProfileServiceSettings) -> None:
        self.settings = settings

    async def upload_avatar(self, user_id: str, file: UploadFile) -> str:
        content_type = file.content_type or ""
        extension = self._EXTENSIONS.get(content_type)
        if extension is None:
            raise AvatarStorageError("Only JPEG, PNG, and WebP profile photos are supported")

        body = await file.read(self.settings.avatar_max_bytes + 1)
        if len(body) > self.settings.avatar_max_bytes:
            max_mb = self.settings.avatar_max_bytes / (1024 * 1024)
            raise AvatarStorageError(f"Profile photo must be {max_mb:g} MB or smaller")

        object_key = self._object_key(user_id=user_id, extension=extension)

        def put_object() -> None:
            client = self._client()
            client.put_object(
                Bucket=self._bucket_name(),
                Key=object_key,
                Body=body,
                ContentType=content_type,
            )

        await run_in_threadpool(put_object)
        return object_key

    def signed_url(self, object_key: str | None) -> str | None:
        if not object_key:
            return None
        if object_key.startswith(("http://", "https://", "data:image/")):
            return object_key
        if not self.settings.aws_s3_bucket:
            return None
        client = self._client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket_name(), "Key": object_key},
            ExpiresIn=self.settings.aws_s3_signed_url_expires_seconds,
        )

    def _object_key(self, user_id: str, extension: str) -> str:
        safe_user_id = re.sub(r"[^A-Za-z0-9_.-]", "_", user_id)
        prefix = self.settings.aws_s3_avatar_prefix.strip("/")
        return f"{prefix}/{safe_user_id}{extension}" if prefix else f"{safe_user_id}{extension}"

    def _bucket_name(self) -> str:
        if not self.settings.aws_s3_bucket:
            raise AvatarStorageError("AWS_S3_BUCKET is not configured")
        return self.settings.aws_s3_bucket

    def _client(self):
        import boto3

        return boto3.client(
            "s3",
            region_name=self.settings.aws_region,
            endpoint_url=self.settings.aws_s3_endpoint_url or None,
        )
