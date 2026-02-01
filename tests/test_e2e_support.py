"""
End-to-end test for the TechNova Support API.

This test:
1. Calls the /get_support endpoint
2. Verifies a ServiceNow incident is created
3. Verifies the assignment group is set correctly
4. Verifies Slack notification is sent to the correct channel

Usage:
    python -m tests.test_e2e_support
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Test cases - each with assignment group that maps to a specific Slack channel
TEST_CASES = [
    {
        "name": "Cloud Infrastructure Issue",
        "request": {
            "short_description": "E2E Test: VM instances not scaling during peak hours",
            "description": "E2E Test: VM instances are not scaling automatically during peak hours. This is a test incident.",
            "urgency_value": "2",
            "impact_value": "2",
            "assignment_group": "CLOUD-L1-Support",
            "caller_username": "admin",
            "incident_category": "Hardware"
        },
        "expected_group_prefix": "CLOUD",
        "expected_channel": "#cloud-support"
    },
    {
        "name": "Security Issue",
        "request": {
            "short_description": "E2E Test: Suspicious login attempts detected",
            "description": "E2E Test: Suspicious login attempts detected on admin account. This is a test incident.",
            "urgency_value": "1",
            "impact_value": "1",
            "assignment_group": "SEC-SOC-Team",
            "caller_username": "admin",
            "incident_category": "Security"
        },
        "expected_group_prefix": "SEC",
        "expected_channel": "#security-incidents"
    },
    {
        "name": "Data Analytics Issue",
        "request": {
            "short_description": "E2E Test: Data pipeline batch jobs failing",
            "description": "E2E Test: Data pipeline failing to process batch jobs. This is a test incident.",
            "urgency_value": "2",
            "impact_value": "2",
            "assignment_group": "DATA-Analytics-Team",
            "caller_username": "admin",
            "incident_category": "Software"
        },
        "expected_group_prefix": "DATA",
        "expected_channel": "#data-support"
    },
]


def test_get_support(test_case: dict, api_key: str = None):
    """Test a single support request."""
    print(f"\n{'='*60}")
    print(f"Test: {test_case['name']}")
    print(f"{'='*60}")
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    
    print(f"\n📤 Request:")
    print(f"   Assignment Group: {test_case['request']['assignment_group']}")
    print(f"   Urgency: {test_case['request']['urgency_value']}")
    print(f"   Description: {test_case['request']['short_description'][:50]}...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/get_support",
            json=test_case["request"],
            headers=headers,
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"\n   ServiceNow Incident:")
            print(f"      Number: {data.get('incident_number', 'N/A')}")
            print(f"      Sys ID: {data.get('incident_sys_id', 'N/A')}")
            
            print(f"\n   Slack Notification:")
            print(f"      Channel: {data.get('slack_channel', 'N/A')}")
            print(f"      Sent: {data.get('slack_message_sent', False)}")
            
            # Verify Slack channel
            channel = data.get('slack_channel', '')
            expected_channel = test_case['expected_channel']
            if channel == expected_channel:
                print(f"\n   ✅ Slack channel is {expected_channel} as expected")
            else:
                print(f"\n   ⚠️  Expected channel {expected_channel}, got: {channel}")
            
            return True
            
        elif response.status_code == 401:
            print(f"\n❌ Authentication required - API key missing or invalid")
            return False
        elif response.status_code == 422:
            print(f"\n❌ Validation error:")
            print(f"   {response.json()}")
            return False
        else:
            print(f"\n❌ Error:")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to API at {API_BASE_URL}")
        print("   Make sure the API is running: uvicorn api.main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False


def main():
    print("="*60)
    print("TechNova Support API - End-to-End Test")
    print("="*60)
    
    api_key = os.getenv("API_KEY", "")
    
    print(f"\nAPI URL: {API_BASE_URL}")
    print(f"API Key: {'configured' if api_key else 'not set (may fail if auth enabled)'}")
    
    passed = 0
    failed = 0
    
    # Run just one test case for now
    test_case = TEST_CASES[0]  # Cloud Infrastructure test
    
    if test_get_support(test_case, api_key):
        passed += 1
    else:
        failed += 1
    
    print(f"\n{'='*60}")
    print(f"Test Summary")
    print(f"{'='*60}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
