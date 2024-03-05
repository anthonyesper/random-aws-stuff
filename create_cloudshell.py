import json
import boto3

def get_network_settings():
    ec2=boto3.client('ec2')
    vpcs = ec2.describe_vpcs()
    
    vpcid = vpcs['Vpcs'][0]['VpcId']
    
    print(vpcid)
    
    subnets = ec2.describe_subnets()
    lst_subnets=[]
    for subnet in subnets['Subnets']:
        #print(subnet)
        #print(subnet['SubnetId'])
        lst_subnets.append(subnet['SubnetId'])
    print(lst_subnets)
    
    sggroups = ec2.describe_security_groups()
    lst_sgs=[]
    for sg in sggroups['SecurityGroups']:
        if 'default' in sg['GroupName']:
            lst_sgs.append(sg['GroupId'])
    print(lst_sgs)
    
    return(vpcid, lst_subnets, lst_sgs)

def create_cloudshell_environment(environment_name):
    cloudshell_client = boto3.client('cloudshell')
    
    response = cloudshell_client.create_environment(
        name=environment_name,
        description='My CloudShell Environment',
        type='single-account',
        connectionType='CONNECT_SSM'
    )
    
    environment_id = response['environmentId']
    print(f"CloudShell environment {environment_name} created with ID: {environment_id}")
    return environment_id

def get_iam_execution_role():
    client = boto3.client('iam')
    
    response = client.get_role(
    RoleName='SandboxServiceRole'
                                )
    role = response['Role']['Arn']
    print(role)
    return role
    #return ('arn:aws:iam::897994370356:role/SandboxServiceRole')

def lambda_handler(event, context):
    # TODO implement
    #get_iam_execution_role()
    
    smclient = boto3.client('sagemaker')
    vpcid, lst_subnets,lst_sgs = get_network_settings()
    domainstatus = create_cloudshell_environment('MyCloudShellEnvironment')
    print(domainstatus)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
