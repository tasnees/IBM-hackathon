"""Test script for Slack message sending."""
from api.slack_client import send_slack_message

result = send_slack_message(
    incident_number='INC0010005',
    short_description='Test incident from API',
    description='This is a test message to verify Slack integration is working.',
    assignment_group='DevOps Team',
    urgency='Medium',
    impact='Medium',
    caller='test_user'
)
print('Result:', result)
