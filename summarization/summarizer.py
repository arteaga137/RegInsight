import json
from openai import OpenAI

def summarize_content(emails_data, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    schema = {
        "type": "object",
        "properties": {
            "Title of the Regulation": {
                "type": "object",
                "properties": {
                    "Original Language": {"type": "string"},
                    "English": {"type": "string"}
                },
                "required": ["Original Language", "English"],
                "additionalProperties": False
            },
            "From": {"type": "string"},
            "Subject": {"type": "string"},
            "Tags": {
                "type": "array",
                "items": {"type": "string"},
                "additionalProperties": False
            },
            "Jurisdiction": {"type": "string"},
            "Subject Matter": {"type": "string"},
            "Date": {"type": "string"},
            "Summary": {"type": "string"},
            "Analysis": {
                "type": "object",
                "properties": {
                    "Purpose and Scope": {"type": "string"}
                },
                "required": ["Purpose and Scope"],
                "additionalProperties": False
            },
            "Relevant Regulations or Legal Measures": {
                "type": "array",
                "items": {"type": "string"},
                "additionalProperties": False
            },
            "Business Impact": {
                "type": "object",
                "properties": {
                    "Overview": {"type": "string"}
                },
                "required": ["Overview"],
                "additionalProperties": False
            },
            "Conclusion": {
                "type": "object",
                "properties": {
                    "Overview": {"type": "string"}
                },
                "required": ["Overview"],
                "additionalProperties": False
            },
            "Relevant Links": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "url": {"type": "string"}
                    },
                    "required": ["description", "url"],
                    "additionalProperties": False
                },
                "additionalProperties": False
            },
            "Note": {"type": "string"}
        },
        "required": [
            "Title of the Regulation", "From", "Subject", "Tags", 
            "Jurisdiction", "Subject Matter", "Date", "Summary", 
            "Analysis", "Relevant Regulations or Legal Measures", 
            "Business Impact", "Conclusion", "Relevant Links", "Note"
        ],
        "additionalProperties": False
    }

    summaries = []
    for email_data in emails_data:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize the following regulatory update:"
                    },
                    {
                        "role": "user",
                        "content": email_data['body']
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "regulatory_summary",
                        "strict": True,
                        "schema": schema
                    }},
                model="gpt-4o-mini-2024-07-18",
                temperature=0.2,
                max_tokens=3500
            )
            summary = chat_completion.choices[0].message.content.strip()
            summaries.append(summary)
        except Exception as e:
            print(f"Error summarizing content: {e}")
            summaries.append("Error summarizing content.")
    return summaries