import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.resource('dynamodb')
    usersTable = dynamodb.Table('Users')
    activitiesTable = dynamodb.Table('Activities')
    eventsTable = dynamodb.Table('Events')
    
    # delete activity in Activities table
    response = activitiesTable.query(
        KeyConditionExpression=Key('activityId').eq(event['activityId'])
    )
    events = response['Items'][0]['events']
    print(events)
    eId = []
    for e in events:
        eventTime = dict()
        eventTime['event'] = e['eventId']
        eventTime['time'] = e['time']
        eId.append(eventTime)
    for eid in eId:
        print("eid:", eid)
        eventsTable.delete_item(
            Key={
                'eventId': eid['event'],
                'eventTime': eid['time']
            }
        )
    activitiesTable.delete_item(
        Key={
            'activityId': event['activityId']
        }
    )
    # delete the activityId in Users table
    response = usersTable.query(
        KeyConditionExpression=Key('userId').eq(event['userId'])
    )
    activities = response['Items'][0]['activities']
    activities.remove(event["activityId"])
    usersTable.update_item(
        Key = {'userId': event['userId']},
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
