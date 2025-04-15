'''
NOTE:
1.Designing a scalable backend for file uploads
'''

from pydantic import BaseModel

class CVUserData(BaseModel):
    name:str
    email:str
    phone:str
    address:str
    education:str
    experience:str
    skills:str
    linkedin_url:str
