from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import io
import shutil

import pandas as pd
import pickle as pk
from src.constants import TOKEN_PATH,CREDS_PATH

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
            creds = pk.load(token)
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
            pk.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def download_drive_spreadsheet(csv_path,fileId,service):
    """
    download a spreadsheet as csv file

    Args:
        csv_path(str): path where to store a local version of the spreadsheet (csv)
        fileId (str): id of the file on drive
        service (gdrive service): as returned by get_drive_service
    """

    data = (service.files()
                   .export(fileId=fileId, mimeType='text/csv')
                   .execute()
    )

    # if non-empty file
    if data:
        with open(csv_path, 'wb') as f:
            f.write(data)
        print("Download 100%")
    else:
        raise ValueError("Empty file")

def download_drive_txt(forms_url_path,file_id,service):
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


def download_all_csv_results(results_url,result_path,service):
    """
    Iterate over the forms present in the index and sequentially download
    their respective most recent results

    Args:
        index_url (str):
    """
    results_url = pd.Series(results_url)
    ids = results_url.apply(lambda x:x.split("/")[-2])
    for idx,drive_id in ids.iteritems():
        path = result_path.joinpath(f"{idx}.csv")
        download_drive_spreadsheet(path,drive_id,service)

    em2idx = pk.load(open("../data/processed/emojis_png/all/dic.pk","rb"))
    idx2em = {str(value):key for key,value in em2idx.items()}

    for res_path in result_path.iterdir():
        res_df = (pd.read_csv(res_path)
                    .rename(columns=lambda x: idx2em.get(x,x))
                 )
        res_df.to_csv(res_path,index=False)