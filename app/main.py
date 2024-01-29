from fastapi import FastAPI, File, UploadFile, HTTPException

app = FastAPI()

# Your Azure Storage Blob related code
import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

storage_connection_string = 'DefaultEndpointsProtocol=https;AccountName=scrapped;AccountKey=ISt/yEooJpXBIKo6cTWzGPbkz3+El4plUodt5AqZPNEkj/0CKQS6Lh/kWiEb7el9NP4U8er2/GSb+AStKek3JQ==;EndpointSuffix=core.windows.net'
blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

container_id = 'valorant'
container_client = blob_service_client.get_container_client(container_id)

def upload_to_azure(file_path, blob_path):
    try:
        blob_obj = blob_service_client.get_blob_client(container=container_id, blob=blob_path)
        with open(file_path, mode='rb') as file_data:
            blob_obj.upload_blob(file_data)
    except ResourceExistsError as e:
        raise HTTPException(status_code=400, detail=f'Blob (file object) {blob_path} already exists.')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list")
async def list_blob():
    container_name = 'valorant'

    # get the container client 
    container_client = blob_service_client.get_container_client(container=container_name)

     # List blobs in the container
    blob_list = [blob.name for blob in container_client.list_blobs()]

    return {"blobs": blob_list}

@app.get("/download-blob")
async def get_blob_data(file_path: str = None):
    if not file_path:
            raise HTTPException(status_code=400, detail="File path is required")
    container_name = 'valorant'
    blob_name = file_path

    # get the container client 
    container_client = blob_service_client.get_container_client(container=container_name)

    data = container_client.download_blob(blob_name).readall().decode("utf-8")

    print(data)
    return {"blob_data": data}

# FastAPI endpoint for file upload
@app.post("/upload-file/")
async def create_upload_file(file: UploadFile = File(...), file_path: str = None):
    try:
        if not file_path:
            raise HTTPException(status_code=400, detail="File path is required")
        
         # Specify the desired blob path within the container
        blob_path = file_path + "/" + file.filename

        # Specify the local file path
        local_file_path = f"/tmp/{file.filename}" 
        
        # Save the uploaded file locally
        with open(local_file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Upload the file to Azure Storage
        upload_to_azure(local_file_path, blob_path)

        return {"filename": file.filename, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
