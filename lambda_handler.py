"""AWS Lambda handler for the FastAPI app.

This module must import safely in multiple environments (Docker/Render, local, serverless).
In some runtimes, Python may import this file as a script (no parent package), so
relative imports like `from .main import app` will fail.

We therefore: 
1) Try absolute import: `from backend.main import app`
2) If that fails, try importing `main` from the same directory as a last resort.
"""

from __future__ import annotations

# Import app with fallbacks to handle environments where `backend` package resolution fails.
try:
    from backend.main import app  # type: ignore
except ImportError:  # pragma: no cover
    # If this file is executed/loaded without a known parent package, relative imports fail.
    # Import `main.py` that lives next to this file.
    from importlib import import_module

    _main = import_module("main")
    app = _main.app


# NOTE: Keep this handler import-light for serverless bundling.
# Avoid hard dependency failures at import time.
try:
    from mangum import Mangum

    lambda_handler = Mangum(app)
except Exception:  # pragma: no cover
    lambda_handler = None


def handler(event, context):
    if lambda_handler is None:
        # Fail with a clear message instead of crashing import-time.
        return {
            "statusCode": 500,
            "body": "Mangum is not available in this deployment bundle.",
        }
    return lambda_handler(event, context)


# Test local
if __name__ == "__main__":
    print("Lambda handler ready - 7MB bundle")
    print("Upload lambda.zip to AWS Lambda")

