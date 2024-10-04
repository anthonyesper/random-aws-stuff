import json
import boto3
import base64
import gzip
import io

def send_log_to_sns(event):
    sns_client = boto3.client('sns')

    # Decode and decompress the CloudWatch log event
    if 'awslogs' in event:
        encoded_data = event['awslogs']['data']

        # First decode the base64-encoded data
        decoded_data = base64.b64decode(encoded_data)

        # Decompress the gzip-compressed data
        with gzip.GzipFile(fileobj=io.BytesIO(decoded_data)) as gz:
            decompressed_data = gz.read()

        # Parse the decompressed data as JSON
        log_event = json.loads(decompressed_data)
    else:
        log_event = event  # Handle the event if it's already plain

    # Format the message as readable JSON
    message = json.dumps(log_event, ensure_ascii=False, indent=4)

    # Send the message to SNS
    response = sns_client.publish(
        TopicArn='your-sns-topic-arn',
        Message=message,
        Subject="CloudWatch Log Event Notification"
    )
    
    return response
