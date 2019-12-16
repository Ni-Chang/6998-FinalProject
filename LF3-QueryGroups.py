import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    usersTable = dynamodb.Table('Users')
    userId = event['userId']
    response = usersTable.query(
        KeyConditionExpression=Key('userId').eq(userId)
    )
    print(response['Items'][0]['groups'])
    return {
        'statusCode': 200,
        'body': response['Items'][0]['groups']
    }