"""Pydantic models for the Support API."""

from typing import Optional
from pydantic import BaseModel, Field


class SupportRequest(BaseModel):
    """Request model for creating a support incident."""
    
    assignment_group: Optional[str] = Field(
        default=None,
        description="The name of the assignment group returned by the tool get_assignment_groups"
    )
    caller_username: Optional[str] = Field(
        default=None,
        description="The caller username is returned by the tool get_system_user"
    )
    description: Optional[str] = Field(
        default=None,
        description="The description for the incident in ServiceNow"
    )
    impact_value: Optional[str] = Field(
        default=None,
        description="The impact_value is returned by the tool get_impacts"
    )
    incident_category: Optional[str] = Field(
        default=None,
        description="The category name, is returned by the tool get_categories"
    )
    short_description: str = Field(
        ...,
        description="A brief summary of the new incident in ServiceNow"
    )
    urgency_value: str = Field(
        ...,
        description="The urgency_value is returned by the tool get_urgencies"
    )


class SupportResponse(BaseModel):
    """Response model for support incident creation."""
    
    success: bool
    incident_number: Optional[str] = None
    incident_sys_id: Optional[str] = None
    slack_message_sent: bool = False
    slack_channel: Optional[str] = Field(
        default=None,
        description="The Slack channel where the notification was sent"
    )
    github_issue_created: bool = False
    github_issue_url: Optional[str] = None
    github_issue_number: Optional[int] = None
    error_details: Optional[dict] = Field(
        default=None,
        description="A unified wrapper to fetch all details about the error"
    )


class ErrorDetails(BaseModel):
    """Error details model."""
    
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    service: Optional[str] = None  # "servicenow" or "slack"
