import os
import base64
import uuid
from io import BytesIO
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from app.database.get_client import get_client
from app.schemas.jd import JD
from app.prompts.prompts import JD_PROMPT
from fastapi import Body
from bson.objectid import ObjectId #type: ignore
from app.utils.pdf_gen import generate_pdf
from app.utils.log_err import log_error
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, File, HTTPException, UploadFile, Form, Request
from app.utils.file_pro import _process_file
load_dotenv()

app = APIRouter()

@app.post("/upload-files-process/")
async def upload_files(
    request: Request,
    files: List[UploadFile] = File(...),
    session_cookie: str = Form(...),
):
    """
    Upload files to the server and process them.

    Args:
        request (Request): FastAPI request object
        files (List[UploadFile]): List of files to upload and process
        session_cookie (str): Session cookie for authentication

    Returns:
        dict: A dictionary containing the number of files uploaded, processed correctly,
              and the details of the processed files.
    """
    # TODO: Implement proper session validation when auth is implemented
    user_id = "123"  # Will come from session cookie after auth implementation
    user_email = "test@test.com"  # Will come from session cookie after auth implementation
    
    # Initialize counters and response data
    file_counter = 0
    correct_files = 0
    frontend_response = {}
    
    try:
        for file in files:
            file_counter += 1
            
            # Process each file
            result = await _process_file(
                request=request, 
                file=file,
                user_id=user_id,
                user_email=user_email
            )
            
            # If processing was successful, add to correct files counter
            if result["success"]:
                correct_files += 1
                frontend_response[file.filename] = result["data"]
                
        # Calculate incorrect files
        incorrect_files = file_counter - correct_files
        
        return {
            "message": f"You have uploaded {file_counter} files, {correct_files} files are correct processed and {incorrect_files} files are not processed.",
            "details": frontend_response
        }
            
    except Exception as e:
        # Log all exceptions
        await log_error(
            request=request,
            error=str(e),
            endpoint="upload-files-process",
            user_id=user_id,
            user_email=user_email
        )
        
        # Return appropriate HTTP exception
        raise HTTPException(status_code=500, detail="Error processing uploaded files.")

@app.post("/create-job-description/")
async def create_job_description(
    request: Request,
    information: str = Form(...),
    session_cookie: str = Form(...),  # session cookie(after the auth) 
):
    """
    Create a job description based on provided information.

    Args:
        request (Request): FastAPI request object
        information (str): The information about the job description provided by the user.
        session_cookie (str): Session cookie for authentication.

    Returns:
        dict: A dictionary containing the job description and status message.
    """
    # TODO: Implement proper session validation when auth is implemented
    user_id = "123"  # Will come from session cookie after auth implementation
    user_email = "test@test.com"  # Will come from session cookie after auth implementation

    try:
        # Generate job description using LLM
        response = await request.app.structured_llm_jd.ainvoke(JD_PROMPT.format(user_requirements=information))
        
        # Create data dictionary from response
        data_dict = {
            "job_title": response.job_title,
            "job_description": response.job_description,
            "job_experience": response.job_experience,
            "job_education": response.job_education,
            "job_skills": response.job_skills,
            "job_responsibilities": response.job_responsibilities,
            "Linkedin_url": response.Linkedin_url,
            "user_id": user_id,
            "user_email": user_email,
            "uploaded_at": datetime.now(),
            "is_exported": 0
        }
        
        # Use the app-wide MongoDB connection
        collection = request.app.mongodb["jd-data"]
        result = await collection.insert_one(data_dict)
        
        # Convert ObjectId to string for the response
        data_dict["_id"] = str(result.inserted_id)
        
        return {
            "message": "Job description created successfully",
            "job_description": data_dict
        }
            
    except Exception as e:
        # Log all exceptions
        await log_error(
            request=request,
            error=str(e),
            endpoint="create-job-description",
            user_id=user_id,
            user_email=user_email
        )
        
        # Otherwise, convert to a generic HTTP 500 error
        raise HTTPException(status_code=500, detail="Error creating job description.")


@app.get("/get-job-description-pdf/{job_id}")
async def get_job_description_pdf(request: Request, job_id: str):
    """
    Generate and return a job description as PDF.

    Args:
        request (Request): FastAPI request object
        job_id (str): The ID of the job description to export.

    Returns:
        StreamingResponse: A PDF file of the job description.
    """
    try:
        # Validate job_id format
        if not ObjectId.is_valid(job_id):
            raise HTTPException(status_code=400, detail="Invalid job ID format")
        
        # Use the app-wide MongoDB connection
        collection = request.app.mongodb["jd-data"]
        job_id_obj = ObjectId(job_id)
        
        # Increment export counter and retrieve job description in one operation
        result = await collection.find_one_and_update(
            {"_id": job_id_obj}, 
            {"$inc": {"is_exported": 1}},
            return_document=True  # Return the updated document
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        # Generate PDF
        pdf_buffer = await generate_pdf(result)
        
        # Create a safe filename
        safe_title = result.get("job_title", "job-description").replace(" ", "-").lower()
        filename = f"{safe_title}-{datetime.now().strftime('%Y-%m-%d')}.pdf"
        
        # Return streaming response
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        # Log all exceptions
        await log_error(
            request=request,
            error=str(e),
            endpoint="export-job-description-pdf",
            job_id=job_id
        )
            
        # Otherwise, convert to a generic HTTP 500 error
        raise HTTPException(status_code=500, detail="Error exporting PDF.")


