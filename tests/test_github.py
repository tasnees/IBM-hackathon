"""Test script for GitHub issue creation."""
from api.github_client import contains_stack_trace, create_github_issue

test_desc = """Application crashed on startup with the following error:

Traceback (most recent call last):
  File "app.py", line 42, in main
    result = process_data(input_data)
ValueError: Invalid configuration
"""

print('Stack trace detected:', contains_stack_trace(test_desc))
result = create_github_issue(test_desc, 'INC0010005', 'Test issue')
print('Result:', result)
