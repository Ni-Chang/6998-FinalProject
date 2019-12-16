import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    usersTable = dynamodb.Table('Users')
    activitiesTable = dynamodb.Table('Activities')
    userId = event['userId']
    response = usersTable.query(
        KeyConditionExpression=Key('userId').eq(userId)
    )
    
    activities = response['Items'][0]['activities']
    print(activities)
    results = []
    for activity in activities:
        response = activitiesTable.query(
            KeyConditionExpression=Key('activityId').eq(activity)
        )
        results.append(response['Items'][0])
    return {
        'statusCode': 200,
        'body': results
    }