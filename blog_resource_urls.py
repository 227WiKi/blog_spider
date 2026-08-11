import os
from urllib.parse import quote, unquote, urlsplit


DEFAULT_BLOG_RESOURCE_BASE_URL = "https://res.227wiki.eu.org/archive/blog"
LEGACY_BLOG_RESOURCE_HOST = "files.227wiki.eu.org"
LEGACY_BLOG_RESOURCE_PREFIX = "/d/Backup/Blog/"

_RESERVED_FIRST_SEGMENTS = {"archive", "backup", "blog", "d"}
_KNOWN_BROKEN_FILENAMES = {"blog.nanabunnonijyuuni.com"}


def blog_resource_base_url():
    return os.getenv(
        "BLOG_RESOURCE_BASE_URL", DEFAULT_BLOG_RESOURCE_BASE_URL
    ).rstrip("/")


def _validate_relative_path(relative_path):
    if not relative_path or relative_path.startswith("/"):
        return False

    parts = relative_path.split("/")
    if len(parts) < 2 or any(part in {"", ".", ".."} for part in parts):
        return False
    if parts[0].lower() in _RESERVED_FIRST_SEGMENTS:
        return False

    filename = parts[-1]
    if filename in _KNOWN_BROKEN_FILENAMES or ";base64," in filename:
        return False
    return True


def build_blog_resource_url(relative_path, base_url=None):
    """Build a public blog resource URL without decoding or normalizing its path."""
    parsed = urlsplit(relative_path)
    if parsed.scheme or parsed.netloc or not _validate_relative_path(parsed.path):
        raise ValueError(f"Invalid blog resource relative path: {relative_path}")

    result = f"{(base_url or blog_resource_base_url()).rstrip('/')}/{parsed.path}"
    if parsed.query:
        result += f"?{parsed.query}"
    if parsed.fragment:
        result += f"#{parsed.fragment}"
    return result


def encode_blog_resource_path(author, filename):
    """Encode source names for a URL while leaving their spelling and case intact."""
    if not author or not filename or "/" in author or "/" in filename:
        raise ValueError("Author and filename must each be a single path segment")
    safe = "-._~"
    return f"{quote(author, safe=safe)}/{quote(filename, safe=safe)}"


def source_filename(url):
    """Return the original filename represented by an HTTP(S) source URL."""
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    encoded_name = parsed.path.rsplit("/", 1)[-1]
    if not encoded_name:
        return None
    filename = unquote(encoded_name)
    if filename in {".", ".."} or "/" in filename or "\x00" in filename:
        return None
    return filename


def extract_legacy_blog_relative_path(url):
    """Extract only the real blog-relative path from a recognized AList URL."""
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    if (parsed.hostname or "").lower() != LEGACY_BLOG_RESOURCE_HOST:
        return None
    if not parsed.path.startswith(LEGACY_BLOG_RESOURCE_PREFIX):
        return None

    relative_path = parsed.path[len(LEGACY_BLOG_RESOURCE_PREFIX):]
    if not _validate_relative_path(relative_path):
        return None
    return relative_path


def migrate_legacy_blog_resource_url(url, base_url=None):
    """Map a recognized legacy AList blog URL to R2, preserving query/fragment."""
    parsed = urlsplit(url)
    relative_path = extract_legacy_blog_relative_path(url)
    if relative_path is None:
        return None

    migrated = build_blog_resource_url(relative_path, base_url=base_url)
    if parsed.query:
        migrated += f"?{parsed.query}"
    if parsed.fragment:
        migrated += f"#{parsed.fragment}"
    return migrated
