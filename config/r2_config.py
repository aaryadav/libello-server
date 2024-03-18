import boto3

from config.settings import *

r2 = boto3.client(
    service_name='s3',
    endpoint_url=settings.r2_endpoint,
    aws_access_key_id=settings.r2_access_id_key,
    aws_secret_access_key=settings.r2_secret_access_key,
    region_name='auto'
)