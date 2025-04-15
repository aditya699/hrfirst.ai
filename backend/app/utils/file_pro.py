import os
from datetime import datetime
from fastapi import Request, UploadFile, HTTPException
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from app.utils.log_err import log_error
from azure.storage.blob import ContentSettings #type: ignore

async def _process_file(request: Request, file: UploadFile, user_id: str, user_email: str):
    """
    Process an individual file - upload to blob storage and extract data.
    
    Args:
        request (Request): FastAPI request object
        file (UploadFile): The file to process
        user_id (str): The ID of the user uploading the file
        user_email (str): The email of the user uploading the file
        
    Returns:
        dict: Processing result with success status and extracted data
    """
    container_client = request.app.blob_container_client
    user_folder_name = f"{user_id}"
    blob_path = f"{user_folder_name}/{file.filename}"
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload file to blob storage
        blob_client = container_client.get_blob_client(blob_path)
        blob_client.upload_blob(file_content, overwrite=True,content_settings=ContentSettings(
            content_type=file.content_type,
            content_disposition='inline'
        ))
        
        # Process file based on content type
        if file.content_type == "application/pdf":
            return await _process_pdf_file(request, file, file_content, user_id, user_email, blob_client.url)
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return await _process_docx_file(request, file, file_content, user_id, user_email, blob_client.url)
        else:
            # Log unsupported file type
            await log_error(
                request=request,
                error=f"Unsupported file type: {file.content_type}",
                endpoint="upload-files-process",
                user_id=user_id,
                user_email=user_email
            )
            return {"success": False, "data": None}
            
    except Exception as e:
        # Log specific file processing error
        await log_error(
            request=request,
            error=f"Error processing file {file.filename}: {str(e)}",
            endpoint="upload-files-process",
            user_id=user_id,
            user_email=user_email
        )
        return {"success": False, "data": None}
    
async def _process_pdf_file(request: Request, file: UploadFile, file_content: bytes, 
                           user_id: str, user_email: str, blob_url: str):
    """
    Process a PDF file and extract text and structured data.
    
    Args:
        request (Request): FastAPI request object
        file (UploadFile): The PDF file
        file_content (bytes): The file content
        user_id (str): The ID of the user uploading the file
        user_email (str): The email of the user uploading the file
        blob_url (str): URL to the uploaded blob
        
    Returns:
        dict: Processing result with success status and extracted data
    """
    # Save file temporarily
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # Write content to temp file
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_content)
        
        # Extract text using PyPDFLoader
        loader = PyPDFLoader(temp_file_path)
        text_content = ""
        
        for page in loader.load():
            text_content += page.page_content + "\n"
        
        # Extract structured data from CV
        response = await _extract_cv_data(request, text_content, file.filename, user_id, user_email,blob_url,"pdf")
        
        # Store metadata in database
        await _store_cv_metadata(
            request=request,
            file=file,
            file_content=file_content,
            text_content=text_content,
            extracted_data=response,
            user_id=user_id,
            user_email=user_email,
            blob_url=blob_url
        )
        
        return {"success": True, "data": response}
        
    except Exception as e:
        # Log PDF processing error
        await log_error(
            request=request,
            error=f"Error processing PDF {file.filename}: {str(e)}",
            endpoint="process-pdf",
            user_id=user_id,
            user_email=user_email
        )
        return {"success": False, "data": None}
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


