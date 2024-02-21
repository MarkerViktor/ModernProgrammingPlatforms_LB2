import os
from pathlib import Path

DB_URL = os.environ["DB_URL"]

PASSWORD_HASH_SALT = b"fhasdkjkfjdjnfaosdhj"
PASSWORD_HASH_LENGTH = 128
PASSWORD_HASH_ITERATIONS = 10000

STORAGE_PATH = Path(os.environ["STORAGE_PATH"])
