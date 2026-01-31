"""
Test script for GitHub issue creation functionality.

This script tests the GitHub issue creation feature which automatically
creates GitHub issues when a stack trace is detected in incident descriptions.

Features tested:
- Stack trace detection using regex patterns
- GitHub issue creation via PyGithub API
- Integration with ServiceNow incident numbers

Usage:
    python -m tests.test_github

Requirements:
    - GITHUB_TOKEN environment variable must be set
    - GITHUB_DEFAULT_REPO environment variable must be set

Author: TechNova Solutions
Version: 1.0.0
"""
from api.github_client import contains_stack_trace, create_github_issue

# Sample description containing a Python stack trace for testing
test_desc = """Application crashed on startup with the following error:

Traceback (most recent call last):
  File "app.py", line 42, in main
    result = process_data(input_data)
ValueError: Invalid configuration
"""

# Test stack trace detection
print('Stack trace detected:', contains_stack_trace(test_desc))

# Test GitHub issue creation (only creates if stack trace detected)
result = create_github_issue(test_desc, 'INC0010005', 'Test issue')
print('Result:', result)
