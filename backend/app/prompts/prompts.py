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
