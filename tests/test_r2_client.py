import hashlib
import os
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from r2_client import R2Client


class R2ClientTests(unittest.TestCase):
    def configured_client(self):
        environment = {
            "R2_ACCOUNT_ID": "account",
            "R2_ACCESS_KEY_ID": "access",
            "R2_SECRET_ACCESS_KEY": "secret",
            "R2_BUCKET_NAME": "bucket",
        }
        with patch.dict(os.environ, environment, clear=True):
            client = R2Client()
        self.assertTrue(client.connect())
        return client

    def test_signature_contains_r2_scope(self):
        client = self.configured_client()
        payload_hash = hashlib.sha256(b"test").hexdigest()
        headers = client._authorization_headers(
            "PUT",
            "/bucket/archive/blog/iko/file.jpg",
            payload_hash,
            datetime(2026, 8, 12, tzinfo=timezone.utc),
        )
        self.assertIn("/20260812/auto/s3/aws4_request", headers["Authorization"])
        self.assertEqual(headers["x-amz-date"], "20260812T000000Z")

    def test_bucket_check_uses_read_only_head_request(self):
        client = self.configured_client()
        response = Mock(status_code=200)
        client.session.head = Mock(return_value=response)

        self.assertTrue(client.check_bucket_access())

        requested_url = client.session.head.call_args.args[0]
        request_options = client.session.head.call_args.kwargs
        self.assertEqual(requested_url, "https://account.r2.cloudflarestorage.com/bucket")
        self.assertIn("Authorization", request_options["headers"])
        self.assertEqual(request_options["timeout"], 30)

    def test_bucket_check_reports_rejected_credentials(self):
        client = self.configured_client()
        client.session.head = Mock(return_value=Mock(status_code=403))

        with patch("r2_client.tqdm.write") as log:
            self.assertFalse(client.check_bucket_access())
        log.assert_called_once()

    def test_upload_uses_archive_blog_object_key(self):
        client = self.configured_client()
        response = Mock(status_code=200, text="")
        client.session.put = Mock(return_value=response)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as local_file:
            local_file.write(b"image")
            local_file.flush()
            self.assertTrue(client.upload_file(local_file.name, "iko"))

        requested_url = client.session.put.call_args.args[0]
        self.assertIn("/bucket/archive/blog/iko/", requested_url)
        self.assertNotIn("/Backup/Blog/", requested_url)


if __name__ == "__main__":
    unittest.main()
