from datetime import datetime
from app.database.get_client import get_client
from fastapi import Request

# Updated error logging function to use app-wide MongoDB connection
async def log_error(request: Request, error, endpoint, **additional_info):
    """
    Log errors to the database using the app-wide MongoDB connection.
    
    Args:
        request (Request): FastAPI request object
        error (str): Error message
        endpoint (str): API endpoint where error occurred
        **additional_info: Additional context information
    """
    error_dict = {
        "error": error,
        "endpoint": endpoint,
        "timestamp": datetime.now(),
        **additional_info
    }
    
    try:
        error_collection = request.app.mongodb["error-log"]
        await error_collection.insert_one(error_dict)
    except Exception as e:
        # If we can't log to DB, print to console as fallback
        print(f"Error logging failed: {str(e)}")
        print(f"Original error: {error_dict}")