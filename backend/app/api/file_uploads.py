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
from langchain_community.document_loaders import Docx2txtLoader
from langchain_anthropic import ChatAnthropic #type: ignore
from langchain_core.messages import HumanMessage
import base64

load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["ANTHROPIC_API_KEY"]=os.getenv("ANTHROPIC_API_KEY")
CONNECTION_STRING=os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME="hr-first"

blob_service_client=BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client=blob_service_client.get_container_client(CONTAINER_NAME)

app = APIRouter()
llm=ChatOpenAI(model="gpt-4o-mini",temperature=0)

llm_image=ChatOpenAI(model="gpt-4o",temperature=0)
# llm=ChatAnthropic(model="claude-3-5-haiku-20241022",temperature=0)
structured_llm=llm.with_structured_output(CVUserData)

@app.post("/upload-files-process/")
async def upload_files(
    files: List[UploadFile] = File(...),  # Lists of files will be sent from frontend
    session_cookie: str = Form(...),  # session cookie(after the auth) 
):
    """
    This function is used to upload files to the server and process them.

    Args:
        files: List[UploadFile] = File(...): Lists of files will be sent from frontend
        session_cookie: str = Form(...): session cookie(after the auth) 

    Returns:
        dict: A dictionary containing the number of files uploaded, the number of files processed correctly, and the details of the processed files.
    
    Example Output:
    {
    "message": "You have uploaded 4 files, 4 files are correct processed and 0 files are not processed.Here are the details of the processed files: {'Aditya Bhatt CV.pdf': {'name': 'Aditya Bhatt', 'email': 'adityabhatt19058568031.stats@rla.du.ac.in', 'phone': '+91 7303041453', 'address': 'Not Found', 'education': 'PG Diploma in Software Engineering for Data Science (IIIT Hyderabad), BSC(H) Statistics (Delhi University)', 'experience': 'Mccormick – Supply Chain Analyst 1 (Apr 2024 – Present), Neenopal - Business Analyst (July 2022 – Apr 2024)', 'skills': 'Programming (Python, R, Pyspark, Syntactical JS, C), Visualization (Power BI, Tableau, Matplotlib, Seaborn, Plotly, ggplot, Folium, Excel, R, Google Data Studio), Machine Learning (Supervised and Unsupervised Learning, ANN, CNN, RNN, LSTM, Time Series Analysis, PyCaret, Pytorch, TensorFlow, MLFlow, Azure ML Studio, Azure Language, Azure Vision, Text Preprocessing, Text Encoding & Embedding, Hugging Face, OpenAI, Langchain, RAG, Fine Tunning, Langsmith, LLMs, AzureOpenAI, Chainlit, NLP, Tranformers, Google Vertex AI, AI Agents, Langgraph), Statistics (Descriptive Statistics, Inferential Statistics, Algebra, SPSS, Hypothesis Testing, Survey Sampling, Linear Modelling), Database (Azure Sql, MySQL, T-SQL, Postgre SQL, SparkSQL, MongoDB, Cassandra, MQL, Vector DBs), Deployment/Backend (Flask, FastAPI, Streamlit, Heroku, Azure, AWS SageMaker, Docker, PyTest, SQLAlchemy, Azure DevOps, GitHub), Others (Power Platform, TableauPrep, BeautifulSoup, SAP Crastal Report, Azure Data Factory, Azure DataBricks, Azure Synpase, Explainable AI, HTML, Recommendation System, Markov Decision Process)'}, 'Pulkit_Analyst_4yr.pdf': {'name': 'Pulkit Rawat', 'email': 'pulkitrawat97@gmail.com', 'phone': '7417700336', 'address': 'Not Found', 'education': 'GLA University, Mathura | Bachelor of Technology in Computer Science & Engineering Aug 2015 - Jun 2019', 'experience': 'Senior Analyst at Infosys Limited Jun 2022 – Jan 2024; Analyst at Tata Consultancy Services May 2019 – Jun 2022', 'skills': 'Python, SQL, Microsoft Power BI, JIRA, Google Big Query, DAX, Jupyter Notebook IDE, Microsoft Excel, AWS, Data Visualization & Reporting, Customer Segmentation, Sales Performance Analysis, Pricing Strategy Development, Data Quality & Compliance, KPI Tracking, Process Documentation & Improvement, Workforce Analytics.'}, 'Ritesh_Kumar_Resume.pdf': {'name': 'Ritesh Kumar', 'email': 'pandeyritesh007@gmail.com', 'phone': '8669666079', 'address': 'Noida', 'education': 'Polytechnic from Tirupati College of Pharmacy (07/2009 – 07/2012), B.Tech from Haldia Institute Of Technology (08/2013 – 08/2016), Matriculation from St. Joseph Public School (03/2008 – 03/2009)', 'experience': 'Tech Mahindra (Associate Analyst, 09/2016 – 05/2019), Optum (Associate Data Analyst, 05/2019 – 11/2020), Accenture (Data Science Analyst, 11/2020 – present)', 'skills': 'Data Science, Machine Learning, Python, SQL/HIVE, Market Mix Modelling, Azure Databricks'}, 'DD9FB8CC-F241-4E3D-86E2-78B57B37874C.pdf': {'name': 'Mradu Singh Kushwah', 'email': 'mradu.kush19@gmail.com', 'phone': '+919818980186', 'address': 'Not Found', 'education': 'M.Sc Statistics- Ramjas College, Faculty of Mathematical Sciences, University of Delhi - 80.0% 2017-2019; B.Sc(H) Statistics –Ramjas College , University of Delhi - 79.2% 2013-2016; 12th ISC - St. Anthony’s Junior College, Agra- 93.25% 2013; 10th ICSE- St. Anthony’s Junior College, Agra- 91.2% 2011', 'experience': 'Associate Manager, Course 5 intelligence, Gurugram May 2024 – Present; Senior Data Analyst, BCG X, Boston Consulting Group, Gurugram Dec 2023 – May 2024; Data Scientist, Marketing Analytics, AB InBev, Bangalore May 2022- Dec 2023; Business Analyst & Senior Business Analyst, Customer Insights and Data Analytics (CIDA), Evalueserve, Gurugram June 2019- May 2022; Data Analyst, Vidooly Media Tech Pvt.Ltd, Noida June 2018- July 2018; Ground Researcher- Policy innovations September 2015', 'skills': 'Programming Languages: SAS (Base SAS, Proc SQL, Macros, Loops), Python, R; Tools & Platforms: MS Excel, Power BI, SPSS, MS PowerPoint, MLFlow, Alteryx (Basic), Azure ML, GitLab; Machine Learning and Data Science: Supervised Learning, Unsupervised Learning, Natural Language Processing (NLP), Time Series Analysis, Recommender Systems, Optimization & Model Selection, Marketing Analytics; Software Development & Deployment: API & Web Application Development: Flask, Front-End Web Development: HTML, CSS, JavaScript; Industry Experience: Consumer Packaged Goods (CPG) Industry, Logistics Industry, Consumer Industry, Credit Risk.'}}"
    }
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
                        print("Error in processing file: ",e)   
                        #Dump it database the error

                        error_dict={
                            "file_name": file.filename,
                            "error": str(e),
                            "user_id": user_id,
                            "user_email": user_email,
                            "uploaded_at": datetime.now(),
                            "type":"api-error"
                        }
                        client=await get_client()
                        if client:
                            db=client["hr-first"]
                            error_collection=db["error-log"]
                            await error_collection.insert_one(error_dict)
                        
                        response = CVUserData(
                            name="Not Found",
                            email="Not Found",
                            phone="Not Found",
                            education="Not Found",
                            experience="Not Found",
                            skills="Not Found"
                        )
                    
                    # Convert the Pydantic model to a dictionary to avoid MongoDB serialization issues
                    response_dict = {
                        "name": response.name,
                        "email": response.email,
                        "phone": response.phone,
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
                        "error": str(e),
                        "user_id": user_id,
                        "user_email": user_email,
                        "uploaded_at": datetime.now()
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
                #NOTE : Resumes are not uploaded as images , will use the same design for chat with data
                pass
             
            if file.content_type=="text/plain":
                #TODO : Extract text from text file
                #NOTE : Resumes are not uploaded as text files , will use the same design for chat with data
                pass

            if file.content_type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                
                #TODO : Extract text from word document
                try:

                    # Save file temporarily to process with Docx2txtLoader  
                    temp_file_path = f"temp_{file.filename}"
                    with open(temp_file_path, "wb") as temp_file:
                        temp_file.write(file_content)

                    loader=Docx2txtLoader(temp_file_path)
                    documents=loader.load()
                    text_content=""
                    for doc in documents:
                        text_content+=doc.page_content+"\n"
                
                    try:
                        response=await structured_llm.ainvoke(CV_DATA_PROMPT.format(cv_data=text_content))
                    except Exception as e:
                        print("Error in processing file: ",e)
                        #Dump it database the error
                        error_dict={
                            "file_name": file.filename,
                            "error": str(e),
                            "user_id": user_id,
                            "user_email": user_email,
                            "uploaded_at": datetime.now(),
                            "type":"api-error"
                        }
                        client=await get_client()
                        if client:
                            db=client["hr-first"]
                            error_collection=db["error-log"]
                            await error_collection.insert_one(error_dict)
                        
                        response=CVUserData(
                            name="Not Found",
                            email="Not Found",
                            phone="Not Found",
                            education="Not Found",
                            experience="Not Found",
                            skills="Not Found"
                        )
                
                    frontend_response[file.filename]=response_dict

                    metadata_dict={
                        "file_name": file.filename,
                        "file_size": len(file_content),
                        "file_type": file.content_type, 
                        "extracted_text": text_content,
                        "user_id": user_id,
                        "user_email": user_email,
                        "uploaded_at": datetime.now(),
                        "extracted_data": response_dict,
                        "name": response.name,
                        "email": response.email,
                        "phone": response.phone,
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
                        "error": str(e),
                        "user_id": user_id,
                        "user_email": user_email,
                        "uploaded_at": datetime.now()
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
    
    except Exception as e:
        return {"error": str(e)}  # Return error message

    incorrect_files = file_counter - correct_files
    return {"message": f"You have uploaded {file_counter} files, {correct_files} files are correct processed and {incorrect_files} files are not processed.Here are the details of the processed files: {frontend_response}"}

@app.post("/upload-files-process-chat/")
async def upload_files(
    files: List[UploadFile] = File(...),  # Lists of files will be sent from frontend
    session_cookie: str = Form(...),  # session cookie(after the auth) 
):
    """
    This function is used to upload files to the server and process them.

    Args:
        files: List[UploadFile] = File(...): Lists of files will be sent from frontend
        session_cookie: str = Form(...): session cookie(after the auth) 

    Returns:
        dict: A dictionary containing the number of files uploaded, the number of files processed correctly, and the details of the processed files.
    
    Example Output:
    {
    "message": "You have uploaded 4 files, 4 files are correct processed and 0 files are not processed.Here are the details of the processed files: {'Aditya Bhatt CV.pdf': {'name': 'Aditya Bhatt', 'email': 'adityabhatt19058568031.stats@rla.du.ac.in', 'phone': '+91 7303041453', 'address': 'Not Found', 'education': 'PG Diploma in Software Engineering for Data Science (IIIT Hyderabad), BSC(H) Statistics (Delhi University)', 'experience': 'Mccormick – Supply Chain Analyst 1 (Apr 2024 – Present), Neenopal - Business Analyst (July 2022 – Apr 2024)', 'skills': 'Programming (Python, R, Pyspark, Syntactical JS, C), Visualization (Power BI, Tableau, Matplotlib, Seaborn, Plotly, ggplot, Folium, Excel, R, Google Data Studio), Machine Learning (Supervised and Unsupervised Learning, ANN, CNN, RNN, LSTM, Time Series Analysis, PyCaret, Pytorch, TensorFlow, MLFlow, Azure ML Studio, Azure Language, Azure Vision, Text Preprocessing, Text Encoding & Embedding, Hugging Face, OpenAI, Langchain, RAG, Fine Tunning, Langsmith, LLMs, AzureOpenAI, Chainlit, NLP, Tranformers, Google Vertex AI, AI Agents, Langgraph), Statistics (Descriptive Statistics, Inferential Statistics, Algebra, SPSS, Hypothesis Testing, Survey Sampling, Linear Modelling), Database (Azure Sql, MySQL, T-SQL, Postgre SQL, SparkSQL, MongoDB, Cassandra, MQL, Vector DBs), Deployment/Backend (Flask, FastAPI, Streamlit, Heroku, Azure, AWS SageMaker, Docker, PyTest, SQLAlchemy, Azure DevOps, GitHub), Others (Power Platform, TableauPrep, BeautifulSoup, SAP Crastal Report, Azure Data Factory, Azure DataBricks, Azure Synpase, Explainable AI, HTML, Recommendation System, Markov Decision Process)'}, 'Pulkit_Analyst_4yr.pdf': {'name': 'Pulkit Rawat', 'email': 'pulkitrawat97@gmail.com', 'phone': '7417700336', 'address': 'Not Found', 'education': 'GLA University, Mathura | Bachelor of Technology in Computer Science & Engineering Aug 2015 - Jun 2019', 'experience': 'Senior Analyst at Infosys Limited Jun 2022 – Jan 2024; Analyst at Tata Consultancy Services May 2019 – Jun 2022', 'skills': 'Python, SQL, Microsoft Power BI, JIRA, Google Big Query, DAX, Jupyter Notebook IDE, Microsoft Excel, AWS, Data Visualization & Reporting, Customer Segmentation, Sales Performance Analysis, Pricing Strategy Development, Data Quality & Compliance, KPI Tracking, Process Documentation & Improvement, Workforce Analytics.'}, 'Ritesh_Kumar_Resume.pdf': {'name': 'Ritesh Kumar', 'email': 'pandeyritesh007@gmail.com', 'phone': '8669666079', 'address': 'Noida', 'education': 'Polytechnic from Tirupati College of Pharmacy (07/2009 – 07/2012), B.Tech from Haldia Institute Of Technology (08/2013 – 08/2016), Matriculation from St. Joseph Public School (03/2008 – 03/2009)', 'experience': 'Tech Mahindra (Associate Analyst, 09/2016 – 05/2019), Optum (Associate Data Analyst, 05/2019 – 11/2020), Accenture (Data Science Analyst, 11/2020 – present)', 'skills': 'Data Science, Machine Learning, Python, SQL/HIVE, Market Mix Modelling, Azure Databricks'}, 'DD9FB8CC-F241-4E3D-86E2-78B57B37874C.pdf': {'name': 'Mradu Singh Kushwah', 'email': 'mradu.kush19@gmail.com', 'phone': '+919818980186', 'address': 'Not Found', 'education': 'M.Sc Statistics- Ramjas College, Faculty of Mathematical Sciences, University of Delhi - 80.0% 2017-2019; B.Sc(H) Statistics –Ramjas College , University of Delhi - 79.2% 2013-2016; 12th ISC - St. Anthony's Junior College, Agra- 93.25% 2013; 10th ICSE- St. Anthony's Junior College, Agra- 91.2% 2011', 'experience': 'Associate Manager, Course 5 intelligence, Gurugram May 2024 – Present; Senior Data Analyst, BCG X, Boston Consulting Group, Gurugram Dec 2023 – May 2024; Data Scientist, Marketing Analytics, AB InBev, Bangalore May 2022- Dec 2023; Business Analyst & Senior Business Analyst, Customer Insights and Data Analytics (CIDA), Evalueserve, Gurugram June 2019- May 2022; Data Analyst, Vidooly Media Tech Pvt.Ltd, Noida June 2018- July 2018; Ground Researcher- Policy innovations September 2015', 'skills': 'Programming Languages: SAS (Base SAS, Proc SQL, Macros, Loops), Python, R; Tools & Platforms: MS Excel, Power BI, SPSS, MS PowerPoint, MLFlow, Alteryx (Basic), Azure ML, GitLab; Machine Learning and Data Science: Supervised Learning, Unsupervised Learning, Natural Language Processing (NLP), Time Series Analysis, Recommender Systems, Optimization & Model Selection, Marketing Analytics; Software Development & Deployment: API & Web Application Development: Flask, Front-End Web Development: HTML, CSS, JavaScript; Industry Experience: Consumer Packaged Goods (CPG) Industry, Logistics Industry, Consumer Industry, Credit Risk.'}}"
    }
    """
    #from the session cookie, we will get the user_id and user_email(for now since auth is not implemented let it be like this)

    user_id="123"   #this would come after decoding the session cookie
    user_email="test@test.com"  #this would come after decoding the session cookie
   
    #push data to container with user_id as the folder name
    user_folder_name=f"{user_id}"

    file_counter=0
    correct_files=0
    extracted_text={}    
    
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

            # Create temporary file path for processing
            temp_file_path = f"temp_{file.filename}"
            
            try:
                # Write content to temporary file
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(file_content)
                
                # Process PDF files
                if file.content_type == "application/pdf":
                    try:
                        # Extract text from PDF
                        loader = PyPDFLoader(temp_file_path)
                        pages = []
                        text_content = ""
                        for page in loader.load():
                            pages.append(page)
                            text_content += page.page_content + "\n"

                        extracted_text[file.filename] = text_content
                        
                        # Store the extracted text with metadata
                        metadata_dict = {
                            "file_name": file.filename,
                            "file_size": len(file_content),
                            "file_type": file.content_type,
                            "file_url": blob_client.url,
                            "extracted_text": text_content,
                            "user_id": user_id,
                            "user_email": user_email,
                            "uploaded_at": datetime.now(),
                            "extraction_method": "PyPDFLoader"
                        }
                        
                        # Save to MongoDB
                        client = await get_client()
                        if client:
                            db = client["hr-first"]
                            collection = db["chat-data"]
                            await collection.insert_one(metadata_dict)
                        
                        correct_files += 1
                        
                    except Exception as e:
                        print(f"Error processing PDF {file.filename}: {e}")
                        error_dict = {
                            "file_name": file.filename,
                            "error": str(e),
                            "user_id": user_id,
                            "user_email": user_email,
                            "uploaded_at": datetime.now(),
                            "type": "pdf-processing-error"
                        }
                        client = await get_client()
                        if client:
                            db = client["hr-first"]
                            error_collection = db["error-log"]
                            await error_collection.insert_one(error_dict)
                
                # Process image files
                elif file.content_type == "image/jpeg" or file.content_type == "image/png":
                    try:
                        # Read the image as base64 for processing with LLM
                        with open(temp_file_path, "rb") as image_file:
                            image_bytes = image_file.read()
                            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        
                        # Create a message with the image for the model
                        message = HumanMessage(
                            content=[
                                {"type": "text", "text": "Extract all text visible in this image. Format the text to maintain its original structure as much as possible."},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/{file.content_type.split('/')[1]};base64,{image_base64}"},
                                },
                            ],
                        )
                        
                        # Use GPT-4o for image analysis
                        response = llm_image.invoke([message])
                        text_content = response.content

                        extracted_text[file.filename] = text_content
                        
                        # Store the extracted text with metadata
                        metadata_dict = {
                            "file_name": file.filename,
                            "file_size": len(file_content),
                            "file_type": file.content_type,
                            "file_url": blob_client.url,
                            "extracted_text": text_content,
                            "user_id": user_id,
                            "user_email": user_email,
                            "uploaded_at": datetime.now(),
                            "extraction_method": "gpt-4o-vision"
                        }
                        
                        # Save to MongoDB
                        client = await get_client()
                        if client:
                            db = client["hr-first"]
                            collection = db["chat-data"]
                            await collection.insert_one(metadata_dict)
                        
                        correct_files += 1
                        
                    except Exception as e:
                        print(f"Error processing image {file.filename}: {e}")
                        error_dict = {
                            "file_name": file.filename,
                            "error": str(e),
                            "user_id": user_id,
                            "user_email": user_email,
                            "uploaded_at": datetime.now(),
                            "type": "image-processing-error"
                        }
                        client = await get_client()
                        if client:
                            db = client["hr-first"]
                            error_collection = db["error-log"]
                            await error_collection.insert_one(error_dict)
                
                # Process text files
                elif file.content_type == "text/plain":
                    try:
                        # Read text file content
                        with open(temp_file_path, "r") as text_file:
                            text_content = text_file.read()
                        
                        extracted_text[file.filename] = text_content

                        # Save the extracted text to the metadata dictionary
                        metadata_dict = {
                            "file_name": file.filename,
                            "file_size": len(file_content),
                            "file_type": file.content_type,
                            "file_url": blob_client.url,
                            "extracted_text": text_content,
                            "user_id": user_id,
                            "user_email": user_email,
                            "uploaded_at": datetime.now(),
                            "extraction_method": "text-reader"
                        }

                        # Save the metadata to MongoDB
                        client = await get_client()
                        if client:
                            db = client["hr-first"]
                            collection = db["chat-data"]
                            await collection.insert_one(metadata_dict)

                        correct_files += 1
                        
                    except Exception as e:
                        print(f"Error processing text file {file.filename}: {e}")
                        error_dict = {
                            "file_name": file.filename,
                            "error": str(e),
                            "user_id": user_id,
                            "user_email": user_email,
                            "uploaded_at": datetime.now(),
                            "type": "text-processing-error"
                        }
                        client = await get_client()
                        if client:
                            db = client["hr-first"]
                            error_collection = db["error-log"]
                            await error_collection.insert_one(error_dict)

                # Process Word documents
                elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    try:
                        # Extract text from Word document
                        loader = Docx2txtLoader(temp_file_path)
                        documents = loader.load()
                        text_content = ""
                        for doc in documents:
                            text_content += doc.page_content + "\n"

                        extracted_text[file.filename] = text_content
                        
                        # Store the extracted text with metadata
                        metadata_dict = {
                            "file_name": file.filename,
                            "file_size": len(file_content),
                            "file_type": file.content_type,
                            "file_url": blob_client.url,
                            "extracted_text": text_content,
                            "user_id": user_id,
                            "user_email": user_email,
                            "uploaded_at": datetime.now(),
                            "extraction_method": "Docx2txtLoader"
                        }
                        
                        # Save to MongoDB
                        client = await get_client()
                        if client:
                            db = client["hr-first"]
                            collection = db["chat-data"]
                            await collection.insert_one(metadata_dict)
                        
                        correct_files += 1
                        
                    except Exception as e:
                        print(f"Error processing Word document {file.filename}: {e}")
                        error_dict = {
                            "file_name": file.filename,
                            "error": str(e),
                            "user_id": user_id,
                            "user_email": user_email,
                            "uploaded_at": datetime.now(),
                            "type": "docx-processing-error"
                        }
                        client = await get_client()
                        if client:
                            db = client["hr-first"]
                            error_collection = db["error-log"]
                            await error_collection.insert_one(error_dict)
                
                else:
                    print(f"Unsupported file type: {file.content_type} for file {file.filename}")
                    error_dict = {
                        "file_name": file.filename,
                        "error": f"Unsupported file type: {file.content_type}",
                        "user_id": user_id,
                        "user_email": user_email,
                        "uploaded_at": datetime.now(),
                        "type": "unsupported-file-type"
                    }
                    client = await get_client()
                    if client:
                        db = client["hr-first"]
                        error_collection = db["error-log"]
                        await error_collection.insert_one(error_dict)
                    
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")
                error_dict = {
                    "file_name": file.filename,
                    "error": str(e),
                    "user_id": user_id,
                    "user_email": user_email,
                    "uploaded_at": datetime.now(),
                    "type": "general-processing-error"
                }
                client = await get_client()
                if client:
                    db = client["hr-first"]
                    error_collection = db["error-log"]
                    await error_collection.insert_one(error_dict)
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
    except Exception as e:
        return {"error": str(e)}  # Return error message

    incorrect_files = file_counter - correct_files
    return {"message": f"You have uploaded {file_counter} files, {correct_files} files are correct processed and {incorrect_files} files are not processed. Data extracted from the files: {extracted_text}"}