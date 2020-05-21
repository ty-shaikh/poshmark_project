import boto3
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, './.env'))

ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('AWS_S3_BUCKET')

def upload_file(file, path):
    "Upload single file to S3 bucket"
    S3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS_KEY)

    FILE_NAME = path + file
    OBJECT_NAME = file

    S3.upload_file(FILE_NAME, BUCKET_NAME, OBJECT_NAME)


def list_files(sub_string):
    S3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS_KEY)
    files = []

    for key in S3.list_objects(Bucket=BUCKET_NAME)['Contents']:
        file_name = key['Key']

        if sub_string in file_name:
            files.append(file_name)

    return files


def download_file(file, path):
    "Download single file from S3 bucket"
    S3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS_KEY)

    OBJECT_NAME = file
    FILE_NAME = path + file

    S3.download_file(BUCKET_NAME, OBJECT_NAME, FILE_NAME)
