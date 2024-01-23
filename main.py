from fastapi import FastAPI, File, UploadFile, HTTPException

app = FastAPI()

# Your Azure Storage Blob related code
import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

storage_connection_string = 'connection_String'
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

# FastAPI endpoint for file upload
@app.post("/upload-file/")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        # Specify the desired blob path within the container
        blob_path = "groupA_valorant/" + file.filename

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
