import hashlib
import hmac
import mimetypes
import os
from datetime import datetime, timezone
from urllib.parse import quote, urlsplit

import requests
from tqdm import tqdm


class R2Client:
    """Minimal Cloudflare R2 PutObject client using AWS Signature Version 4."""

    def __init__(self):
        self.account_id = os.getenv("R2_ACCOUNT_ID")
        self.access_key_id = os.getenv("R2_ACCESS_KEY_ID")
        self.secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("R2_BUCKET_NAME")
        self.endpoint = os.getenv("R2_ENDPOINT")
        self.root_folder_path = os.getenv("R2_BLOG_PREFIX", "archive/blog").strip("/")
        self.session = requests.Session()

    def connect(self):
        if not self.endpoint and self.account_id:
            self.endpoint = f"https://{self.account_id}.r2.cloudflarestorage.com"

        required = [
            self.endpoint,
            self.access_key_id,
            self.secret_access_key,
            self.bucket_name,
        ]
        if not all(required):
            print(
                "[ERROR] Missing R2 configuration. Set R2_ACCOUNT_ID (or "
                "R2_ENDPOINT), R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, and "
                "R2_BUCKET_NAME."
            )
            return False

        parsed = urlsplit(self.endpoint)
        if parsed.scheme != "https" or not parsed.netloc or parsed.path.rstrip("/"):
            print("[ERROR] R2_ENDPOINT must be an HTTPS origin without a path.")
            return False
        self.endpoint = self.endpoint.rstrip("/")
        return True

    @staticmethod
    def _sign(key, message):
        return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()

    def _authorization_headers(self, method, canonical_uri, payload_hash, now):
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")
        host = urlsplit(self.endpoint).netloc
        canonical_headers = (
            f"host:{host}\n"
            f"x-amz-content-sha256:{payload_hash}\n"
            f"x-amz-date:{amz_date}\n"
        )
        signed_headers = "host;x-amz-content-sha256;x-amz-date"
        canonical_request = "\n".join(
            [method, canonical_uri, "", canonical_headers, signed_headers, payload_hash]
        )

        scope = f"{date_stamp}/auto/s3/aws4_request"
        string_to_sign = "\n".join(
            [
                "AWS4-HMAC-SHA256",
                amz_date,
                scope,
                hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
            ]
        )
        date_key = self._sign(
            ("AWS4" + self.secret_access_key).encode("utf-8"), date_stamp
        )
        region_key = self._sign(date_key, "auto")
        service_key = self._sign(region_key, "s3")
        signing_key = self._sign(service_key, "aws4_request")
        signature = hmac.new(
            signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        authorization = (
            f"AWS4-HMAC-SHA256 Credential={self.access_key_id}/{scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )
        return {
            "Authorization": authorization,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amz_date,
        }

    def check_bucket_access(self):
        """Validate credentials and bucket access without changing any objects."""
        if not self.connect():
            return False

        canonical_uri = "/" + quote(self.bucket_name, safe="-_.~")
        payload_hash = hashlib.sha256(b"").hexdigest()
        headers = self._authorization_headers(
            "HEAD", canonical_uri, payload_hash, datetime.now(timezone.utc)
        )

        try:
            response = self.session.head(
                f"{self.endpoint}{canonical_uri}",
                headers=headers,
                timeout=30,
            )
            if response.status_code == 200:
                return True
            tqdm.write(
                f"[ERROR] R2 HeadBucket failed ({response.status_code}). "
                "Check the account, bucket, credentials, and token permissions."
            )
        except Exception as error:
            tqdm.write(f"[ERROR] R2 HeadBucket exception: {error}")
        return False

    def upload_file(self, local_path, remote_subfolder):
        filename = os.path.basename(local_path)
        object_key = "/".join(
            part.strip("/")
            for part in (self.root_folder_path, remote_subfolder, filename)
            if part.strip("/")
        )
        safe = "/-_.~"
        canonical_uri = "/" + quote(
            f"{self.bucket_name}/{object_key}", safe=safe
        )

        try:
            with open(local_path, "rb") as file_handle:
                content = file_handle.read()

            payload_hash = hashlib.sha256(content).hexdigest()
            headers = self._authorization_headers(
                "PUT", canonical_uri, payload_hash, datetime.now(timezone.utc)
            )
            content_type, _ = mimetypes.guess_type(filename)
            if content_type:
                headers["Content-Type"] = content_type

            response = self.session.put(
                f"{self.endpoint}{canonical_uri}",
                headers=headers,
                data=content,
                timeout=60,
            )
            if response.status_code in {200, 201}:
                return True
            tqdm.write(
                f"[ERROR] R2 PutObject failed ({response.status_code}): "
                f"{response.text[:500]}"
            )
        except Exception as error:
            tqdm.write(f"[ERROR] R2 upload exception: {error}")
        return False
