import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import string
from random import choice

def generateRamdomString(length=8, chars=string.ascii_letters+string.digits):
    return ''.join([choice(chars) for i in range(length)])
    
def lambda_handler(event, context):
    db_client = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
    )
    users = db_client.Table('Users')
    userId = event['userId']
    print(userId)
    response = users.query(
        KeyConditionExpression=Key('userId').eq(userId)
        )
    gid = generateRamdomString()
    print(gid)
    newGroup = {
        'groupId': gid,
        'groupName': event['groups']['groupname'],
        'members': event['groups']['members']
    }
    response['Items'][0]['groups'].append(newGroup)
    print(response['Items'][0])
    users.put_item(
        Item = {
            'userId': event['userId'],
            'activities': response['Items'][0]['activities'],
            'groups': response['Items'][0]['groups']
        }    
    )
    return {
        'statusCode': 200,
        'body': {"groupId":gid}
    }
