from dotenv import load_dotenv

from r2_client import R2Client


def main():
    load_dotenv()
    client = R2Client()
    if not client.check_bucket_access():
        return 1

    print("[OK] R2 credentials and bucket access are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
