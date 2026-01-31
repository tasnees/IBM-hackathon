"""GitHub client helper functions."""

import logging
import re
from typing import Optional
from github import Github, GithubException

from .config import get_settings

logger = logging.getLogger(__name__)

# Patterns that indicate a stack trace
STACK_TRACE_PATTERNS = [
    r'Traceback \(most recent call last\)',  # Python
    r'at .+\(.+:\d+\)',  # Java/JavaScript
    r'^\s+at\s+',  # Generic "at" pattern
    r'Exception in thread',  # Java
    r'Error:\s*\n\s+at\s+',  # Node.js
    r'File ".+", line \d+',  # Python file reference
    r'\.py", line \d+',  # Python file
    r'\.java:\d+\)',  # Java file
    r'\.js:\d+:\d+',  # JavaScript file
    r'\.ts:\d+:\d+',  # TypeScript file
    r'Stack trace:',  # Generic
    r'Call stack:',  # Generic
    r'NullPointerException',  # Java
    r'TypeError:|ValueError:|KeyError:|AttributeError:',  # Python exceptions
    r'Caused by:',  # Java chained exceptions
]


def get_github_client() -> Github:
    """Create and return a GitHub client instance."""
    settings = get_settings()
    return Github(settings.github_token)


def contains_stack_trace(error_message: str) -> bool:
    """
    Check if an error message contains a stack trace.
    
    Args:
        error_message: The error message to check
        
    Returns:
        bool: True if a stack trace pattern is found
    """
    if not error_message:
        return False
    
    for pattern in STACK_TRACE_PATTERNS:
        if re.search(pattern, error_message, re.MULTILINE | re.IGNORECASE):
            return True
    
    return False


def create_github_issue(
    error_message: str,
    incident_number: Optional[str] = None,
    short_description: Optional[str] = None,
    product_id: Optional[str] = None,
    caller_username: Optional[str] = None,
    repo_name: Optional[str] = None
) -> dict:
    """
    Create a GitHub issue if the error message includes a stack trace.
    
    Args:
        error_message: The error message/description that may contain a stack trace
        incident_number: Associated ServiceNow incident number
        short_description: Brief summary of the issue
        product_id: The product ID related to this error
        caller_username: Username of the person who reported the issue
        repo_name: Repository name (owner/repo format). If not provided, uses default from config.
        
    Returns:
        dict: Contains success status, issue URL, issue number, and any error details
    """
    result = {
        "success": False,
        "issue_created": False,
        "issue_url": None,
        "issue_number": None,
        "error_details": None,
        "stack_trace_detected": False
    }
    
    # Check if error message contains a stack trace
    if not contains_stack_trace(error_message):
        logger.info("No stack trace detected in error message, skipping GitHub issue creation")
        result["success"] = True  # Not an error, just no action needed
        return result
    
    result["stack_trace_detected"] = True
    logger.info("Stack trace detected, creating GitHub issue")
    
    try:
        settings = get_settings()
        client = get_github_client()
        
        # Use provided repo or default from config
        target_repo = repo_name or settings.github_default_repo
        
        if not target_repo:
            result["error_details"] = {
                "error_code": "GITHUB_NO_REPO",
                "error_message": "No repository specified and no default configured",
                "service": "github"
            }
            return result
        
        repo = client.get_repo(target_repo)
        
        # Build issue title
        title_parts = []
        if incident_number:
            title_parts.append(f"[{incident_number}]")
        if product_id:
            title_parts.append(f"[{product_id}]")
        title_parts.append(short_description or "Error with stack trace detected")
        
        issue_title = " ".join(title_parts)
        
        # Build issue body
        issue_body = build_issue_body(
            error_message=error_message,
            incident_number=incident_number,
            short_description=short_description,
            product_id=product_id,
            caller_username=caller_username
        )
        
        # Create labels
        labels = ["bug", "auto-generated"]
        if product_id:
            labels.append(f"product:{product_id}")
        
        # Try to use existing labels, skip if they don't exist
        existing_labels = []
        for label in labels:
            try:
                repo.get_label(label)
                existing_labels.append(label)
            except GithubException:
                logger.warning(f"Label '{label}' does not exist in repo, skipping")
        
        # Create the issue
        issue = repo.create_issue(
            title=issue_title,
            body=issue_body,
            labels=existing_labels if existing_labels else None
        )
        
        result["success"] = True
        result["issue_created"] = True
        result["issue_url"] = issue.html_url
        result["issue_number"] = issue.number
        
        logger.info(f"Successfully created GitHub issue #{issue.number}: {issue.html_url}")
        
    except GithubException as e:
        logger.error(f"GitHub API error: {str(e)}")
        result["error_details"] = {
            "error_code": "GITHUB_API_ERROR",
            "error_message": str(e),
            "service": "github"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error creating GitHub issue: {str(e)}")
        result["error_details"] = {
            "error_code": "GITHUB_UNEXPECTED_ERROR",
            "error_message": str(e),
            "service": "github"
        }
    
    return result


def build_issue_body(
    error_message: str,
    incident_number: Optional[str] = None,
    short_description: Optional[str] = None,
    product_id: Optional[str] = None,
    caller_username: Optional[str] = None
) -> str:
    """
    Build the GitHub issue body with formatted content.
    
    Args:
        error_message: The error message containing the stack trace
        incident_number: Associated ServiceNow incident number
        short_description: Brief summary of the issue
        product_id: The product ID related to this error
        caller_username: Username of the person who reported the issue
        
    Returns:
        str: Formatted issue body in Markdown
    """
    body_parts = [
        "## Auto-Generated Issue from Support Incident",
        "",
        "This issue was automatically created because a stack trace was detected in a support incident.",
        ""
    ]
    
    # Add metadata section
    body_parts.append("### Incident Details")
    body_parts.append("")
    body_parts.append("| Field | Value |")
    body_parts.append("|-------|-------|")
    
    if incident_number:
        body_parts.append(f"| ServiceNow Incident | {incident_number} |")
    if product_id:
        body_parts.append(f"| Product ID | {product_id} |")
    if caller_username:
        body_parts.append(f"| Reported By | {caller_username} |")
    if short_description:
        body_parts.append(f"| Summary | {short_description} |")
    
    body_parts.append("")
    
    # Add error message / stack trace
    body_parts.append("### Error Message / Stack Trace")
    body_parts.append("")
    body_parts.append("```")
    body_parts.append(error_message)
    body_parts.append("```")
    body_parts.append("")
    
    # Add action items
    body_parts.append("### Action Items")
    body_parts.append("")
    body_parts.append("- [ ] Investigate root cause")
    body_parts.append("- [ ] Implement fix")
    body_parts.append("- [ ] Add test coverage")
    body_parts.append("- [ ] Update incident with resolution")
    body_parts.append("")
    
    # Add footer
    body_parts.append("---")
    body_parts.append("*This issue was auto-generated by the TechNova Support API*")
    
    return "\n".join(body_parts)
