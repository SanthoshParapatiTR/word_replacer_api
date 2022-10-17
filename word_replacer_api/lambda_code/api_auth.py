import json
import boto3
import os

def lambda_handler(event, context):
    secret_name = 'arn:aws:secretsmanager:us-east-1:349115202997:secret:Authorization_Key-5bFnEk' 
    region_name = context.invoked_function_arn.split(":")[3]

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    response = client.get_secret_value(
                     SecretId=secret_name
        )
    secret=json.loads(response['SecretString'])
  

    if event['headers']['authorization'] == secret['auth-token']:
        return {
          "isAuthorized": True
        }
