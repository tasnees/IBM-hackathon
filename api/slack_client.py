"""Slack client helper functions."""

import logging
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .config import get_settings

logger = logging.getLogger(__name__)


def get_slack_client() -> WebClient:
    """Create and return a Slack WebClient instance."""
    settings = get_settings()
    return WebClient(token=settings.slack_bot_token)


def create_channel(channel_name: str, is_private: bool = False) -> dict:
    """
    Create a new Slack channel.
    
    Args:
        channel_name: Name of the channel to create (without # prefix)
        is_private: Whether to create a private channel
        
    Returns:
        dict: Contains success status, channel_id, and any error details
    """
    result = {
        "success": False,
        "channel_id": None,
        "error_details": None
    }
    
    # Remove # prefix if present
    channel_name = channel_name.lstrip('#')
    
    try:
        client = get_slack_client()
        response = client.conversations_create(
            name=channel_name,
            is_private=is_private
        )
        
        result["success"] = response["ok"]
        result["channel_id"] = response["channel"]["id"]
        logger.info(f"Successfully created Slack channel: {channel_name}")
        
    except SlackApiError as e:
        error_msg = e.response['error']
        logger.error(f"Slack API error creating channel: {error_msg}")
        result["error_details"] = {
            "error_code": "SLACK_API_ERROR",
            "error_message": error_msg,
            "service": "slack"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error creating Slack channel: {str(e)}")
        result["error_details"] = {
            "error_code": "SLACK_UNEXPECTED_ERROR",
            "error_message": str(e),
            "service": "slack"
        }
    
    return result


def send_slack_message(
    channel: Optional[str] = None,
    incident_number: Optional[str] = None,
    short_description: str = "",
    description: Optional[str] = None,
    assignment_group: Optional[str] = None,
    urgency: Optional[str] = None,
    impact: Optional[str] = None,
    caller: Optional[str] = None
) -> dict:
    """
    Send a Slack notification about a new incident.
    
    Args:
        channel: Slack channel to post to (defaults to configured channel)
        incident_number: The ServiceNow incident number
        short_description: Brief summary of the incident
        description: Detailed description of the incident
        assignment_group: The assigned support group
        urgency: Urgency level
        impact: Impact level
        caller: Username of the person who reported the incident
        
    Returns:
        dict: Contains success status and any error details
    """
    settings = get_settings()
    result = {
        "success": False,
        "error_details": None
    }
    
    # Use default channel if not specified
    if not channel:
        channel = settings.slack_default_channel
    
    # Ensure channel has # prefix
    if channel and not channel.startswith('#'):
        channel = f'#{channel}'
    
    try:
        client = get_slack_client()
        
        # Build the message blocks for rich formatting
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎫 New Incident Created: {incident_number or 'N/A'}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{short_description}*"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add incident details section
        fields = []
        
        if assignment_group:
            fields.append({
                "type": "mrkdwn",
                "text": f"*Assignment Group:*\n{assignment_group}"
            })
            
        if urgency:
            urgency_emoji = get_urgency_emoji(urgency)
            fields.append({
                "type": "mrkdwn",
                "text": f"*Urgency:*\n{urgency_emoji} {urgency}"
            })
            
        if impact:
            fields.append({
                "type": "mrkdwn",
                "text": f"*Impact:*\n{impact}"
            })
            
        if caller:
            fields.append({
                "type": "mrkdwn",
                "text": f"*Reported By:*\n{caller}"
            })
        
        if fields:
            blocks.append({
                "type": "section",
                "fields": fields
            })
        
        # Add description if provided
        if description:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{description[:500]}{'...' if len(description) > 500 else ''}"
                }
            })
        
        # Add link to ServiceNow (if incident number exists)
        if incident_number:
            servicenow_url = f"https://{settings.servicenow_instance}/nav_to.do?uri=incident.do?sysparm_query=number={incident_number}"
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View in ServiceNow",
                            "emoji": True
                        },
                        "url": servicenow_url,
                        "style": "primary"
                    }
                ]
            })
        
        # Send the message
        try:
            response = client.chat_postMessage(
                channel=channel,
                text=f"New Incident: {incident_number} - {short_description}",  # Fallback text
                blocks=blocks
            )
            result["success"] = response["ok"]
            logger.info(f"Successfully sent Slack message to {channel}")
            
        except SlackApiError as e:
            # If channel not found, try to create it
            if e.response['error'] == 'channel_not_found':
                logger.info(f"Channel {channel} not found, attempting to create it...")
                create_result = create_channel(channel)
                
                if create_result["success"]:
                    # Retry sending the message to the newly created channel
                    response = client.chat_postMessage(
                        channel=channel,
                        text=f"New Incident: {incident_number} - {short_description}",
                        blocks=blocks
                    )
                    result["success"] = response["ok"]
                    logger.info(f"Successfully sent Slack message to newly created channel {channel}")
                else:
                    raise e
            else:
                raise e
        
    except SlackApiError as e:
        logger.error(f"Slack API error: {e.response['error']}")
        result["error_details"] = {
            "error_code": "SLACK_API_ERROR",
            "error_message": e.response['error'],
            "service": "slack"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error sending Slack message: {str(e)}")
        result["error_details"] = {
            "error_code": "SLACK_UNEXPECTED_ERROR",
            "error_message": str(e),
            "service": "slack"
        }
    
    return result


def get_urgency_emoji(urgency: str) -> str:
    """Return an emoji based on urgency level."""
    urgency_lower = urgency.lower()
    
    if "critical" in urgency_lower or urgency == "1":
        return "🔴"
    elif "high" in urgency_lower or urgency == "2":
        return "🟠"
    elif "medium" in urgency_lower or urgency == "3":
        return "🟡"
    else:
        return "🟢"
