"""
Pluggable file storage service.

Set STORAGE_BACKEND=s3 (plus AWS_S3_BUCKET, AWS_S3_REGION, AWS_ACCESS_KEY_ID,
AWS_SECRET_ACCESS_KEY) to use S3.  Defaults to local disk under FILE_STORAGE_PATH.

Usage:
    from utils.storage_service import storage
    path_or_key = storage.put_file(project_id, evidence_id, data, content_type)
    url          = storage.get_url(project_id, evidence_id)
"""

import os
from pathlib import Path
from typing import Optional

_BACKEND       = os.environ.get("STORAGE_BACKEND", "local")
_LOCAL_BASE    = Path(os.environ.get("FILE_STORAGE_PATH", "uploads"))
_S3_BUCKET     = os.environ.get("AWS_S3_BUCKET", "")
_S3_REGION     = os.environ.get("AWS_S3_REGION", "us-east-1")
_PRESIGN_TTL   = 3600  # seconds


class StorageService:
    # ── Public interface ────────────────────────────────────────────────────

    def put_file(
        self,
        project_id: str,
        evidence_id: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Store a file. Returns a storage key / local path for later retrieval."""
        key = f"{project_id}/{evidence_id}"
        if _BACKEND == "s3" and _S3_BUCKET:
            return self._put_s3(key, data, content_type)
        return self._put_local(key, data)

    def get_url(self, project_id: str, evidence_id: str) -> Optional[str]:
        """Return a URL (pre-signed S3 URL or local path) for accessing the file."""
        key = f"{project_id}/{evidence_id}"
        if _BACKEND == "s3" and _S3_BUCKET:
            return self._get_s3_url(key)
        return self._get_local_path(key)

    def delete_file(self, project_id: str, evidence_id: str) -> bool:
        """Delete a stored file. Returns True on success."""
        key = f"{project_id}/{evidence_id}"
        if _BACKEND == "s3" and _S3_BUCKET:
            return self._delete_s3(key)
        return self._delete_local(key)

    # ── Local filesystem backend ────────────────────────────────────────────

    def _put_local(self, key: str, data: bytes) -> str:
        dest = _LOCAL_BASE / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return str(dest)

    def _get_local_path(self, key: str) -> Optional[str]:
        p = _LOCAL_BASE / key
        return str(p) if p.exists() else None

    def _delete_local(self, key: str) -> bool:
        p = _LOCAL_BASE / key
        if p.exists():
            p.unlink()
            return True
        return False

    # ── S3 backend ──────────────────────────────────────────────────────────

    def _put_s3(self, key: str, data: bytes, content_type: str) -> str:
        import boto3  # noqa: PLC0415  # type: ignore[import-untyped]
        client = boto3.client("s3", region_name=_S3_REGION)
        client.put_object(
            Bucket=_S3_BUCKET,
            Key=key,
            Body=data,
            ContentType=content_type,
            ServerSideEncryption="AES256",
        )
        return f"s3://{_S3_BUCKET}/{key}"

    def _get_s3_url(self, key: str) -> str:
        import boto3  # noqa: PLC0415  # type: ignore[import-untyped]
        client = boto3.client("s3", region_name=_S3_REGION)
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": _S3_BUCKET, "Key": key},
            ExpiresIn=_PRESIGN_TTL,
        )

    def _delete_s3(self, key: str) -> bool:
        import boto3  # noqa: PLC0415  # type: ignore[import-untyped]
        client = boto3.client("s3", region_name=_S3_REGION)
        client.delete_object(Bucket=_S3_BUCKET, Key=key)
        return True


# Module-level singleton
storage = StorageService()
