import json
from pathlib import Path
import builtins 
import typing

from constructs import Construct  
from typing import Any

# import boto3
from aws_cdk import aws_ssm as ssm 
from aws_cdk import pipelines, Stack  
from aws_cdk import aws_secretsmanager as secrets


class Pipeline(Stack): 
        
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.repo_name = ''
        self.repo_branch = 'master' 

        github_input_source = pipelines.CodePipelineSource.git_hub(
            repo_string="{github_user}/{github_repo}".format(
                github_user=ssm.StringParameter.value_from_lookup(
                    self,
                    parameter_name='github-user',
                ),
                github_repo=self.repo_name
            ),
            branch="main",
            authentication='' #secrets.get('github-token'),
        )
        synth_action = pipelines.CodeBuildStep(
            "Synth",
            input=github_input_source,
            commands=[
                "pyenv local 3.7.10",
                "./scripts/install-deps.sh",
                "npm install -g aws-cdk",
                "cdk synth",
            ],
            primary_output_directory="cdk.out"
        )

        cdk_pipeline = pipelines.CodePipeline(
            self,
            "EKSMultiEnvPipeline",
            synth=synth_action,
            publish_assets_in_parallel=False,
            cli_version=Pipeline._get_cdk_cli_version(),
        ) 
