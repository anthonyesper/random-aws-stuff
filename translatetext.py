import json
import boto3

def translate_text(text, source_lang, target_lang):
    translate_client = boto3.client('translate')
    
    response = translate_client.translate_text(
        Text=text,
        SourceLanguageCode=source_lang,
        TargetLanguageCode=target_lang
    )
    
    translated_text = response['TranslatedText']
    return translated_text

def get_network_settings():
    ec2=boto3.client('ec2')
    vpcs = ec2.describe_vpcs()
    
    vpcid = vpcs['Vpcs'][0]['VpcId']
    
    print(vpcid)
    
    subnets = ec2.describe_subnets()
    lst_subnets=[]
    for subnet in subnets['Subnets']:
        lst_subnets.append(subnet['SubnetId'])
    print(lst_subnets)
    
    sggroups = ec2.describe_security_groups()
    lst_sgs=[]
    for sg in sggroups['SecurityGroups']:
        if 'default' in sg['GroupName']:
            lst_sgs.append(sg['GroupId'])
    print(lst_sgs)
    
    return(vpcid, lst_subnets, lst_sgs)

def get_iam_execution_role():
    client = boto3.client('iam')
    
    response = client.get_role(
    RoleName='SandboxServiceRole'
                                )
    role = response['Role']['Arn']
    print(role)
    return role

def lambda_handler(event, context):
    # Example usage of translate_text function
    translated_text = translate_text("Hello, how are you?", "en", "es")
    print("Translated Text:", translated_text)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
