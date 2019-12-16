import json
from time import gmtime, strftime
import boto3
from boto3.dynamodb.conditions import Key, Attr
import datetime
import time
from datetime import datetime, timedelta

def lambda_handler(ev, context):
    # this function should be triggered once an hour
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')

    ts = (datetime.now() + timedelta(hours=-5)).strftime('%Y-%m-%d %H:00')
    print(ts)

    # retrieve all the events in the time period
    response = client.query(
        TableName = "Events",
        IndexName = "eventTime-index",
        KeyConditionExpression= "eventTime = :t",
        ExpressionAttributeValues= {
            ":t": { "S" : ts }
        }
    )
    print(response)
    
    toDeleteActivitesDict = {}
    sendingList = []
    for event in response["Items"]:
        toDeleteActivitesDict[event["activityId"]["S"]] = event["eventId"]["S"]
        # toDeleteEvents.append((event["eventId"]["S"], event["eventTime"]["S"]))
        for number in event["numbers"]["L"]:
            sendingList.append((number["S"], event["message"]["S"]))
            
    print(sendingList)
    print(toDeleteActivitesDict)
    
    usersTable = dynamodb.Table('Users')
    activitiesTable = dynamodb.Table('Activities')
    eventsTable = dynamodb.Table('Events')
            
    # TODO: delete events from activities, if needed, delete activity
    for activityId, eventId in toDeleteActivitesDict.items():
        response = activitiesTable.query(
            KeyConditionExpression=Key('activityId').eq(activityId)
        )
        events = response["Items"][0]["events"]
        toDeleteEvents = []
        for i in range(0, len(events)):
            print(events[i])
            print(len(events))
            toDeleteEvents.append((events[i]["eventId"], events[i]["time"]))
            if events[i]["eventId"] == eventId:
                events = events[i + 1:len(events)]
                print(len(events))
                if len(events) == 0:
                    # delete this activity
                    activitiesTable.delete_item(
                        Key = {'activityId': activityId}
                    )
                    # delete the activityId in Users table
                    response = usersTable.query(
                        KeyConditionExpression=Key('userId').eq(response["Items"][0]["userId"])
                    )
                    activities = response['Items'][0]['activities']
                    activities.remove(activityId)
                    usersTable.update_item(
                        Key = {'userId': response["Items"][0]["userId"]},
                        UpdateExpression = "set activities = :a",
                        ExpressionAttributeValues={
                            ':a': activities
                        },
                        ReturnValues="UPDATED_NEW"
                    )
                else:
                    activitiesTable.update_item(
                        Key = {'activityId': activityId},
                        UpdateExpression = "set events = :a",
                        ExpressionAttributeValues={
                            ':a': events
                        },
                        ReturnValues="UPDATED_NEW"
                    )
                    
                # delete all events before
                with eventsTable.batch_writer() as batch:
                    for e in toDeleteEvents:
                        eventsTable.delete_item(
                            Key={
                                'eventId': e[0],
                                'eventTime': e[1]
                            }
                        )
                break;
    
    # TODO: send messages
    print(sendingList)
    for send in sendingList:
        # number: send[0], message: send[1]
        print("fdsa")
        sns = boto3.client("sns", region_name="us-east-1")
        sns.publish(
            PhoneNumber = send[0],
            Message = send[1]
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }