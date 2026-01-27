from azure.storage.blob import BlobServiceClient,  __version__
from io import BytesIO
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError 
from databricks.sdk import WorkspaceClient
from lib.setting import SETTINGS
import os


def main_upload(env):

    rootpath = SETTINGS[env]['path'] 
    volume_path = SETTINGS[env]['volume_path']

    client = WorkspaceClient(
        host= SETTINGS[env]['host'],
        client_id=SETTINGS[env]['client_id'],
        client_secret=SETTINGS[env]['client_secret']
    )

    current_directory = os.path.normpath(os.getcwd() + rootpath)
    print(f"Local directory: {current_directory}")

    files = os.listdir(current_directory)
    files = [
        f for f in files
        if os.path.isfile(os.path.join(current_directory, f))
    ]

    for f in files:
        local_file_path = os.path.join(current_directory, f)
        remote_file_path = f"{volume_path.rstrip('/')}/{f}"

        try:
            print(f"Uploading {f} → {remote_file_path}")
            with open(local_file_path, "rb") as data:
                client.files.upload(
                    remote_file_path,
                    data,
                    overwrite=True
                )
            print(f"Uploaded {f} successfully")
        except Exception as e:
            print(f"Failed to upload {f}: {e}")
