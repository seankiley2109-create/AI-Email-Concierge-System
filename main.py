from google import genai
from google.cloud import storage
from google.cloud import language_v2
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree
import datetime
import os
import json
import uuid
import re
from redaction import redact
from classification import classify_email, classification_prompt
from draft import create_draft_reply
from sentiment import analyze_sentiment
from urgency import define_urgency
import asyncio
import csv

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = ""
os.environ["LANGSMITH_PROJECT"] = "Project-Southafrica"

CSV_PATH = "full_customer_email_samples.csv"
BUCKET_NAME = 'hackathon-team2-bucket'

@traceable
async def ottomation(original_email_text: str, 
                    email_address: str) -> {}:
    """
    Orchestrates a comprehensive email processing workflow, from redaction and
    classification to sentiment analysis, urgency assessment, and draft reply generation.

    This asynchronous function integrates several specialized sub-functions to
    automate the initial handling of customer emails. It takes an original email
    and the sender's email address, processes the email content through various
    AI and rule-based steps, and compiles all generated insights into a structured
    dictionary.

    The workflow includes:
    1.  **Redaction:** Hides sensitive information from the original email.
    2.  **Classification:** Determines the primary support team/category for the email.
    3.  **Sentiment Analysis:** Evaluates the overall sentiment (e.g., happy, unhappy)
        and magnitude of the email content.
    4.  **Urgency Definition:** Calculates an urgency score based on the email's category
        and sentiment.
    5.  **Draft Reply Creation:** Generates a brand-aligned, PII-free draft response.
    6.  **Timestamping:** Records when the processing occurred.

    Args:
        original_email_text (str): The complete, raw content of the customer's email.
        email_address (str): The email address of the sender.

    Returns:
        dict: A dictionary containing all the processed information and insights
              derived from the email. The dictionary includes:
              - `timestamp` (str): The date and time of processing (dd/mm/YYYY HH:MM).
              - `email_address` (str): The sender's email address.
              - `subject` (str): Subject retrieved from the first line in the redacted email.
              - `original_email_text` (str): The original, unredacted email content.
              - `redacted_email_text` (str): The email content after PII redaction.
              - `support_team` (str): The classified support team or category.
              - `sentiment_category` (str): The categorized sentiment (e.g., "Happy", "Unhappy").
              - `sentiment_score` (float): The numerical sentiment score (-1.0 to 1.0).
              - `sentiment_magnitude` (float): The numerical sentiment magnitude.
              - `urgency` (int): The calculated urgency score for the email.
              - `draft_reply` (str): The AI-generated draft response.
              - `answered` (bool): A flag indicating if the email has been answered (initially False).
    """
    current_run = get_current_run_tree()

    # Access the trace_id and run_id
    trace_id = current_run.trace_id
   
    redacted_email_text = redact(original_email_text)
    support_team = await classify_email(redacted_email_text, classification_prompt) 
    sentiment = analyze_sentiment(redacted_email_text)
    urgency = define_urgency(support_team, str(sentiment["sentiment_category"]))
    draft_reply = await create_draft_reply(redacted_email_text)

    ### Getting the Timestamp of now
    now = datetime.datetime.now()
    formatted_date = now.strftime("%d/%m/%Y")
    formatted_time = now.strftime("%H:%M")

    ### Getting the subject from the subject line
    match = re.search(r"Subject:\s*(.*?)(?=\n|$)", redacted_email_text, re.IGNORECASE)
    if match:
        # If a subject is found, strip any leading/trailing whitespace
        subject = match.group(1).strip()

    result = {
        "timestamp": f"{formatted_date} {formatted_time}",
        "email_address": email_address,
        "subject": subject,
        "original_email_text": original_email_text,
        "redacted_email_text": redacted_email_text,
        "support_team": support_team,
        "sentiment_category": sentiment["sentiment_category"],
        "sentiment_score": sentiment["score"],
        "sentiment_magnitude": sentiment["magnitude"],
        "urgency": urgency,
        "draft_reply": draft_reply,
        "answered": False,
        "trace_id": str(trace_id)
    }
    return result


def load_emails_from_csv(file_path):
    emails = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subject = row["subject"].strip()
            body = row["body"].strip()
            full_email = f"Subject: {subject}\n\n{body}"
            # ⬇ Return both full_email and subject as a tuple
            emails.append((full_email, subject))
    return emails


def convert_to_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def upload_data_to_gcs(bucket_name: str, file_name: str, data: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(data)
    print(f"Data uploaded to {bucket_name}/{file_name}")


async def main():
    emails = load_emails_from_csv(CSV_PATH)
        
    results = []
    for full_email_text, subject in emails:
        fake_email = f"{uuid.uuid4().hex}@example.com"
        result = await ottomation(full_email_text, fake_email)
        results.append(result)
    
    json_data = convert_to_json(results)
    upload_data_to_gcs(BUCKET_NAME, "all_customer_support_analysis.json", json_data)


if __name__ == "__main__":
    asyncio.run(main())







