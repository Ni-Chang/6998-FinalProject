import json
import boto3

def lambda_handler(event, context):
    db_client = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
    )
    users = db_client.Table('Users')
    userId = event['userName']
    users.put_item(
        Item = {
            'userId': userId,
            'activities': [],
            'groups': []
        }    
    )
    return event