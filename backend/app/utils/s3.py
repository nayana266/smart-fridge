import boto3
import os
from botocore.exceptions import ClientError
from typing import Optional

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=os.getenv('AWS_REGION', 'us-east-2')  # Use your region
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'smart-fridge-images-nayana')

def generate_presigned_url(key: str, content_type: str, expiration: int = 3600) -> str:
    """Generate a presigned URL for S3 upload"""
    try:
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        raise e

def get_object_url(key: str) -> str:
    """Get the public URL for an S3 object"""
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"

def delete_object(key: str) -> bool:
    """Delete an object from S3"""
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except ClientError as e:
        print(f"Error deleting object: {e}")
        return False
