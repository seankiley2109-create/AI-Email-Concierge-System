# Test only support_team
pytest tests.py --test_fields=support_team

# Test support_team and sentiment
pytest tests.py --test_fields=support_team,sentiment

# Test everything (default)
pytest tests.py --test_fields=all

# Test Fields
all
support_team 
sentiment
urgency
draft 