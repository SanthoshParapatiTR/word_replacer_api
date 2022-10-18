import json
import boto3 


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code. 
    '''
    print("Received event: " + json.dumps(event, indent=2))

    operations = [  'GET', 'POST'] 

    operation = event['httpMethod']
    if operation in operations:
        if operation == 'POST':
            payload = event['queryStringParameters']  
            return respond(None,word_replacer(payload['inputstring']))
            
        if operation == 'GET' :
            return respond(None, 'Welcome to Word Replacer API')
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))

def word_replacer(input_string):
    replce_words_list = ['Oracle', 'Google', 'Microsoft','Amazon' , 'Deloitte' ]
    
    output = ''
    for word in input_string.split():
        if word in replce_words_list:
            word = word + r'©'
        output = output + word + ' '
    return output
