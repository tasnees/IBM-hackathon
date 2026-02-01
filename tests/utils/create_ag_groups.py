"""
Script to programmatically create all TechNova Solutions assignment groups in ServiceNow.

This script creates the assignment groups defined in the knowledge-base/servicenow-assignment-groups.txt file.

Usage:
    python -m tests.create_ag_groups

Environment variables required:
    SERVICENOW_INSTANCE - Your ServiceNow instance name (e.g., dev314739)
    SERVICENOW_USERNAME - ServiceNow admin username
    SERVICENOW_PASSWORD - ServiceNow admin password
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import pysnow

# Load environment variables
load_dotenv()


# All TechNova Solutions Assignment Groups
ASSIGNMENT_GROUPS = [
    # CLOUD - Cloud Infrastructure Services
    {"name": "CLOUD-L1-Support", "description": "Cloud Infrastructure L1 Support - Initial triage for all CLOUD products", "manager": "sarah.chen@technovasolutions.com", "email": "cloud-oncall@technovasolutions.com"},
    {"name": "CLOUD-L2-Engineering", "description": "Cloud Infrastructure L2 Engineering - Technical issues for CLOUD-001 to CLOUD-010", "manager": "sarah.chen@technovasolutions.com", "email": "cloud-oncall@technovasolutions.com"},
    {"name": "CLOUD-L3-Architecture", "description": "Cloud Infrastructure L3 Architecture - Complex infrastructure issues", "manager": "sarah.chen@technovasolutions.com", "email": "cloud-oncall@technovasolutions.com"},
    {"name": "CLOUD-Storage-Team", "description": "Cloud Storage Team - CLOUD-003, CLOUD-004, CLOUD-007", "manager": "sarah.chen@technovasolutions.com", "email": "cloud-oncall@technovasolutions.com"},
    {"name": "CLOUD-Network-Team", "description": "Cloud Network Team - CLOUD-005, CLOUD-006, CLOUD-008", "manager": "sarah.chen@technovasolutions.com", "email": "cloud-oncall@technovasolutions.com"},
    {"name": "CLOUD-Compute-Team", "description": "Cloud Compute Team - CLOUD-001, CLOUD-002, CLOUD-009, CLOUD-010", "manager": "sarah.chen@technovasolutions.com", "email": "cloud-oncall@technovasolutions.com"},
    
    # DATA - Data & Analytics
    {"name": "DATA-L1-Support", "description": "Data & Analytics L1 Support - Initial triage for all DATA products", "manager": "marcus.johnson@technovasolutions.com", "email": "data-oncall@technovasolutions.com"},
    {"name": "DATA-L2-Engineering", "description": "Data & Analytics L2 Engineering - Technical issues for DATA-001 to DATA-010", "manager": "marcus.johnson@technovasolutions.com", "email": "data-oncall@technovasolutions.com"},
    {"name": "DATA-L3-Architecture", "description": "Data & Analytics L3 Architecture - Complex data platform issues", "manager": "marcus.johnson@technovasolutions.com", "email": "data-oncall@technovasolutions.com"},
    {"name": "DATA-Warehouse-Team", "description": "Data Warehouse Team - DATA-001, DATA-006, DATA-007", "manager": "marcus.johnson@technovasolutions.com", "email": "data-oncall@technovasolutions.com"},
    {"name": "DATA-Analytics-Team", "description": "Data Analytics Team - DATA-002, DATA-009, DATA-010", "manager": "marcus.johnson@technovasolutions.com", "email": "data-oncall@technovasolutions.com"},
    {"name": "DATA-Pipeline-Team", "description": "Data Pipeline Team - DATA-003, DATA-004, DATA-005", "manager": "marcus.johnson@technovasolutions.com", "email": "data-oncall@technovasolutions.com"},
    {"name": "DATA-Governance-Team", "description": "Data Governance Team - DATA-008", "manager": "marcus.johnson@technovasolutions.com", "email": "data-oncall@technovasolutions.com"},
    
    # SECURITY - Cybersecurity Operations
    {"name": "SEC-L1-Support", "description": "Security L1 Support - Initial triage for all SEC products", "manager": "aisha.patel@technovasolutions.com", "email": "security-oncall@technovasolutions.com"},
    {"name": "SEC-L2-Engineering", "description": "Security L2 Engineering - Technical issues for SEC-001 to SEC-010", "manager": "aisha.patel@technovasolutions.com", "email": "security-oncall@technovasolutions.com"},
    {"name": "SEC-L3-Architecture", "description": "Security L3 Architecture - Critical security incidents", "manager": "aisha.patel@technovasolutions.com", "email": "security-oncall@technovasolutions.com"},
    {"name": "SEC-Endpoint-Team", "description": "Security Endpoint Team - SEC-001, SEC-008", "manager": "aisha.patel@technovasolutions.com", "email": "security-oncall@technovasolutions.com"},
    {"name": "SEC-Network-Team", "description": "Security Network Team - SEC-002, SEC-007, SEC-010", "manager": "aisha.patel@technovasolutions.com", "email": "security-oncall@technovasolutions.com"},
    {"name": "SEC-Identity-Team", "description": "Security Identity Team - SEC-003, SEC-004, SEC-009", "manager": "aisha.patel@technovasolutions.com", "email": "security-oncall@technovasolutions.com"},
    {"name": "SEC-SOC-Team", "description": "Security Operations Center - SEC-005, SEC-006", "manager": "aisha.patel@technovasolutions.com", "email": "soc@technovasolutions.com"},
    
    # COLLAB - Collaboration & Productivity
    {"name": "COLLAB-L1-Support", "description": "Collaboration L1 Support - Initial triage for all COLLAB products", "manager": "jennifer.martinez@technovasolutions.com", "email": "collab-oncall@technovasolutions.com"},
    {"name": "COLLAB-L2-Engineering", "description": "Collaboration L2 Engineering - Technical issues for COLLAB-001 to COLLAB-010", "manager": "jennifer.martinez@technovasolutions.com", "email": "collab-oncall@technovasolutions.com"},
    {"name": "COLLAB-L3-Architecture", "description": "Collaboration L3 Architecture - Complex collaboration issues", "manager": "jennifer.martinez@technovasolutions.com", "email": "collab-oncall@technovasolutions.com"},
    {"name": "COLLAB-Communication-Team", "description": "Collaboration Communication Team - COLLAB-001, COLLAB-002, COLLAB-003", "manager": "jennifer.martinez@technovasolutions.com", "email": "collab-oncall@technovasolutions.com"},
    {"name": "COLLAB-Productivity-Team", "description": "Collaboration Productivity Team - COLLAB-004, COLLAB-005, COLLAB-006", "manager": "jennifer.martinez@technovasolutions.com", "email": "collab-oncall@technovasolutions.com"},
    {"name": "COLLAB-Portal-Team", "description": "Collaboration Portal Team - COLLAB-007, COLLAB-008, COLLAB-009, COLLAB-010", "manager": "jennifer.martinez@technovasolutions.com", "email": "collab-oncall@technovasolutions.com"},
    
    # FINTECH - Financial Technology
    {"name": "FIN-L1-Support", "description": "FinTech L1 Support - Initial triage for all FIN products", "manager": "robert.kim@technovasolutions.com", "email": "fintech-oncall@technovasolutions.com"},
    {"name": "FIN-L2-Engineering", "description": "FinTech L2 Engineering - Technical issues for FIN-001 to FIN-010", "manager": "robert.kim@technovasolutions.com", "email": "fintech-oncall@technovasolutions.com"},
    {"name": "FIN-L3-Architecture", "description": "FinTech L3 Architecture - Critical financial system issues", "manager": "robert.kim@technovasolutions.com", "email": "fintech-oncall@technovasolutions.com"},
    {"name": "FIN-Payments-Team", "description": "FinTech Payments Team - FIN-001, FIN-002, FIN-010", "manager": "robert.kim@technovasolutions.com", "email": "fintech-oncall@technovasolutions.com"},
    {"name": "FIN-Accounting-Team", "description": "FinTech Accounting Team - FIN-003, FIN-004, FIN-005, FIN-008, FIN-009", "manager": "robert.kim@technovasolutions.com", "email": "fintech-oncall@technovasolutions.com"},
    {"name": "FIN-Treasury-Team", "description": "FinTech Treasury Team - FIN-006, FIN-007", "manager": "robert.kim@technovasolutions.com", "email": "fintech-oncall@technovasolutions.com"},
    
    # DEVTOOLS - Developer Tools & Platforms
    {"name": "DEVTOOLS-L1-Support", "description": "DevTools L1 Support - Initial triage for all DEV products", "manager": "alex.thompson@technovasolutions.com", "email": "devtools-oncall@technovasolutions.com"},
    {"name": "DEVTOOLS-L2-Engineering", "description": "DevTools L2 Engineering - Technical issues for DEV-001 to DEV-010", "manager": "alex.thompson@technovasolutions.com", "email": "devtools-oncall@technovasolutions.com"},
    {"name": "DEVTOOLS-L3-Architecture", "description": "DevTools L3 Architecture - Complex platform issues", "manager": "alex.thompson@technovasolutions.com", "email": "devtools-oncall@technovasolutions.com"},
    {"name": "DEV-SCM-Team", "description": "DevTools Source Control Team - DEV-001, DEV-003", "manager": "alex.thompson@technovasolutions.com", "email": "devtools-oncall@technovasolutions.com"},
    {"name": "DEV-CICD-Team", "description": "DevTools CI/CD Team - DEV-002, DEV-004, DEV-005", "manager": "alex.thompson@technovasolutions.com", "email": "devtools-oncall@technovasolutions.com"},
    {"name": "DEV-Observability-Team", "description": "DevTools Observability Team - DEV-006, DEV-007, DEV-008", "manager": "alex.thompson@technovasolutions.com", "email": "devtools-oncall@technovasolutions.com"},
    {"name": "DEV-API-Team", "description": "DevTools API Team - DEV-009, DEV-010", "manager": "alex.thompson@technovasolutions.com", "email": "devtools-oncall@technovasolutions.com"},
    
    # ITSM - IT Service Management
    {"name": "ITSM-L1-Support", "description": "ITSM L1 Support - Initial triage for all ITSM products", "manager": "david.wilson@technovasolutions.com", "email": "itsm-oncall@technovasolutions.com"},
    {"name": "ITSM-L2-Engineering", "description": "ITSM L2 Engineering - Technical issues for ITSM-001 to ITSM-010", "manager": "david.wilson@technovasolutions.com", "email": "itsm-oncall@technovasolutions.com"},
    {"name": "ITSM-L3-Architecture", "description": "ITSM L3 Architecture - Complex ITSM platform issues", "manager": "david.wilson@technovasolutions.com", "email": "itsm-oncall@technovasolutions.com"},
    {"name": "ITSM-ServiceDesk-Team", "description": "ITSM Service Desk Team - ITSM-001, ITSM-005, ITSM-006, ITSM-007", "manager": "david.wilson@technovasolutions.com", "email": "itsm-oncall@technovasolutions.com"},
    {"name": "ITSM-Asset-Team", "description": "ITSM Asset Team - ITSM-002, ITSM-003", "manager": "david.wilson@technovasolutions.com", "email": "itsm-oncall@technovasolutions.com"},
    {"name": "ITSM-Process-Team", "description": "ITSM Process Team - ITSM-004, ITSM-008, ITSM-009, ITSM-010", "manager": "david.wilson@technovasolutions.com", "email": "itsm-oncall@technovasolutions.com"},
    
    # ERP - Enterprise Resource Planning
    {"name": "ERP-L1-Support", "description": "ERP L1 Support - Initial triage for all ERP products", "manager": "lisa.anderson@technovasolutions.com", "email": "erp-oncall@technovasolutions.com"},
    {"name": "ERP-L2-Engineering", "description": "ERP L2 Engineering - Technical issues for ERP-001 to ERP-010", "manager": "lisa.anderson@technovasolutions.com", "email": "erp-oncall@technovasolutions.com"},
    {"name": "ERP-L3-Architecture", "description": "ERP L3 Architecture - Complex ERP platform issues", "manager": "lisa.anderson@technovasolutions.com", "email": "erp-oncall@technovasolutions.com"},
    {"name": "ERP-Core-Team", "description": "ERP Core Team - ERP-001, ERP-009, ERP-010", "manager": "lisa.anderson@technovasolutions.com", "email": "erp-oncall@technovasolutions.com"},
    {"name": "ERP-HR-Team", "description": "ERP HR Team - ERP-002", "manager": "lisa.anderson@technovasolutions.com", "email": "erp-oncall@technovasolutions.com"},
    {"name": "ERP-Supply-Team", "description": "ERP Supply Chain Team - ERP-003, ERP-004, ERP-006, ERP-007", "manager": "lisa.anderson@technovasolutions.com", "email": "erp-oncall@technovasolutions.com"},
    {"name": "ERP-Sales-Team", "description": "ERP Sales Team - ERP-005, ERP-008", "manager": "lisa.anderson@technovasolutions.com", "email": "erp-oncall@technovasolutions.com"},
    
    # IOT - IoT & Industrial (from guidelines)
    {"name": "IOT-L1-Support", "description": "IoT L1 Support - Initial triage for all IOT products", "manager": "iot.manager@technovasolutions.com", "email": "iot-oncall@technovasolutions.com"},
    {"name": "IOT-L2-Engineering", "description": "IoT L2 Engineering - Technical issues for IOT-001 to IOT-010", "manager": "iot.manager@technovasolutions.com", "email": "iot-oncall@technovasolutions.com"},
    {"name": "IOT-L3-Architecture", "description": "IoT L3 Architecture - Complex IoT/Industrial issues", "manager": "iot.manager@technovasolutions.com", "email": "iot-oncall@technovasolutions.com"},
    
    # General Support (fallback)
    {"name": "GENERAL-L1-Support", "description": "General L1 Support - Fallback for unidentified products", "manager": "support.manager@technovasolutions.com", "email": "support@technovasolutions.com"},
]


def get_servicenow_client():
    """Create and return a ServiceNow client."""
    instance = os.getenv("SERVICENOW_INSTANCE")
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")
    
    if not all([instance, username, password]):
        raise ValueError("Missing ServiceNow credentials. Please set SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD")
    
    # pysnow expects just the instance name (e.g., 'dev314739'), 
    # it automatically adds '.service-now.com'
    # Remove .service-now.com suffix if present to avoid duplication
    if instance.endswith(".service-now.com"):
        instance = instance.replace(".service-now.com", "")
    
    return pysnow.Client(instance=instance, user=username, password=password)


def check_group_exists(client, group_name: str) -> bool:
    """Check if an assignment group already exists."""
    try:
        group_resource = client.resource(api_path='/table/sys_user_group')
        response = group_resource.get(query={'name': group_name})
        return len(list(response.all())) > 0
    except Exception as e:
        print(f"  ⚠️  Error checking if group exists: {e}")
        return False


def create_assignment_group(client, group_data: dict) -> dict:
    """
    Create an assignment group in ServiceNow.
    
    Args:
        client: pysnow client
        group_data: dict with name, description, manager, email
        
    Returns:
        dict with success status and sys_id or error
    """
    result = {
        "success": False,
        "sys_id": None,
        "error": None
    }
    
    try:
        # Check if group already exists
        if check_group_exists(client, group_data["name"]):
            print(f"  ⏭️  Group '{group_data['name']}' already exists, skipping...")
            result["success"] = True
            result["error"] = "Already exists"
            return result
        
        # Create the group
        group_resource = client.resource(api_path='/table/sys_user_group')
        
        new_group = {
            "name": group_data["name"],
            "description": group_data.get("description", ""),
            "email": group_data.get("email", ""),
            "type": "assignment"  # Mark as assignment group
        }
        
        response = group_resource.create(payload=new_group)
        
        result["success"] = True
        # pysnow Response object needs to be accessed differently
        try:
            result["sys_id"] = response.one().get("sys_id", "unknown")
        except:
            result["sys_id"] = "created"
        print(f"  ✅ Created group: {group_data['name']} (sys_id: {result['sys_id']})")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"  ❌ Failed to create '{group_data['name']}': {e}")
    
    return result


def create_all_assignment_groups(dry_run: bool = False):
    """
    Create all TechNova assignment groups in ServiceNow.
    
    Args:
        dry_run: If True, just print what would be created without actually creating
    """
    print("=" * 60)
    print("TechNova Solutions - ServiceNow Assignment Groups Setup")
    print("=" * 60)
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()
        for group in ASSIGNMENT_GROUPS:
            print(f"  Would create: {group['name']}")
            print(f"    Description: {group['description']}")
            print(f"    Email: {group['email']}")
            print()
        print(f"Total groups to create: {len(ASSIGNMENT_GROUPS)}")
        return
    
    # Connect to ServiceNow
    print("🔌 Connecting to ServiceNow...")
    try:
        client = get_servicenow_client()
        print("  ✅ Connected successfully")
    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        return
    
    print()
    print(f"📋 Creating {len(ASSIGNMENT_GROUPS)} assignment groups...")
    print()
    
    # Track results
    created = 0
    skipped = 0
    failed = 0
    
    for group in ASSIGNMENT_GROUPS:
        result = create_assignment_group(client, group)
        
        if result["success"]:
            if result["error"] == "Already exists":
                skipped += 1
            else:
                created += 1
        else:
            failed += 1
    
    # Print summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  ✅ Created: {created}")
    print(f"  ⏭️  Skipped (already exist): {skipped}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Total: {len(ASSIGNMENT_GROUPS)}")


def list_existing_groups():
    """List all existing assignment groups in ServiceNow."""
    print("=" * 60)
    print("Existing Assignment Groups in ServiceNow")
    print("=" * 60)
    print()
    
    try:
        client = get_servicenow_client()
        group_resource = client.resource(api_path='/table/sys_user_group')
        
        # Query for groups that match our naming pattern
        response = group_resource.get(
            query={'name': 'LIKE^CLOUD-^ORname=LIKE^DATA-^ORname=LIKE^SEC-^ORname=LIKE^COLLAB-^ORname=LIKE^FIN-^ORname=LIKE^DEV^ORname=LIKE^ITSM-^ORname=LIKE^ERP-^ORname=LIKE^IOT-^ORname=LIKE^GENERAL-'},
            fields=['name', 'description', 'sys_id', 'email']
        )
        
        groups = list(response.all())
        
        if not groups:
            print("No TechNova assignment groups found.")
            return
        
        print(f"Found {len(groups)} groups:")
        print()
        
        for group in sorted(groups, key=lambda x: x.get('name', '')):
            print(f"  • {group.get('name')}")
            if group.get('description'):
                print(f"    {group.get('description')[:60]}...")
        
    except Exception as e:
        print(f"❌ Error listing groups: {e}")


def delete_all_assignment_groups(confirm: bool = False):
    """
    Delete all TechNova assignment groups from ServiceNow.
    USE WITH CAUTION!
    
    Args:
        confirm: Must be True to actually delete
    """
    print("=" * 60)
    print("⚠️  DELETE ALL ASSIGNMENT GROUPS")
    print("=" * 60)
    print()
    
    if not confirm:
        print("This will DELETE all TechNova assignment groups!")
        print("To confirm, call delete_all_assignment_groups(confirm=True)")
        return
    
    try:
        client = get_servicenow_client()
        group_resource = client.resource(api_path='/table/sys_user_group')
        
        deleted = 0
        
        for group_data in ASSIGNMENT_GROUPS:
            try:
                response = group_resource.get(query={'name': group_data['name']})
                groups = list(response.all())
                
                for group in groups:
                    group_resource.delete(query={'sys_id': group['sys_id']})
                    print(f"  🗑️  Deleted: {group_data['name']}")
                    deleted += 1
                    
            except Exception as e:
                print(f"  ⚠️  Could not delete {group_data['name']}: {e}")
        
        print()
        print(f"Deleted {deleted} groups")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage TechNova ServiceNow Assignment Groups")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without making changes")
    parser.add_argument("--list", action="store_true", help="List existing assignment groups")
    parser.add_argument("--delete", action="store_true", help="Delete all assignment groups (requires --confirm)")
    parser.add_argument("--confirm", action="store_true", help="Confirm deletion")
    
    args = parser.parse_args()
    
    if args.list:
        list_existing_groups()
    elif args.delete:
        delete_all_assignment_groups(confirm=args.confirm)
    else:
        create_all_assignment_groups(dry_run=args.dry_run)
