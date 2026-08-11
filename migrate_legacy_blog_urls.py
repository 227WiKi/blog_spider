#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

from blog_resource_urls import migrate_legacy_blog_resource_url


LEGACY_URL_PATTERN = re.compile(
    r"https?://files\.227wiki\.eu\.org/d/Backup/Blog/[^\s\"'<>\)\]]+",
    re.IGNORECASE,
)
TEXT_SUFFIXES = {
    ".html",
    ".htm",
    ".json",
    ".md",
    ".yaml",
    ".yml",
}


def transform_text(text):
    mappings = []
    unrecognized = []

    def replace(match):
        old_url = match.group(0)
        new_url = migrate_legacy_blog_resource_url(old_url)
        if new_url is None:
            unrecognized.append(old_url)
            return old_url
        mappings.append((old_url, new_url))
        return new_url

    return LEGACY_URL_PATTERN.sub(replace, text), mappings, unrecognized


def iter_files(paths):
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_file():
            yield path
            continue
        if not path.exists():
            raise FileNotFoundError(path)
        for candidate in sorted(path.rglob("*")):
            if (
                candidate.is_file()
                and candidate.suffix.lower() in TEXT_SUFFIXES
                and ".git" not in candidate.parts
                and "node_modules" not in candidate.parts
            ):
                yield candidate


def migrate_paths(paths, write=False):
    all_mappings = []
    all_unrecognized = []
    changed_files = []

    for path in iter_files(paths):
        original = path.read_text(encoding="utf-8")
        migrated, mappings, unrecognized = transform_text(original)
        all_mappings.extend((path, old, new) for old, new in mappings)
        all_unrecognized.extend((path, url) for url in unrecognized)
        if migrated != original:
            changed_files.append(path)
            if write:
                path.write_text(migrated, encoding="utf-8")

    return changed_files, all_mappings, all_unrecognized


def main():
    parser = argparse.ArgumentParser(
        description="Migrate recognized AList blog URLs to Cloudflare R2."
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to scan")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply changes (the default is a dry-run)",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Print every mapping instead of the first 50 unique mappings",
    )
    args = parser.parse_args()

    changed_files, mappings, unrecognized = migrate_paths(args.paths, args.write)
    unique_mappings = list(dict.fromkeys((old, new) for _, old, new in mappings))
    display_limit = len(unique_mappings) if args.show_all else 50

    print("Mode:", "WRITE" if args.write else "DRY-RUN (no files changed)")
    for old, new in unique_mappings[:display_limit]:
        print(f"{old} -> {new}")
    if len(unique_mappings) > display_limit:
        print(
            f"... {len(unique_mappings) - display_limit} more unique mappings; "
            "use --show-all to display them."
        )

    print(f"Matched URL occurrences: {len(mappings)}")
    print(f"Unique recognized URLs: {len(unique_mappings)}")
    print(f"Files that {'changed' if args.write else 'would change'}: {len(changed_files)}")

    if unrecognized:
        print("Unrecognized legacy blog URLs (left unchanged):")
        for path, url in dict.fromkeys(unrecognized):
            print(f"  {path}: {url}")
        print(f"Unrecognized occurrences: {len(unrecognized)}")


if __name__ == "__main__":
    main()
