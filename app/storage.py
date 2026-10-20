import os
from io import BytesIO
from uuid import uuid4

import boto3
from botocore.config import Config
from PIL import Image, UnidentifiedImageError


MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class StorageError(RuntimeError):
    pass


def upload_animal_image(file_storage, farm_id):
    if not file_storage or not file_storage.filename:
        return None, None
    raw = file_storage.read(MAX_IMAGE_BYTES + 1)
    if len(raw) > MAX_IMAGE_BYTES:
        raise StorageError("Cow image must be 5 MB or smaller.")
    if not raw:
        raise StorageError("The selected image is empty.")

    try:
        with Image.open(BytesIO(raw)) as source:
            if source.format not in ALLOWED_FORMATS:
                raise StorageError("Use a JPG, PNG, or WEBP image.")
            source.verify()
        with Image.open(BytesIO(raw)) as source:
            source = source.convert("RGB")
            source.thumbnail((1600, 1600))
            output = BytesIO()
            source.save(output, format="JPEG", quality=86, optimize=True)
            body = output.getvalue()
    except UnidentifiedImageError as exc:
        raise StorageError("The selected file is not a valid image.") from exc

    endpoint = os.getenv("AWS_ENDPOINT_URL_S3", "").strip()
    bucket = os.getenv("STORAGE_BUCKET", "").strip()
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    region = os.getenv("AWS_REGION", "auto").strip()
    public_base = (os.getenv("STORAGE_PUBLIC_BASE_URL") or os.getenv("STORAGE_BASE_URL") or "").strip().rstrip("/")
    if not all((endpoint, bucket, access_key, secret_key, public_base)):
        raise StorageError(
            "Image storage is not configured. Set AWS_ENDPOINT_URL_S3, AWS_ACCESS_KEY_ID, "
            "AWS_SECRET_ACCESS_KEY, STORAGE_BUCKET and STORAGE_PUBLIC_BASE_URL."
        )

    key = f"farms/{farm_id}/animals/{uuid4().hex}.jpg"
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )
    try:
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType="image/jpeg",
            CacheControl="public, max-age=31536000, immutable",
        )
    except Exception as exc:
        raise StorageError("Could not upload the cow image to object storage.") from exc

    # STORAGE_PUBLIC_BASE_URL should be the public root URL, optionally ending in the bucket name.
    prefix = public_base if public_base.endswith("/" + bucket) else f"{public_base}/{bucket}"
    return f"{prefix}/{key}", key
