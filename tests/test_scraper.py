import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from scraper import BlogScraper


class FakeStorage:
    root_folder_path = "archive/blog"

    def __init__(self):
        self.uploads = []

    def connect(self):
        return True

    def upload_file(self, local_path, remote_subfolder):
        self.uploads.append((Path(local_path), remote_subfolder))
        return True


class ScraperResourceTests(unittest.TestCase):
    def test_download_upload_and_url_generation_use_r2_path(self):
        storage = FakeStorage()
        scraper = BlogScraper(storage_client=storage)
        response = Mock()
        response.raise_for_status = Mock()
        response.iter_content.return_value = [b"image"]
        scraper.session.get = Mock(return_value=response)

        with tempfile.TemporaryDirectory() as directory:
            scraper.updates_dir = directory
            public_url = scraper.handle_image(
                "https://example.com/S__34037763.jpg", "iko"
            )

            self.assertEqual(
                public_url,
                "https://res.227wiki.eu.org/archive/blog/iko/S__34037763.jpg",
            )
            self.assertEqual(storage.uploads[0][1], "iko")
            self.assertEqual(storage.uploads[0][0].name, "S__34037763.jpg")

    def test_non_http_inline_image_is_left_untouched(self):
        scraper = BlogScraper(storage_client=FakeStorage())
        self.assertIsNone(scraper.handle_image("data:image/gif;base64,AAAA", "iko"))


if __name__ == "__main__":
    unittest.main()
