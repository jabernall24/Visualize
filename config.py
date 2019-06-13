import os

S3_BUCKET = os.environ["S3_BUCKET_NAME"]
S3_KEY = os.environ["S3_ACCESS_KEY"]
S3_SECRET = os.environ["S3_SECRET_ACCESS_KEY"]
S3_LOCATION = f'http://{S3_BUCKET}.s3.amazonaws.com/'

SECRET_KEY = os.urandom(32)
DEBUG = True
PORT = 5000
