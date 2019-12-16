import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import string
from random import choice

    
def lambda_handler(event, context):
    db_client = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
    )
    users = db_client.Table('Users')
    user_Id = event['userId']
    group_Id = event['groupId']
    activities = db_client.Table('Activities')
    print(user_Id)
    print(group_Id)
    users_response = users.query(
        KeyConditionExpression=Key('userId').eq(user_Id)
        )
    # print(users_response['Items'][0]['groups'])
    # print(users_response['Items'][0]['activities'])
    activity_Id = users_response['Items'][0]['activities']
    print(activity_Id)
    
    a = 'success'
    
    if len(activity_Id) == 0:
        user_group = users_response['Items'][0]['groups']
        # print(user_group)
        for i,item in enumerate(user_group):
            if item['groupId'] == group_Id:
                index = i
                break
        user_group.remove(user_group[i])
        users.update_item(
            Key={
                'userId': user_Id
            },
            UpdateExpression="set groups = :g",
            ExpressionAttributeValues={
            ':g': user_group
            },
            ReturnValues="UPDATED_NEW"
        )
    else:
        for item in activity_Id:
            activities_response =  activities.query(KeyConditionExpression=Key('activityId').eq(item))
            # print(activities_response['Items'][0]['groupId'])
            groupId_response = activities_response['Items'][0]['groupId']
            if groupId_response == group_Id:
                a = "fail"
                break
            else:
                user_group = users_response['Items'][0]['groups']
                # print(user_group)
                for i,item in enumerate(user_group):
                    if item['groupId'] == group_Id:
                        index = i
                        break
                user_group.remove(user_group[i])
                users.update_item(
                    Key={
                        'userId': user_Id
                    },
                    UpdateExpression="set groups = :g",
                    ExpressionAttributeValues={
                    ':g': user_group
                    },
                    ReturnValues="UPDATED_NEW"
                )
            
    
    return {
        'statusCode': 200,
        'body': {"str":a}
    }
