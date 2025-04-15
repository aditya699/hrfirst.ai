from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api import file_uploads
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from azure.storage.blob import BlobServiceClient #type: ignore
from langchain_openai import ChatOpenAI
from app.schemas.file_uploads import CVUserData
from app.schemas.jd import JD
from app.prompts.prompts import CV_DATA_PROMPT,JD_PROMPT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variables
MONGODB_URL = os.getenv("uri")

app = FastAPI(title="HR First.AI", description="Backend for HR First.AI")
app.mongodb_client = None
app.mongodb = None

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Serve templates
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Database connection events
@app.on_event("startup") 
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    app.mongodb = app.mongodb_client["hr-first"]
    print("Connected to MongoDB")
    CONNECTION_STRING=os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    CONTAINER_NAME=os.getenv("CONTAINER_NAME")
    app.blob_container_client = BlobServiceClient.from_connection_string(CONNECTION_STRING).get_container_client(CONTAINER_NAME)
    print("Connected to Blob Storage")
    os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
    llm=ChatOpenAI(model="gpt-4o-mini",temperature=0)
    llm_jd=ChatOpenAI(model="gpt-4o-mini",temperature=0) 
    app.structured_llm=llm.with_structured_output(CVUserData)
    app.structured_llm_jd=llm_jd.with_structured_output(JD)
    print("GPT4o mini and GPT4o are initialized")
    app.CV_DATA_PROMPT=CV_DATA_PROMPT
    app.JD_PROMPT=JD_PROMPT
    print("Prompts are initialized")

@app.on_event("shutdown")
async def shutdown_db_client():
    if app.mongodb_client:
        app.mongodb_client.close()
        print("MongoDB connection closed")

# Home route 
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Include routers
app.include_router(file_uploads.app, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)