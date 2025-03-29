from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import file_uploads

app = FastAPI(title="HR First.AI", description="Backend for HR First.AI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(file_uploads.app, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
