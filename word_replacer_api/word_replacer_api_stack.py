import os
import random
import string 
import json
import shutil
from constructs import Construct  

from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,    
    SecretValue as secretvalue,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events as events,
    aws_s3 as s3, 
    aws_sam as sam,
    aws_apigatewayv2_alpha as apigateway,
    aws_secretsmanager as secrets
)

from aws_cdk import aws_apigatewayv2_alpha 
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpLambdaAuthorizer, HttpLambdaResponseType

 
#aws_region = os.environ['AWS_REGION'] 

class WordReplacerApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
        #create apigateway
        api_name = 'word-replacer-api'
        word_replacer_api = apigateway.HttpApi(self,  api_name) 

        #create secret for authorization
        secret_name = 'Authorization_Key'
        auth_secret = secrets.Secret(self, "authorization-token", secret_name= secret_name,
                secret_object_value={
                "auth-token": secretvalue.unsafe_plain_text(''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10)))
                }
        )  
        word_replacer_code = _lambda.Code.from_inline(open(f"word_replacer_api\\lambda_code\\word_replacer.py", "r").read())
        api_authorizer_code = _lambda.Code.from_inline(open(f"word_replacer_api\\lambda_code\\api_auth.py", "r").read())

        word_replacer_lambda = create_lambda(self, 'word_replacer_lambda', 'index.lambda_handler',
                               ' AWS Lambda API for word replacement', word_replacer_code, 'CreateLambdaWordReplacer')

        api_authorizer_lambda = create_lambda(self, 'api_authorizer_lambda', 'index.lambda_handler',
                               'AWS Lambda API for authorizing api', api_authorizer_code, 'CreateLambdaAuthorizor')


        authorizer = HttpLambdaAuthorizer("apiAuthorizer", api_authorizer_lambda,
            response_types=[HttpLambdaResponseType.SIMPLE]
        )
        http_route = apigateway.HttpRoute(self, "Replace",
                http_api=word_replacer_api,
                integration=HttpLambdaIntegration('word_replacer', word_replacer_lambda,payload_format_version=apigateway.PayloadFormatVersion.VERSION_1_0),
                route_key=apigateway.HttpRouteKey.with_("/default", apigateway.HttpMethod.ANY),
                authorizer=authorizer
            )

def create_lambda(cls: classmethod, function_name, handler, desc, code, stack_id='CreateLambda'):
    return _lambda.Function(
        cls,
        stack_id,
        function_name=function_name,
        runtime=_lambda.Runtime.PYTHON_3_9,
        handler=handler,
        timeout=Duration.minutes(10),
        description=desc,
        tracing=_lambda.Tracing.ACTIVE,
        environment={},
        code=code, 
    )
