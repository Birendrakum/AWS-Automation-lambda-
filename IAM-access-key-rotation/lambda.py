import boto3
import json
from datetime import datetime, timedelta, timezone

iam = boto3.client('iam')
sns = boto3.client('sns')
secretsmanager = boto3.client('secretsmanager')

# Paste your aws sns topic arn here
TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:MalwareNotifications"

def rotate_key_func(user_name):
    # Create a new access key for the user
    new_access_key = iam.create_access_key(UserName=user_name)
    new_secret_access_key = new_access_key['AccessKey']['SecretAccessKey']
        
    # Create a secret name for the new access key in secrets manager
    secret_name = f"{user_name}-access-key-rotation"
        
    # Create secret payload to store in secrets manager
    secret_payload = {
       "UserName": user_name,
       "AccessKeyId": new_access_key['AccessKey']['AccessKeyId'],
       "SecretAccessKey": new_secret_access_key,
       "CreatedAt": datetime.now(timezone.utc).isoformat()           
            }
    try:
        secretsmanager.create_secret(
        Name=secret_name,
        SecretString=json.dumps(secret_payload),
        Tags=[
            {
                'Key': 'Owner',
                'Value': user_name
            }
          ]
        )
    except secretsmanager.exceptions.ResourceExistsException:
        secretsmanager.put_secret_value(
          SecretId=secret_name,
          SecretString=json.dumps(secret_payload),
        )
    return secret_name


def lambda_handler(event, context):
    paginator = iam.get_paginator('list_users')
    for page in paginator.paginate():
        for user in page['Users']:
          access_keys = iam.list_access_keys(UserName=user['UserName'])
          user_name = user['UserName']
          if len(access_keys['AccessKeyMetadata']) > 1:
            sns.publish(
                TopicArn=TOPIC_ARN,
                Message=f"""
                  User {user['UserName']} has more than 1 access keys.
                  --------------------------------
                    Please review the access keys and delete the unnecessary access keys to maintain security best practices.
                    """,
                Subject=f"Access Key Alert for User {user['UserName']}"
            )
            continue
          elif len(access_keys['AccessKeyMetadata']) == 0:
              response = rotate_key_func(user_name)
              sns.publish(
                TopicArn=TOPIC_ARN,
                Message=f"""
                  User {user['UserName']} has no active access keys.
                  --------------------------------
                    User {user['UserName']} does not have any active keys.
                    A new access key has been created for the user in secret manager with the name: {response}
                    Please rotate the access key and update your applications to use the new access key.
                    """,
                Subject=f"Access Key Rotation Alert for User {user['UserName']}"
             )
          else:
              current_access_key = access_keys['AccessKeyMetadata'][0]
              if current_access_key['CreateDate'] > (datetime.now(timezone.utc) - timedelta(days=90)) and current_access_key['Status'] == 'Active':
                # Active access key is present and is less than 90 days old, no action needed
                pass
              else:
                  response = rotate_key_func(user_name)
                  sns.publish(
                  TopicArn=TOPIC_ARN,
                  Message=f"""
                    User {user['UserName']} has no active access keys or all active keys are older than 90 days.
                    --------------------------------
                    A new access key has been created for the user in secret manager with the name: {response}
                    Old access key: {current_access_key['AccessKeyId']} should be reviewed and removed after applications are updated to use the new key.
                    Please rotate the access key and update your applications to use the new access key.
                    """,
                  Subject=f"Access Key Rotation Alert for User {user['UserName']}"
             )
        
    