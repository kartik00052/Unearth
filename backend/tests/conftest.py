"""Test configuration.

The application's secret-bearing settings have no defaults so production fails
fast when they are missing. Tests inject safe placeholders here, before any
application module imports the settings, so the suite can run without a local
``.env`` file. These values are never used to reach a real service.
"""

import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://unearth:unearth@localhost:5432/unearth")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "test-access-key")
os.environ.setdefault("MINIO_SECRET_KEY", "test-secret-key")
os.environ.setdefault("MINIO_BUCKET", "unearth-test")
