import boto3
import os
import subprocess
import shutil
import datetime


def lambda_handler(event, context):

    target_bucket = os.environ['TARGET_BUCKET']

    PIP_TARGET_DIR = '/tmp/pip_packages'
    ARCHIVE_BASE_NAME = '/tmp/packages'
    ARCHIVE_TYPE = 'zip'

    pip_result = subprocess.run(['pip3', 'install', '-r', 'requirements.txt', '--disable-pip-version-check', '--no-cache-dir', '--target', PIP_TARGET_DIR],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if pip_result.returncode != 0:
        return {
            'message': 'Problem running pip',
            'pip_stdout': pip_result.stdout,
            'pip_stderr': pip_result.stderr,
        }

    shutil.copy('requirements.txt', PIP_TARGET_DIR + '/requirements.txt')  # include requirements.txt in the zip file

    shutil.make_archive(ARCHIVE_BASE_NAME, ARCHIVE_TYPE, PIP_TARGET_DIR)

    archive_file_name = ARCHIVE_BASE_NAME + '.' + ARCHIVE_TYPE


    # TODO - include requirements.txt in zip file

    s3_object_key = 'packages-' + datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + '.' + ARCHIVE_TYPE

    client = boto3.client('s3')
    client.put_object(Body=open(archive_file_name, 'rb'), Bucket=target_bucket, Key=s3_object_key)

    presignedUrl = client.generate_presigned_url(
        ClientMethod='get_object',
        ExpiresIn=3600,
        Params={
            'Bucket': target_bucket,
            'Key': s3_object_key
        }
    )

    return {
        'message': 'Your pip packages have been build, the zip is temporarily available for download',
        'download_url': presignedUrl
    }


# print (lambda_handler(True, True))
