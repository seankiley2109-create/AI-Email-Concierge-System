def pytest_addoption(parser):
    parser.addoption(
        "--test_fields",
        action="store",
        default="all",
        help="Comma-separated fields to test: support_team,sentiment,urgency,draft"
    )