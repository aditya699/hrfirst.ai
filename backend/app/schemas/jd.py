from pydantic import BaseModel


class JD(BaseModel):
    job_title:str
    job_description:str
    job_location:str
    job_type:str
    job_category:str
    job_experience:str
    job_education:str
    job_skills:str
    job_responsibilities:str
    job_requirements:str    