async def _process_docx_file(request: Request, file: UploadFile, file_content: bytes,
                            user_id: str, user_email: str, blob_url: str):
    """
    Process a DOCX file and extract text and structured data.
    
    Args:
        request (Request): FastAPI request object
        file (UploadFile): The DOCX file
        file_content (bytes): The file content
        user_id (str): The ID of the user uploading the file
        user_email (str): The email of the user uploading the file
        blob_url (str): URL to the uploaded blob
        
    Returns:
        dict: Processing result with success status and extracted data
    """
    # Save file temporarily
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # Write content to temp file
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_content)
        
        # Extract text using Docx2txtLoader
        loader = Docx2txtLoader(temp_file_path)
        documents = loader.load()
        text_content = ""
        
        for doc in documents:
            text_content += doc.page_content + "\n"
        
        # Extract structured data from CV
        response = await _extract_cv_data(request, text_content, file.filename, user_id, user_email,blob_url,"docx")
        
        # Store metadata in database
        await _store_cv_metadata(
            request=request,
            file=file,
            file_content=file_content,
            text_content=text_content,
            extracted_data=response,
            user_id=user_id,
            user_email=user_email,
            blob_url=f"https://view.officeapps.live.com/op/view.aspx?src={blob_url}"
        )
        
        return {"success": True, "data": response}
        
    except Exception as e:
        # Log DOCX processing error
        await log_error(
            request=request,
            error=f"Error processing DOCX {file.filename}: {str(e)}",
            endpoint="process-docx",
            user_id=user_id,
            user_email=user_email
        )
        return {"success": False, "data": None}
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


async def _extract_cv_data(request: Request, text_content: str, filename: str, user_id: str, user_email: str,blob_url:str,file_type:str):
    """
    Extract structured data from CV text content using LLM.
    
    Args:
        request (Request): FastAPI request object
        text_content (str): The text content extracted from the CV
        filename (str): The filename of the CV
        user_id (str): The ID of the user
        user_email (str): The email of the user
        blob_url (str): URL to the uploaded blob
        file_type (str): The type of the file
    Returns:
        dict: Extracted CV data as a dictionary
    """
    try:
        # Get structured LLM from app state
        structured_llm = request.app.structured_llm
        
        # Invoke LLM to extract CV data
        response = await structured_llm.ainvoke(request.app.CV_DATA_PROMPT.format(cv_data=text_content))
        
        if file_type == "pdf":
        # Convert Pydantic model to dictionary
            return {
                "name": response.name,
                "email": response.email,
                "phone": response.phone,
                "address": getattr(response, "address", "Not Found"),
                "education": response.education,
                "experience": response.experience,
                "skills": response.skills,
                "linkedin_url": response.linkedin_url,
                "file_url": blob_url
            }
        elif file_type == "docx":
            return {
                "name": response.name,
                "email": response.email,
                "phone": response.phone,
                "address": getattr(response, "address", "Not Found"),
                "education": response.education,
                "experience": response.experience,
                "skills": response.skills,
                "linkedin_url": response.linkedin_url,
                "file_url": f"https://view.officeapps.live.com/op/view.aspx?src={blob_url}"
            }
        
    except Exception as e:
        # Log LLM processing error
        await log_error(
            request=request,
            error=f"Error extracting CV data for {filename}: {str(e)}",
            endpoint="extract-cv-data",
            user_id=user_id,
            user_email=user_email,
            type="api-error"
        )
        
        # Return default values on error
        return {
            "name": "Not Found",
            "email": "Not Found",
            "phone": "Not Found",
            "address": "Not Found",
            "education": "Not Found",
            "experience": "Not Found",
            "skills": "Not Found",
            "linkedin_url": "Not Found",
            "file_url": blob_url
        }


async def _store_cv_metadata(request: Request, file: UploadFile, file_content: bytes,
                           text_content: str, extracted_data: dict, user_id: str,
                           user_email: str, blob_url: str):
    """
    Store CV metadata in the database.
    
    Args:
        request (Request): FastAPI request object
        file (UploadFile): The uploaded file
        file_content (bytes): The file content
        text_content (str): The extracted text content
        extracted_data (dict): The extracted CV data
        user_id (str): The ID of the user
        user_email (str): The email of the user
        blob_url (str): URL to the uploaded blob
        
    Returns:
        None
    """
    # Create metadata dictionary
    metadata_dict = {
        "file_name": file.filename,
        "file_size": len(file_content),
        "file_type": file.content_type,
        "file_url": blob_url,
        "extracted_text": text_content,
        "user_id": user_id,
        "user_email": user_email,
        "uploaded_at": datetime.now(),
        "extracted_data": extracted_data,
        **extracted_data  # Flatten extracted data for direct field access
    }
    
    # Store in MongoDB
    collection = request.app.mongodb["cv-data"]
    await collection.insert_one(metadata_dict)
