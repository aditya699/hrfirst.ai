from pydantic import BaseModel


class JD(BaseModel):
    job_title:str
    job_description:str
    job_experience:str
    job_education:str
    job_skills:str
    job_responsibilities:str


