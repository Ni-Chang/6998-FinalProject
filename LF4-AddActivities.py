import json
import boto3
import string
from random import choice
from boto3.dynamodb.conditions import Key, Attr
import time

def lambda_handler(event, context):
    event["activityId"]= generateRamdomString()
    activityJson = event
    print(activityJson)
    dynamodb = boto3.resource('dynamodb')
    activitiesTable = dynamodb.Table('Activities')
    eventsTable = dynamodb.Table('Events')
    usersTable = dynamodb.Table('Users')
    
    # generate events items
    events = activityJson['events']
    eventItems = []
    for eventJson in events:
        numbers = []
        members = eventJson['members']
        for memberJson in members:
            numbers.append(memberJson['number'])
        eventItemJson = {
            'activityId': activityJson['activityId'],
            'eventId': generateRamdomString(),
            'eventTime': eventJson['time'],
            'numbers': numbers,
            'message': activityJson['message']
        }
        eventItems.append(eventItemJson)
        eventJson['eventId'] = eventItemJson['eventId']
    print(activityJson)
    print(eventItems)
    
    # add into Events
    with eventsTable.batch_writer() as batch:
        for eventItemJson in eventItems:
            batch.put_item(Item = eventItemJson)
    
    # add into Activities
    activitiesTable.put_item(Item = activityJson)
    
    # add activityId into user
    response = usersTable.query(
        KeyConditionExpression=Key('userId').eq(activityJson['userId'])
    )
    activities = response['Items'][0]['activities']
    activities.append(event["activityId"])
    usersTable.update_item(
        Key = {'userId': activityJson['userId']},
        UpdateExpression = "set activities = :a",
        ExpressionAttributeValues={
            ':a': activities
        },
        ReturnValues="UPDATED_NEW"
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def generateRamdomString(length=16, chars=string.ascii_letters+string.digits):
    return ''.join([choice(chars) for i in range(length)])