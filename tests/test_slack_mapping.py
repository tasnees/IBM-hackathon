"""Test the assignment group to Slack channel mapping."""
from api.main import get_slack_channel_for_assignment_group, ASSIGNMENT_GROUP_SLACK_CHANNELS

# Test the mapping
test_groups = [
    'CLOUD-L1-Support',
    'DATA-Analytics-Team', 
    'SEC-SOC-Team',
    'COLLAB-Portal-Team',
    'FIN-Payments-Team',
    'DEVTOOLS-L1-Support',
    'DEV-CICD-Team',
    'ITSM-ServiceDesk-Team',
    'ERP-HR-Team',
    'IOT-L2-Engineering',
    'GENERAL-L1-Support',
    'Unknown-Group'
]

print('Assignment Group -> Slack Channel Mapping Test')
print('=' * 60)
for group in test_groups:
    channel = get_slack_channel_for_assignment_group(group)
    default_indicator = '' if channel else ' (will use default from .env)'
    print(f'{group:30} -> {channel or "SLACK_DEFAULT_CHANNEL"}{default_indicator}')

print()
print('Configured Mappings:')
print('-' * 60)
for prefix, channel in ASSIGNMENT_GROUP_SLACK_CHANNELS.items():
    print(f'  {prefix:15} -> {channel}')
