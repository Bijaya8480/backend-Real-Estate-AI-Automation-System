from backend.main import app

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

