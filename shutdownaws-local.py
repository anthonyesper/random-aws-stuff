import boto3
import logging
from datetime import datetime
import pytz
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def get_current_time_in_est():
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    eastern = pytz.timezone('US/Eastern')
    now_est = now_utc.astimezone(eastern)
    return now_est.time()

def is_off_business_hours(current_time):
    business_start = datetime.strptime("09:00", "%H:%M").time()  # 09:00 AM EST
    business_end = datetime.strptime("17:00", "%H:%M").time()   # 05:00 PM EST
    return not (business_start <= current_time <= business_end)

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

def stop_sagemaker_notebooks():
    try:
        sagemaker = boto3.client('sagemaker')
        notebooks = sagemaker.list_notebook_instances(
            StatusEquals='InService'
        )

        for notebook in notebooks['NotebookInstances']:
            tags_response = sagemaker.list_tags(ResourceArn=notebook['NotebookInstanceArn'])
            tags = {tag['Key']: 'Value' for tag in tags_response.get('Tags', [])}
            if tags.get('donotshutdown') != 'true':
                sagemaker.stop_notebook_instance(NotebookInstanceName=notebook['NotebookInstanceName'])
                logger.info(f"Stopping SageMaker notebook instance: {notebook['NotebookInstanceName']}")
            else:
                logger.info(f"Skipping SageMaker notebook instance: {notebook['NotebookInstanceName']} (tagged with donotshutdown:true)")
    except NoCredentialsError:
        logger.error("No AWS credentials found. Please configure your credentials.")
    except PartialCredentialsError:
        logger.error("Incomplete AWS credentials found. Please check your credentials.")

def main():
    current_time_est = get_current_time_in_est()
    logger.info(f"Current time in EST: {current_time_est}")
    if is_off_business_hours(current_time_est):
        logger.info("Off business hours - initiating shutdown of instances")
        stop_ec2_instances()
        stop_rds_instances()
        stop_sagemaker_notebooks()
    else:
        logger.info("Business hours - no shutdown required.")

if __name__ == "__main__":
    main()
