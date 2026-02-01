"""
Script to create the TechNova support Slack channels.

This script creates all the department-specific Slack channels needed for
routing support notifications based on assignment groups.

Usage:
    python -m tests.create_slack_channels
    python -m tests.create_slack_channels --dry-run
"""

import os
import sys
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

# Channels to create (without the # prefix)
SUPPORT_CHANNELS = [
    {"name": "cloud-support", "description": "Cloud Infrastructure support notifications"},
    {"name": "data-support", "description": "Data & Analytics support notifications"},
    {"name": "security-incidents", "description": "Security team incident notifications"},
    {"name": "collab-support", "description": "Collaboration & Productivity support notifications"},
    {"name": "fintech-support", "description": "Financial Technology support notifications"},
    {"name": "devtools-support", "description": "Developer Tools support notifications"},
    {"name": "itsm-support", "description": "IT Service Management support notifications"},
    {"name": "erp-support", "description": "ERP support notifications"},
    {"name": "iot-support", "description": "IoT & Industrial support notifications"},
    {"name": "general-support", "description": "General support notifications (fallback)"},
]


def create_slack_channels(dry_run: bool = False):
    """Create all TechNova support Slack channels."""
    print("=" * 60)
    print("TechNova Solutions - Slack Channel Setup")
    print("=" * 60)
    print()
    
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("❌ Error: SLACK_BOT_TOKEN not found in environment")
        return
    
    client = WebClient(token=token)
    
    # Get existing channels
    print("🔍 Checking existing channels...")
    try:
        response = client.conversations_list(types="public_channel,private_channel")
        existing_channels = {ch["name"] for ch in response["channels"]}
        print(f"  Found {len(existing_channels)} existing channels")
    except SlackApiError as e:
        print(f"❌ Error listing channels: {e.response['error']}")
        return
    
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()
    
    created = 0
    skipped = 0
    failed = 0
    
    for channel_info in SUPPORT_CHANNELS:
        channel_name = channel_info["name"]
        description = channel_info["description"]
        
        if channel_name in existing_channels:
            print(f"  ⏭️  #{channel_name} already exists, skipping...")
            skipped += 1
            continue
        
        if dry_run:
            print(f"  Would create: #{channel_name}")
            print(f"    Description: {description}")
            created += 1
            continue
        
        try:
            # Create the channel
            response = client.conversations_create(
                name=channel_name,
                is_private=False
            )
            channel_id = response["channel"]["id"]
            
            # Set the channel topic/purpose
            try:
                client.conversations_setTopic(
                    channel=channel_id,
                    topic=description
                )
                client.conversations_setPurpose(
                    channel=channel_id,
                    purpose=f"TechNova Support - {description}"
                )
            except SlackApiError:
                pass  # Topic/purpose setting is optional
            
            print(f"  ✅ Created #{channel_name} (ID: {channel_id})")
            created += 1
            
        except SlackApiError as e:
            error = e.response.get("error", str(e))
            print(f"  ❌ Failed to create #{channel_name}: {error}")
            failed += 1
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  ✅ Created: {created}")
    print(f"  ⏭️  Skipped (already exist): {skipped}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Total: {len(SUPPORT_CHANNELS)}")


def list_channels():
    """List all existing Slack channels."""
    print("=" * 60)
    print("Existing Slack Channels")
    print("=" * 60)
    print()
    
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("❌ Error: SLACK_BOT_TOKEN not found in environment")
        return
    
    client = WebClient(token=token)
    
    try:
        response = client.conversations_list(types="public_channel,private_channel")
        channels = response["channels"]
        
        print(f"Found {len(channels)} channels:")
        print()
        for ch in sorted(channels, key=lambda x: x["name"]):
            member_count = ch.get("num_members", "?")
            print(f"  #{ch['name']:30} ({member_count} members)")
            
    except SlackApiError as e:
        print(f"❌ Error: {e.response['error']}")


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_channels()
    elif "--dry-run" in sys.argv:
        create_slack_channels(dry_run=True)
    else:
        create_slack_channels(dry_run=False)
