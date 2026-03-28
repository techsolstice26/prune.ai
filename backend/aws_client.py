import boto3
import os

# Use region from environment or default to us-east-1
region = os.environ.get("AWS_REGION", "us-east-1")

ec2_client = boto3.client('ec2', region_name=region)
dynamodb = boto3.resource('dynamodb', region_name=region)

SNOOZE_TABLE = "SnoozeRegistry"

def restart_instance(instance_id: str):
    """Restarts a stopped EC2 instance to remediate the anomaly."""
    try:
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def add_to_snooze_registry(instance_id: str):
    """Adds instance_id to SnoozeRegistry to pause monitoring."""
    try:
        table = dynamodb.Table(SNOOZE_TABLE)
        response = table.put_item(
            Item={
                'instance_id': instance_id
            }
        )
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}
