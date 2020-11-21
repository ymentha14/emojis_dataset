"""
Script to automate the creation of MTURK task: this assumes you did run the app script
generating the forms and their associate file previously.
"""
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from src.constants import TOKEN_PATH,CREDS_PATH, FORMS_URLS_PATH, AWS_KEYS_PATH
from src.utils import read_access_keys
from google.auth.transport.requests import Request
import io
import boto3
import shutil
import pandas as pd
from googleapiclient.http import MediaIoBaseDownload

def get_drive_service():
    """
    Return the drive service for files downloading
    """
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def download_forms_urls(forms_url_path,file_id,service):
    """
    Download the forms_url file to the provided path

    Args:
        forms_url_path (str): path where to store a local version of the forms urls
        file_id (str): gdrive id of the urls file
        service (gdrive service): as returned by get_drive_service
    """
    request = service.files().export(fileId=file_id, mimeType='text/plain')

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%" % int(status.progress() * 100))

    # The file has been downloaded into RAM, now save it in a file
    fh.seek(0)
    with open(forms_url_path, 'wb') as f:
        shutil.copyfileobj(fh, f, length=131072)

def create_mturk_client(aws_access_key_id,aws_secret_access_key,production=False):
    """
    Return an MTURK client

    Args:
        aws_access_key_id (str): aws key
        aws_secret_access_key (str): secret aws key
        production (Bool): sandbox if set to false

    Returns:
        client (boto3.client)
    """
    create_hits_in_production = False
    environments = {
            "production": {
                "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
                "preview": "https://www.mturk.com/mturk/preview"
            },
            "sandbox": {
                "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
                "preview": "https://workersandbox.mturk.com/mturk/preview"
            },
    }
    mturk_environment = environments["production"] if create_hits_in_production else environments["sandbox"]

    client = boto3.client(
       'mturk',
       aws_access_key_id = aws_access_key_id,
       aws_secret_access_key = aws_secret_access_key,
       region_name='us-east-1',
       endpoint_url = mturk_environment['endpoint'],
    )
    return client

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--id',
        help="gdrive id of the urls file",
        default='11UjUJ9WfafdMEXZww9Q9GBnXsqX0dPWPdZGXGfFr_t4',
        type=str
    )
    parser.add_argument(
        '--hittype',
        help="HITTypeId of the MTurk HIT",
        type=str,
        required=True
    )
    parser.add_argument(
        '--hitlayout',
        help="HITLayoutID of the MTurk HIT",
        type=str,
        required=True
    )

    args = parser.parse_args()
    file_id = args.id
    hittypeid = args.hittype
    hitlayout = args.hitlayout

    # (1). Retrieve the urls from the app script

    # retrieve gdrive service
    service = get_drive_service()

    # download the most recent forms_urls
    download_forms_urls(FORMS_URLS_PATH,file_id,service)
    forms_url = pd.read_csv(FORMS_URLS_PATH,sep=r"\s+",header=None,names=['url'],index_col=0)

    # (2). Link to AWS Mturk

    # retrieval of the access keys
    aws_access_key_id,aws_secret_access_key = read_access_keys(AWS_KEYS_PATH)

    # creation of an mturk client
    client = create_mturk_client(aws_access_key_id,aws_secret_access_key)
    myhit = client.create_hit_with_hit_type(
                HITTypeId=hittypeid,
                HITLayoutId=hitlayout,
                HITLayoutParameters = [{'Name':'url',
                           'Value':'https://forms.gle/XKVGkivEhe2JwuEW7'}],
                LifetimeInSeconds = 3600,
                )



