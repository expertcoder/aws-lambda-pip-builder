import boto3
import os
import subprocess
import shutil
import datetime
import json
import traceback
import sys

def _get_response_data(status_code, response_body_data):
    if status_code < 200 or status_code > 600:
        raise Exception('invalid status code')


    return {
        "statusCode": status_code,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        },
        "body": json.dumps(response_body_data)
    }

def _get_exception_data(e):
    return {
        "message": str(e),
        "type": type(e).__name__,
        "args": e.args,
        "traceback": traceback.format_exc()
    }

def _build_pip():
    # TODO requirements.txt should come from POST parameters

    target_bucket = os.environ['TARGET_BUCKET']

    PIP_TARGET_DIR = '/tmp/pip_packages'
    ARCHIVE_BASE_NAME = '/tmp/packages'
    ARCHIVE_TYPE = 'zip'

    pip_result = subprocess.run(
        ['pip3', 'install', '-r', 'requirements.txt', '--disable-pip-version-check', '--no-cache-dir', '--target',
         PIP_TARGET_DIR],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if pip_result.returncode != 0:
        response_body_data = {
            'message': 'Problem running pip',
            'pip_stdout': pip_result.stdout.decode("utf-8"),
            'pip_stderr': pip_result.stderr.decode("utf-8"),
        }

        return _get_response_data(400, response_body_data)


    shutil.copy('requirements.txt', PIP_TARGET_DIR + '/requirements.txt')  # include requirements.txt in the zip file

    shutil.make_archive(ARCHIVE_BASE_NAME, ARCHIVE_TYPE, PIP_TARGET_DIR)

    archive_file_name = ARCHIVE_BASE_NAME + '.' + ARCHIVE_TYPE

    s3_object_key = 'packages-' + datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + '.' + ARCHIVE_TYPE

    client = boto3.client('s3')
    client.put_object(Body=open(archive_file_name, 'rb'), Bucket=target_bucket, Key=s3_object_key)

    presigned_url = client.generate_presigned_url(
        ClientMethod='get_object',
        ExpiresIn=3600,
        Params={
            'Bucket': target_bucket,
            'Key': s3_object_key
        }
    )


    response_body_data = {
        'message': 'Your pip packages have been build, the zip is temporarily available for download',
        'presigned_url': presigned_url
    }

    return _get_response_data(200, response_body_data)

def build_pip_handler(event, context):
    try:
        return _build_pip()
    except Exception as e:
        return _get_response_data(400, {"message": str(e), "exception": _get_exception_data(e)})

