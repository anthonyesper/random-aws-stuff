import boto3
import logging
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def stop_ec2_instances():
    try:
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
                    logger.info(f"Stopping EC2 instance: {instance['InstanceId']}")
                else:
                    logger.info(f"Skipping EC2 instance: {instance['InstanceId']} (tagged with donotshutdown:true)")
    except NoCredentialsError:
        logger.error("No AWS credentials found. Please configure your credentials.")
    except PartialCredentialsError:
        logger.error("Incomplete AWS credentials found. Please check your credentials.")

def stop_rds_instances():
    try:
        rds = boto3.client('rds')
        instances = rds.describe_db_instances()
        for instance in instances['DBInstances']:
            # Skip Aurora instances
            if instance['Engine'].startswith('aurora'):
                logger.info(f"Skipping RDS instance: {instance['DBInstanceIdentifier']} (Aurora instance)")
                continue

            tags_response = rds.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])
            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
            if tags.get('donotshutdown') != 'true':
                rds.stop_db_instance(DBInstanceIdentifier=instance['DBInstanceIdentifier'])
                logger.info(f"Stopping RDS instance: {instance['DBInstanceIdentifier']}")
            else:
                logger.info(f"Skipping RDS instance: {instance['DBInstanceIdentifier']} (tagged with donotshutdown:true)")
    except NoCredentialsError:
        logger.error("No AWS credentials found. Please configure your credentials.")
    except PartialCredentialsError:
        logger.error("Incomplete AWS credentials found. Please check your credentials.")

def lambda_handler(event, context):
    logger.info("Initiating shutdown of instances")
    stop_ec2_instances()
    stop_rds_instances()
