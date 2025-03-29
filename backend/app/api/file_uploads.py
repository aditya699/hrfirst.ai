'''NOTE:FOR @app.post("/upload-files/")

1.@app.post("/upload-files/") is the endpoint for uploading files

2. ... means required fields.

3.File uploads are sent using multipart/form-data so other fields also need to be sent in the form format.

4.Frontend must send the data as multipart/form-data
'''



from fastapi import APIRouter, File, UploadFile, Form
from typing import List
from azure.storage.blob import BlobServiceClient #type: ignore
from dotenv import load_dotenv
import os

load_dotenv()

CONNECTION_STRING=os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME="hr-first"

blob_service_client=BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client=blob_service_client.get_container_client(CONTAINER_NAME)

app = APIRouter()

@app.post("/upload-files/")
async def upload_files(
    files: List[UploadFile] = File(...),  # Lists of files will be sent from frontend
    session_cookie: str = Form(...),  # session cookie(after the auth) 
):
    """
    This function is used to upload files to the server.

    The frontend will send the files(as a multipart/form-data) and the session cookie.
    """
    #from the session cookie, we will get the user_id and user_email(for now since auth is not implemented let it be like this)

    user_id="123"   #this would come after decoding the session cookie
    user_email="test@test.com"  #this would come after decoding the session cookie
   
    #push data to container with user_id as the folder name
    user_folder_name=f"{user_id}"

    # Error handling for file uploads
    try:
        # Upload the files to the container
        for file in files:
            # Create blob path with user folder prefix
            blob_path = f"{user_folder_name}/{file.filename}"
            blob_client = container_client.get_blob_client(blob_path)
            
            # Read file content
            file_content = await file.read()
            
            # Upload the file content
            blob_client.upload_blob(file_content, overwrite=True)
    
    except Exception as e:
        return {"error": str(e)}  # Return error message

    return {"message": "Files uploaded successfully"}
