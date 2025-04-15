CV_DATA_PROMPT = """
You are a helpful assistant that extracts data from a CV.

Extract the following data:
- name
- email
- phone
- education
- experience
- skills

IMPORTANT: If data is not found, return "Not Found" for that field.

cv_data:
{cv_data}
"""

JD_PROMPT = """
You are a helpful assistant that creates a job description.

Upon given user requirements, you will create a job description and return it in a structured format.

Return the following data:
-job_title
-job_description
-job_experience
-job_education
-job_skills
-job_responsibilities
-Linkedin_url

user_requirements:
{user_requirements}
"""
