"""
Test script for Slack message sending functionality.

This script tests the Slack integration which sends notifications
to the configured Slack channel when incidents are created.

Features tested:
- Slack message formatting with incident details
- Slack API connection using Bot Token
- Channel posting with rich message format

Usage:
    python -m tests.test_slack

Requirements:
    - SLACK_BOT_TOKEN environment variable must be set
    - SLACK_DEFAULT_CHANNEL environment variable must be set
    - Bot must be invited to the target channel

Author: TechNova Solutions
Version: 1.0.0
"""
from api.slack_client import send_slack_message

# Test sending a Slack message with sample incident data
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
