"""ServiceNow client helper functions."""

import logging
from typing import Optional
from pysnow import Client
from pysnow.exceptions import PysnowException

from .config import get_settings
from .models import SupportRequest

logger = logging.getLogger(__name__)


def get_servicenow_client() -> Client:
    """Create and return a ServiceNow client instance."""
    settings = get_settings()
    
    client = Client(
        instance=settings.servicenow_instance,
        user=settings.servicenow_username,
        password=settings.servicenow_password
    )
    
    return client


def create_service_now_incident(request: SupportRequest) -> dict:
    """
    Create a new incident in ServiceNow.
    
    Args:
        request: SupportRequest containing incident details
        
    Returns:
        dict: Contains success status, incident number, sys_id, and any error details
    """
    result = {
        "success": False,
        "incident_number": None,
        "incident_sys_id": None,
        "error_details": None
    }
    
    try:
        client = get_servicenow_client()
        
        # Get the incident table resource
        incident_table = client.resource(api_path='/table/incident')
        
        # Build the incident payload
        incident_data = {
            "short_description": request.short_description,
            "urgency": request.urgency_value,
        }
        
        # Add optional fields if provided
        if request.description:
            incident_data["description"] = request.description
            
        if request.assignment_group:
            incident_data["assignment_group"] = request.assignment_group
            
        if request.caller_username:
            incident_data["caller_id"] = request.caller_username
            
        if request.impact_value:
            incident_data["impact"] = request.impact_value
            
        if request.incident_category:
            incident_data["category"] = request.incident_category
        
        logger.info(f"Creating ServiceNow incident with data: {incident_data}")
        
        # Create the incident
        response = incident_table.create(payload=incident_data)
        
        # Extract incident details from response
        incident_record = response.one()
        
        result["success"] = True
        result["incident_number"] = incident_record.get("number")
        result["incident_sys_id"] = incident_record.get("sys_id")
        
        logger.info(f"Successfully created incident: {result['incident_number']}")
        
    except PysnowException as e:
        logger.error(f"ServiceNow API error: {str(e)}")
        result["error_details"] = {
            "error_code": "SERVICENOW_API_ERROR",
            "error_message": str(e),
            "service": "servicenow"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error creating incident: {str(e)}")
        result["error_details"] = {
            "error_code": "SERVICENOW_UNEXPECTED_ERROR",
            "error_message": str(e),
            "service": "servicenow"
        }
    
    return result


def get_assignment_groups() -> list:
    """
    Retrieve available assignment groups from ServiceNow.
    
    Returns:
        list: List of assignment group names
    """
    try:
        client = get_servicenow_client()
        group_table = client.resource(api_path='/table/sys_user_group')
        
        response = group_table.get(query={}, fields=['name', 'sys_id'])
        groups = [{"name": record.get("name"), "sys_id": record.get("sys_id")} 
                  for record in response.all()]
        
        return groups
        
    except Exception as e:
        logger.error(f"Error fetching assignment groups: {str(e)}")
        return []


def get_categories() -> list:
    """
    Retrieve available incident categories from ServiceNow.
    
    Returns:
        list: List of category names
    """
    # Common ServiceNow incident categories
    return [
        "Access / Login",
        "Performance",
        "Error / Bug", 
        "Data Issue",
        "Configuration",
        "Outage",
        "How-To / Question",
        "Enhancement Request"
    ]


def get_impacts() -> list:
    """
    Retrieve available impact values from ServiceNow.
    
    Returns:
        list: List of impact values with labels
    """
    return [
        {"value": "1", "label": "1 - Enterprise"},
        {"value": "2", "label": "2 - Department"},
        {"value": "3", "label": "3 - Multiple Users"},
        {"value": "4", "label": "4 - Single User"}
    ]


def get_urgencies() -> list:
    """
    Retrieve available urgency values from ServiceNow.
    
    Returns:
        list: List of urgency values with labels
    """
    return [
        {"value": "1", "label": "1 - Critical"},
        {"value": "2", "label": "2 - High"},
        {"value": "3", "label": "3 - Medium"},
        {"value": "4", "label": "4 - Low"}
    ]
