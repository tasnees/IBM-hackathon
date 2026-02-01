"""
Quick script to create Slack channels directly without listing first.
"""

import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

CHANNELS = [
    "cloud-support",
    "data-support",
    "security-incidents",
    "collab-support",
    "fintech-support",
    "devtools-support",
    "itsm-support",
    "erp-support",
    "iot-support",
    "general-support",
]

token = os.getenv("SLACK_BOT_TOKEN")
print(f"Token starts with: {token[:20]}..." if token else "No token found!")

client = WebClient(token=token)

print("\nCreating channels...\n")

for name in CHANNELS:
    try:
        response = client.conversations_create(name=name, is_private=False)
        channel_id = response["channel"]["id"]
        print(f"✅ Created #{name} (ID: {channel_id})")
    except SlackApiError as e:
        error = e.response.get("error", str(e))
        if error == "name_taken":
            print(f"⏭️  #{name} already exists")
        elif error == "missing_scope":
            print(f"❌ #{name} - Missing scope: {e.response.get('needed', 'channels:manage')}")
        else:
            print(f"❌ #{name} - Error: {error}")

print("\nDone!")
