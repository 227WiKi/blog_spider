import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from blog_resource_urls import (
    build_blog_resource_url,
    encode_blog_resource_path,
    migrate_legacy_blog_resource_url,
    source_filename,
)
from migrate_legacy_blog_urls import migrate_paths, transform_text


class BlogResourceUrlTests(unittest.TestCase):
    def test_builds_public_url_from_relative_path(self):
        self.assertEqual(
            build_blog_resource_url("iko/S__34037763.jpg"),
            "https://res.227wiki.eu.org/archive/blog/iko/S__34037763.jpg",
        )

    def test_migrates_alist_prefix_and_preserves_suffix(self):
        old_url = (
            "https://files.227wiki.eu.org/d/Backup/Blog/minami/"
            "_%E5%8D%97%E3%83%96%E3%83%AD%E3%82%B0%20%282%29.jpg"
            "?download=1#photo"
        )
        self.assertEqual(
            migrate_legacy_blog_resource_url(old_url),
            "https://res.227wiki.eu.org/archive/blog/minami/"
            "_%E5%8D%97%E3%83%96%E3%83%AD%E3%82%B0%20%282%29.jpg"
            "?download=1#photo",
        )

    def test_rejects_non_blog_and_known_malformed_values(self):
        self.assertIsNone(
            migrate_legacy_blog_resource_url(
                "https://files.227wiki.eu.org/d/Backup/Instagram/user/photo.jpg"
            )
        )
        self.assertIsNone(
            migrate_legacy_blog_resource_url(
                "https://files.227wiki.eu.org/d/Backup/Blog/nao/"
                "blog.nanabunnonijyuuni.com"
            )
        )

    def test_source_filename_decodes_only_the_url_path_segment(self):
        self.assertEqual(
            source_filename("https://example.com/%E5%86%99%E7%9C%9F%20(2).jpg?v=1"),
            "写真 (2).jpg",
        )
        self.assertIsNone(source_filename("data:image/gif;base64,AAAA"))

    def test_encodes_original_filename_for_public_url(self):
        self.assertEqual(
            encode_blog_resource_path("iko", "写真 (2).jpg"),
            "iko/%E5%86%99%E7%9C%9F%20%282%29.jpg",
        )

    def test_base_url_can_be_overridden_once(self):
        with patch.dict(os.environ, {"BLOG_RESOURCE_BASE_URL": "https://cdn.test/blog/"}):
            self.assertEqual(
                build_blog_resource_url("iko/file.jpg"),
                "https://cdn.test/blog/iko/file.jpg",
            )


class MigrationTests(unittest.TestCase):
    def test_transform_is_scoped_and_idempotent(self):
        original = "\n".join(
            [
                "https://files.227wiki.eu.org/d/Backup/Blog/iko/file.jpg",
                "https://files.227wiki.eu.org/d/Backup/Instagram/iko/file.jpg",
                "https://res.227wiki.eu.org/archive/blog/iko/already.jpg",
            ]
        )
        migrated, mappings, unrecognized = transform_text(original)
        self.assertIn(
            "https://res.227wiki.eu.org/archive/blog/iko/file.jpg", migrated
        )
        self.assertIn("/d/Backup/Instagram/", migrated)
        self.assertEqual(len(mappings), 1)
        self.assertEqual(unrecognized, [])

        migrated_again, mappings_again, _ = transform_text(migrated)
        self.assertEqual(migrated_again, migrated)
        self.assertEqual(mappings_again, [])

    def test_default_migration_is_dry_run(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "post.md"
            old = "https://files.227wiki.eu.org/d/Backup/Blog/iko/file.jpg"
            path.write_text(old, encoding="utf-8")
            changed, mappings, _ = migrate_paths([path])
            self.assertEqual(changed, [path])
            self.assertEqual(len(mappings), 1)
            self.assertEqual(path.read_text(encoding="utf-8"), old)


if __name__ == "__main__":
    unittest.main()
