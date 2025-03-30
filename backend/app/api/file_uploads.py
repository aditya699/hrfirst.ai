'''NOTE:FOR @app.post("/upload-files/")

1.@app.post("/upload-files/") is the endpoint for uploading files

2. ... means required fields.

3.File uploads are sent using multipart/form-data so other fields also need to be sent in the form format.

4.Frontend must send the data as multipart/form-data

Thoughts on extracting text from files:

1.for cv's we can use langchain or anyother pdf parser to extract text from cv.

2.For chat with data systems , we need a stronger ocr tool since we will be extracting text from images and pdfs.
'''



from datetime import datetime
from fastapi import APIRouter, File, UploadFile, Form
from typing import List
from azure.storage.blob import BlobServiceClient #type: ignore
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
import os
from app.database.get_client import get_client
from langchain_openai import ChatOpenAI
from app.schemas.file_uploads import CVUserData
from app.prompts.prompts import CV_DATA_PROMPT

load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
CONNECTION_STRING=os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME="hr-first"

blob_service_client=BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client=blob_service_client.get_container_client(CONTAINER_NAME)

app = APIRouter()
llm=ChatOpenAI(model="gpt-4o-mini",temperature=0)
structured_llm=llm.with_structured_output(CVUserData)
@app.post("/upload-files-process/")
async def upload_files(
    files: List[UploadFile] = File(...),  # Lists of files will be sent from frontend
    session_cookie: str = Form(...),  # session cookie(after the auth) 
):
    """
    This function is used to upload files to the server and process them.

    The frontend will send the files(as a multipart/form-data) and the session cookie.
    """
    #from the session cookie, we will get the user_id and user_email(for now since auth is not implemented let it be like this)

    user_id="123"   #this would come after decoding the session cookie
    user_email="test@test.com"  #this would come after decoding the session cookie
   
    #push data to container with user_id as the folder name
    user_folder_name=f"{user_id}"

    file_counter=0
    correct_files=0
    incorrect_files=file_counter-correct_files

    frontend_response={}
    
    
    # Error handling for file uploads
    try:
        # Upload the files to the container
        for file in files:
            file_counter+=1
            # Create blob path with user folder prefix
            blob_path = f"{user_folder_name}/{file.filename}"
            blob_client = container_client.get_blob_client(blob_path)
            
            # Read file content
            file_content = await file.read()
            
            # Upload the file content
            blob_client.upload_blob(file_content, overwrite=True)

            if file.content_type=="application/pdf":

                # Save file temporarily to process with PyPDFLoader
                temp_file_path = f"temp_{file.filename}"
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(file_content)
                
                # Extract text from PDF
                loader = PyPDFLoader(temp_file_path)
                pages = []
                text_content = ""
                try:
                    for page in loader.load():
                        pages.append(page)
                        text_content += page.page_content + "\n"

                    try:
                        response = await structured_llm.ainvoke(CV_DATA_PROMPT.format(cv_data=text_content))
                    except Exception as e:
                        response = CVUserData(
                            name="Not Found",
                            email="Not Found",
                            phone="Not Found",
                            address="Not Found",
                            education="Not Found",
                            experience="Not Found",
                            skills="Not Found"
                        )
                    
                    # Convert the Pydantic model to a dictionary to avoid MongoDB serialization issues
                    response_dict = {
                        "name": response.name,
                        "email": response.email,
                        "phone": response.phone,
                        "address": response.address,
                        "education": response.education,
                        "experience": response.experience,
                        "skills": response.skills
                    }

                    frontend_response[file.filename]=response_dict
                    
                    metadata_dict={
                        "file_name": file.filename,
                        "file_size": len(file_content),
                        "file_type": file.content_type,
                        "file_url": blob_client.url,
                        "extracted_text": text_content,
                        "user_id": user_id,
                        "user_email": user_email,
                        "uploaded_at": datetime.now(),
                        "extracted_data": response_dict,  # Store as dictionary instead of Pydantic model
                        "name": response.name,
                        "email": response.email,
                        "phone": response.phone,
                        "address": response.address,
                        "education": response.education,
                        "experience": response.experience,
                        "skills": response.skills
                    }

                    #push metadata to mongodb
                    client=await get_client()
                    if client:
                        db=client["hr-first"]
                        collection=db["cv-data"]
                        await collection.insert_one(metadata_dict)

                    correct_files+=1

                except Exception as e:
                    print("Error in processing file: ",e)
                    error_dict={
                        "file_name": file.filename,
                        "error": str(e)
                    }
                    client=await get_client()
                    if client:
                        db=client["hr-first"]
                        error_collection=db["error-log"]
                        await error_collection.insert_one(error_dict)
                        
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                pass
            
            if file.content_type=="image/jpeg" or file.content_type=="image/png":
                #TODO : Extract text from image
                pass
             
            if file.content_type=="text/plain":
                #TODO : Extract text from text file
                pass

            if file.content_type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                #TODO : Extract text from word document
                pass
    
    except Exception as e:
        return {"error": str(e)}  # Return error message

    incorrect_files = file_counter - correct_files
    return {"message": f"You have uploaded {file_counter} files, {correct_files} files are correct processed and {incorrect_files} files are not processed.Here are the details of the processed files: {frontend_response}"}
