"""TechNova Support API - FastAPI Application."""

import logging
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional

from .config import get_settings, Settings
from .models import SupportRequest, SupportResponse
from .servicenow_client import (
    create_service_now_incident,
    get_assignment_groups,
    get_categories,
    get_impacts,
    get_urgencies
)
from .slack_client import send_slack_message
from .github_client import create_github_issue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Key Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key provided in the X-API-Key header.
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    settings = get_settings()
    
    # If no API key is configured, allow all requests (development mode)
    if not settings.api_key:
        logger.warning("No API_KEY configured - API is running in open mode")
        return "open-mode"
    
    if not api_key:
        logger.warning("API request missing X-API-Key header")
        raise HTTPException(
            status_code=401,
            detail="Missing API Key. Include 'X-API-Key' header in your request."
        )
    
    if api_key != settings.api_key:
        logger.warning("Invalid API key provided")
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    
    return api_key


# Assignment Group to Slack Channel Mapping
ASSIGNMENT_GROUP_SLACK_CHANNELS = {
    # CLOUD - Cloud Infrastructure Services
    "CLOUD": "#cloud-support",
    
    # DATA - Data & Analytics
    "DATA": "#data-support",
    
    # SECURITY - Cybersecurity Operations
    "SEC": "#security-incidents",
    
    # COLLAB - Collaboration & Productivity
    "COLLAB": "#collab-support",
    
    # FINTECH - Financial Technology
    "FIN": "#fintech-support",
    
    # DEVTOOLS - Developer Tools & Platforms
    "DEVTOOLS": "#devtools-support",
    "DEV": "#devtools-support",
    
    # ITSM - IT Service Management
    "ITSM": "#itsm-support",
    
    # ERP - Enterprise Resource Planning
    "ERP": "#erp-support",
    
    # IOT - IoT & Industrial
    "IOT": "#iot-support",
    
    # General/Fallback
    "GENERAL": "#general-support",
}


def get_slack_channel_for_assignment_group(assignment_group: str) -> Optional[str]:
    """
    Get the appropriate Slack channel for a given assignment group.
    
    Args:
        assignment_group: The ServiceNow assignment group name (e.g., "CLOUD-L1-Support")
        
    Returns:
        The Slack channel to use (e.g., "#cloud-support"), or None to use default
    """
    if not assignment_group:
        return None
    
    # Extract the prefix from the assignment group (e.g., "CLOUD" from "CLOUD-L1-Support")
    assignment_group_upper = assignment_group.upper()
    
    # Check each prefix
    for prefix, channel in ASSIGNMENT_GROUP_SLACK_CHANNELS.items():
        if assignment_group_upper.startswith(prefix):
            return channel
    
    # Return None to use default channel from .env
    return None

# Initialize FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    servers=[
        {
            "url": settings.api_server_url,
            "description": "Production server on IBM Code Engine"
        }
    ]
)

# Define OpenAPI security scheme for documentation
app.openapi_schema = None  # Reset to allow customization

def custom_openapi():
    """Generate custom OpenAPI schema with API key security."""
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=app.servers
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for authenticating requests. Contact TechNova admin for access."
        }
    }
    
    # Apply security globally to all endpoints except health
    for path, methods in openapi_schema["paths"].items():
        if path != "/health":
            for method in methods.values():
                if isinstance(method, dict):
                    method["security"] = [{"ApiKeyAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.api_version}


@app.post("/get_support", response_model=SupportResponse)
async def get_support(
    request: SupportRequest,
    api_key: str = Depends(verify_api_key)
) -> SupportResponse:
    """
    Create a support incident in ServiceNow and send a Slack notification.
    
    This endpoint:
    1. Creates a new incident in ServiceNow with the provided details
    2. Sends a notification to the configured Slack channel
    3. Returns the incident details and status
    
    Args:
        request: SupportRequest containing incident details
        
    Returns:
        SupportResponse with incident number and status
    """
    logger.info(f"Received support request: {request.short_description}")
    
    # Step 1: Create the ServiceNow incident
    snow_result = create_service_now_incident(request)
    
    if not snow_result["success"]:
        logger.error(f"Failed to create ServiceNow incident: {snow_result['error_details']}")
        return SupportResponse(
            success=False,
            incident_number=None,
            incident_sys_id=None,
            slack_message_sent=False,
            error_details=snow_result["error_details"]
        )
    
    # Step 2: Send Slack notification to the appropriate channel based on assignment group
    slack_channel = get_slack_channel_for_assignment_group(request.assignment_group)
    logger.info(f"Sending Slack notification to channel: {slack_channel or 'default'}")
    
    slack_result = send_slack_message(
        channel=slack_channel,
        incident_number=snow_result["incident_number"],
        short_description=request.short_description,
        description=request.description,
        assignment_group=request.assignment_group,
        urgency=request.urgency_value,
        impact=request.impact_value,
        caller=request.caller_username
    )
    
    if not slack_result["success"]:
        logger.warning(f"Failed to send Slack message: {slack_result['error_details']}")
        # Note: We still return success=True since the incident was created
    
    # Step 3: Create GitHub issue if stack trace detected in description
    github_result = {"success": True, "issue_created": False, "issue_url": None, "issue_number": None}
    if request.description:
        github_result = create_github_issue(
            error_message=request.description,
            incident_number=snow_result["incident_number"],
            short_description=request.short_description,
            caller_username=request.caller_username
        )
        if github_result.get("issue_created"):
            logger.info(f"GitHub issue created: {github_result['issue_url']}")
        elif github_result.get("error_details"):
            logger.warning(f"Failed to create GitHub issue: {github_result['error_details']}")
    
    return SupportResponse(
        success=True,
        incident_number=snow_result["incident_number"],
        incident_sys_id=snow_result["incident_sys_id"],
        slack_message_sent=slack_result["success"],
        slack_channel=slack_result.get("channel"),
        github_issue_created=github_result.get("issue_created", False),
        github_issue_url=github_result.get("issue_url"),
        github_issue_number=github_result.get("issue_number"),
        error_details=slack_result.get("error_details") if not slack_result["success"] else github_result.get("error_details")
    )


@app.get("/assignment_groups")
async def list_assignment_groups(api_key: str = Depends(verify_api_key)):
    """
    Get available ServiceNow assignment groups.
    
    Returns:
        list: Available assignment groups
    """
    groups = get_assignment_groups()
    return {"assignment_groups": groups}


@app.get("/categories")
async def list_categories(api_key: str = Depends(verify_api_key)):
    """
    Get available incident categories.
    
    Returns:
        list: Available incident categories
    """
    categories = get_categories()
    return {"categories": categories}


@app.get("/impacts")
async def list_impacts(api_key: str = Depends(verify_api_key)):
    """
    Get available impact values.
    
    Returns:
        list: Available impact values with labels
    """
    impacts = get_impacts()
    return {"impacts": impacts}


@app.get("/urgencies")
async def list_urgencies(api_key: str = Depends(verify_api_key)):
    """
    Get available urgency values.
    
    Returns:
        list: Available urgency values with labels
    """
    urgencies = get_urgencies()
    return {"urgencies": urgencies}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
