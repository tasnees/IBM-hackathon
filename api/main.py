"""TechNova Support API - FastAPI Application."""

import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

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
async def get_support(request: SupportRequest) -> SupportResponse:
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
    
    # Step 2: Send Slack notification
    slack_result = send_slack_message(
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
        github_issue_created=github_result.get("issue_created", False),
        github_issue_url=github_result.get("issue_url"),
        github_issue_number=github_result.get("issue_number"),
        error_details=slack_result.get("error_details") if not slack_result["success"] else github_result.get("error_details")
    )


@app.get("/assignment_groups")
async def list_assignment_groups():
    """
    Get available ServiceNow assignment groups.
    
    Returns:
        list: Available assignment groups
    """
    groups = get_assignment_groups()
    return {"assignment_groups": groups}


@app.get("/categories")
async def list_categories():
    """
    Get available incident categories.
    
    Returns:
        list: Available incident categories
    """
    categories = get_categories()
    return {"categories": categories}


@app.get("/impacts")
async def list_impacts():
    """
    Get available impact values.
    
    Returns:
        list: Available impact values with labels
    """
    impacts = get_impacts()
    return {"impacts": impacts}


@app.get("/urgencies")
async def list_urgencies():
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
