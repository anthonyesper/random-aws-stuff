import boto3

ROLE_NAME = 'CentralAccountAccessRole'  # The role to assume in each workload account
OU_ID = 'ou-xxxxxxxx-xxxxxxxx'  # Specify the OU ID

def get_accounts_in_ou(ou_id):
    organizations_client = boto3.client('organizations')
    accounts = []
    paginator = organizations_client.get_paginator('list_accounts_for_parent')
    response_iterator = paginator.paginate(ParentId=ou_id)
    
    for page in response_iterator:
        for account in page['Accounts']:
            accounts.append(account['Id'])
    
    return accounts

def assume_role(account_id, role_name):
    client = boto3.client('sts')
    role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'
    response = client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='CentralAccountSession'
    )
    return response['Credentials']

def delete_stale_inventory(credentials):
    ssm_client = boto3.client('ssm',
                              aws_access_key_id=credentials['AccessKeyId'],
                              aws_secret_access_key=credentials['SecretAccessKey'],
                              aws_session_token=credentials['SessionToken'])
    
    paginator = ssm_client.get_paginator('list_inventory_entries')
    response_iterator = paginator.paginate()
    
    for page in response_iterator:
        for entry in page['Entities']:
            resource_id = entry['Id']
            # Check if the resource still exists
            try:
                resource = ssm_client.describe_instance_information(
                    InstanceInformationFilterList=[
                        {
                            'key': 'InstanceIds',
                            'valueSet': [resource_id]
                        },
                    ]
                )
                if not resource['InstanceInformationList']:
                    # Delete the stale inventory entry
                    ssm_client.delete_inventory(
                        InstanceId=resource_id,
                        TypeName='AWS:InstanceInformation'
                    )
                    print(f'Deleted stale inventory for resource: {resource_id}')
            except ssm_client.exceptions.InventoryDoesNotExistException:
                # Handle the case where the inventory doesn't exist
                print(f'No inventory found for resource: {resource_id}')

if __name__ == "__main__":
    try:
        account_ids = get_accounts_in_ou(OU_ID)
        for account_id in account_ids:
            try:
                credentials = assume_role(account_id, ROLE_NAME)
                delete_stale_inventory(credentials)
            except Exception as e:
                print(f'Error processing account {account_id}: {e}')
    except Exception as e:
        print(f'Error fetching accounts in OU {OU_ID}: {e}')
