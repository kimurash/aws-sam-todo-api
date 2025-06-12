import json
import os
import uuid
from typing import Any

import boto3

s3 = boto3.client("s3", region_name="ap-northeast-1")
BUCKET_NAME = os.getenv("BUCKET_NAME")


def generate_upload_url(event: dict, context: Any) -> dict:
    try:
        query_params = event.get("queryStringParameters", {}) or {}
        format = query_params.get("format", "jpg")

        if format not in ["jpg", "png", "gif", "webp"]:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "不正な画像形式です"}),
            }

        file_name = f"{uuid.uuid4()}.{format}"

        content_type = "image/jpeg"
        if format == "png":
            content_type = "image/png"
        elif format == "gif":
            content_type = "image/gif"
        elif format == "webp":
            content_type = "image/webp"

        signed_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_name,
                "ContentType": content_type,
            },
            ExpiresIn=3600,
            HttpMethod="PUT",
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "uploadUrl": signed_url,
                    "fileName": file_name,
                    "contentType": content_type,
                }
            ),
        }

    except Exception as e:
        print(f"Error generating upload URL: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
