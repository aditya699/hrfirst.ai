'''
NOTE:
FOR @app.post("/upload-files/")
1.@app.post("/upload-files/") is the endpoint for uploading files

2.Since we are using UploadFile, we need to use Form to get the file type, user_id, user_email

3. ... means required fields.

4.File uploads are sent using multipart/form-data so other fields also need to be sent in the form format.

5.Frontend must send the data as multipart/form-data


'''


from fastapi import FastAPI,File,UploadFile,Form
from typing import List

app=FastAPI()

@app.post("/upload-files/")
async def upload_files(
    files:List[UploadFile]=File(...),  #Lists of files will be sent from frontend
    session_cookie:str=Form(...),  #session cookie(after the auth) 
):
    """
    This function is used to upload files to the server.

    The frontend will send the files(as a multipart/form-data) and the session cookie.
    """
    
    master_dict={}

    #Reading the files and storing in master_dict
    for file in files:
        #Read the file content
        content=await file.read()
        #get the content type
        content_type=file.content_type
        #decoding the content to string
        content=content.decode(errors="ignore")



    return {"message":"Files uploaded successfully"}


            












