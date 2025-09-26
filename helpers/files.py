import os
import aioboto3

async def delete_file(key: str) -> bool:
    if not key:
        print("Key is not available")
        return False
    aws_access_key = os.environ.get("AWS_ACCESS_KEY")
    aws_secret_key = os.environ.get("AWS_SECRET_KEY")
    aws_region = os.environ.get("AWS_REGION")
    bucket_name = os.environ.get("BUCKET_NAME")
    if not all([aws_access_key, aws_secret_key, aws_region, bucket_name]):
        print("AWS credentials or bucket name are missing in environment variables")
        return False
    session = aioboto3.Session()
    try:
        async with session.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        ) as s3_client:
            await s3_client.delete_object(Bucket=bucket_name, Key=key)
            print(f"File {key} deleted successfully")
            return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False
