import boto3
from datetime import datetime, time, timedelta

def get_current_time_in_est():
    # Get current time in UTC
    now_utc = datetime.utcnow()
    # Convert to EST (UTC-5)
    est_offset = timedelta(hours=-5)
    now_est = now_utc + est_offset
    return now_est.time()

def is_off_business_hours(current_time):
    # Business hours in EST
    business_start = time(9, 0)  # 09:00 AM EST
    business_end = time(17, 0)   # 05:00 PM EST
    return not (business_start <= current_time <= business_end)

def stop_ec2_instances():
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            if tags.get('donotshutdown') != 'true':
                ec2.stop_instances(InstanceIds=[instance['InstanceId']])

def stop_rds_instances():
    rds = boto3.client('rds')
    instances = rds.describe_db_instances()
    for instance in instances['DBInstances']:
        tags_response = rds.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])
        tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
        if tags.get('donotshutdown') != 'true':
            rds.stop_db_instance(DBInstanceIdentifier=instance['DBInstanceIdentifier'])

def stop_sagemaker_notebooks():
    sagemaker = boto3.client('sagemaker')
    notebooks = sagemaker.list_notebook_instances(
        StatusEquals='InService'
    )

    for notebook in notebooks['NotebookInstances']:
        tags_response = sagemaker.list_tags(ResourceArn=notebook['NotebookInstanceArn'])
        tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
        if tags.get('donotshutdown') != 'true':
            sagemaker.stop_notebook_instance(NotebookInstanceName=notebook['NotebookInstanceName'])

def lambda_handler(event, context):
    current_time_est = get_current_time_in_est()
    if is_off_business_hours(current_time_est):
        stop_ec2_instances()
        stop_rds_instances()
        stop_sagemaker_notebooks()
