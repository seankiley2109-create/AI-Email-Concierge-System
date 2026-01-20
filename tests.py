import pytest
import csv
import asyncio
from main import ottomation

CSV_PATH = "full_customer_email_samples.csv"

def load_emails_from_csv(path):
    emails = []
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            email_text = f"Subject: {row['subject']}\n\n{row['body']}"
            emails.append({
                "email_text": email_text,
                "support_team": row.get("support-group", "").strip(),
                "sentiment": row.get("sentiment", "").strip(),
                "urgency": row.get("urgency", "").strip()
            })
    return emails

@pytest.mark.asyncio
@pytest.mark.parametrize("email_data", load_emails_from_csv(CSV_PATH))
async def test_ottomation_with_csv_data(email_data, request):
    test_fields = request.config.getoption("--test_fields").split(",")

    result = await ottomation(email_data["email_text"], "test@example.com")

    if "support_team" in test_fields or "all" in test_fields:
        assert result["support_team"].lower() == email_data["support_team"].lower()

    if "sentiment" in test_fields or "all" in test_fields:
        assert result["sentiment_category"].lower() == email_data["sentiment"].lower()

    if "urgency" in test_fields or "all" in test_fields:
        assert isinstance(result["urgency"], int)
        assert int(email_data["urgency"]) == result["urgency"]

    if "draft" in test_fields or "all" in test_fields:
        assert len(result["draft_reply"]) > 0