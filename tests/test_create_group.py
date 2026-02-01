"""Test creating a single assignment group."""
import os
from dotenv import load_dotenv
import pysnow

load_dotenv()

instance = os.getenv('SERVICENOW_INSTANCE').replace('.service-now.com', '')
print(f'Instance: {instance}')

client = pysnow.Client(
    instance=instance, 
    user=os.getenv('SERVICENOW_USERNAME'), 
    password=os.getenv('SERVICENOW_PASSWORD')
)
resource = client.resource(api_path='/table/sys_user_group')

# Try to create one test group
new_group = {
    'name': 'TEST-Group-01',
    'description': 'Test assignment group',
    'type': 'assignment'
}

print('Creating test group...')
try:
    response = resource.create(payload=new_group)
    print(f'Response type: {type(response)}')
    result = response.one()
    print(f'Created! sys_id: {result.get("sys_id")}')
    print(f'Full result: {result}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

# List all groups to check
print('\nListing all groups...')
try:
    response = resource.get()
    groups = list(response.all())
    print(f'Total groups: {len(groups)}')
    for g in groups[:10]:
        print(f'  - {g.get("name")}')
except Exception as e:
    print(f'Error listing: {e}')
