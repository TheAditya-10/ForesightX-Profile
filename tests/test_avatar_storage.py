from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from app.services.avatar_storage import AvatarStorageError, S3AvatarStorage
from app.utils.config import ProfileServiceSettings


def test_object_key_sanitizes_user_id_and_prefix() -> None:
    settings = ProfileServiceSettings(aws_s3_avatar_prefix="/avatars/")
    storage = S3AvatarStorage(settings)
    key = storage._object_key(user_id="user@id/..", extension=".png")
    assert key.startswith("avatars/")
    assert key.endswith(".png")
    assert "@" not in key
    assert "/.." not in key


def test_signed_url_passthrough_and_missing_bucket() -> None:
    settings = ProfileServiceSettings(aws_s3_bucket=None)
    storage = S3AvatarStorage(settings)
    assert storage.signed_url(None) is None
    assert storage.signed_url("https://example.com/a.png") == "https://example.com/a.png"
    assert storage.signed_url("avatars/u.png") is None


def test_upload_avatar_rejects_unsupported_content_type() -> None:
    async def _run() -> None:
        settings = ProfileServiceSettings(aws_s3_bucket="bucket")
        storage = S3AvatarStorage(settings)
        file = SimpleNamespace(content_type="application/pdf")
        file.read = lambda n: b"x"  # type: ignore[assignment]
        with pytest.raises(AvatarStorageError, match="Only JPEG"):
            await storage.upload_avatar("user-1", file)  # type: ignore[arg-type]

    asyncio.run(_run())


def test_upload_avatar_rejects_files_over_max_bytes() -> None:
    async def _run() -> None:
        settings = ProfileServiceSettings(aws_s3_bucket="bucket", avatar_max_bytes=3)

        class _NoopStorage(S3AvatarStorage):
            def _client(self):
                class _Client:
                    def put_object(self, **kwargs):  # noqa: ANN003
                        return None

                return _Client()

        storage = _NoopStorage(settings)

        file = SimpleNamespace(content_type="image/png")

        async def _read(n):  # noqa: ANN001
            return b"abcd"

        file.read = _read
        with pytest.raises(AvatarStorageError, match="smaller"):
            await storage.upload_avatar("user-1", file)  # type: ignore[arg-type]

    asyncio.run(_run())
