from azure.storage.blob import BlobServiceClient,  __version__
from io import BytesIO
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError 
from lib.setting import SETTINGS
import os

def main_upload(env, name, container):
    setting = SETTINGS
    key = setting[env][name]['key']
    rootpath = setting[env][name]['path']
    try:   
        # path = get_path_from_config()
        sas_url = key

        blob_service_client = BlobServiceClient(account_url=sas_url)

        # Use the correct container name instead of `path`
        print('----------- start upload measurement file -----------')
        container_name = setting[env][name][container]
        print(f"Container name: {container_name}")
        container_client = blob_service_client.get_container_client(container_name)

        print(os.getcwd())
        print(rootpath)
        current_directory = os.getcwd()+ rootpath
        print(current_directory)
        files = os.listdir(current_directory) 
        files = [f for f in files if os.path.isfile(os.path.join(current_directory, f))]

        for f in files:
            file_name = f"{f}" 
            path_des = os.path.normpath(os.path.join(current_directory, f)) 
            blob_client = container_client.get_blob_client(file_name)
            with open(path_des, "rb") as data:
                blob_client.upload_blob(data, overwrite=True) 
            print(f"Uploaded {f} to {container_name} successfully")

            # os.remove(path_des)

    except Exception as e:
        print(e)


def batch_upload(env, name, container):
    setting = SETTINGS
    key = setting[env][name]['key']
    rootpath = setting[env][name]['path_batch']
    try:   
        sas_url = key

        blob_service_client = BlobServiceClient(account_url=sas_url)

        # Use the correct container name instead of `path`
        print('----------- start upload measurement file -----------')
        container_name = setting[env][name][container]
        print(f"Container name: {container_name}")
        container_client = blob_service_client.get_container_client(container_name)

        print(os.getcwd())
        print(rootpath)
        current_directory = os.getcwd()+ rootpath
        print(current_directory)
        files = os.listdir(current_directory) 
        files = [f for f in files if os.path.isfile(os.path.join(current_directory, f))]

        for f in files:
            file_name = f"{f}" 
            path_des = os.path.normpath(os.path.join(current_directory, f)) 
            blob_client = container_client.get_blob_client(file_name)
            with open(path_des, "rb") as data:
                blob_client.upload_blob(data, overwrite=True) 
            print(f"Uploaded {f} to {container_name} successfully")

    except Exception as e:
        print(e)
    