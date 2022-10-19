import aws_cdk as cdk
from constructs import Construct   
from aws_cdk import  Stack, aws_codebuild as codebuild, aws_codepipeline  as codepipeline, aws_codepipeline_actions as codepipeline_actions


class CICDStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        source_output = codepipeline.Artifact(artifact_name='app_source')
        build_spec = codebuild.BuildSpec.from_object({                 
                            "version": '0.2',
                            "phases": {
                            "pre_build": {
                                "commands": [
                                'ls'
                                'env',
                                'export TAG=${CODEBUILD_RESOLVED_SOURCE_VERSION}',
                                'export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output=text)', 
                                'echo Logging in to Amazon ECR',
                                'aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 349115202997.dkr.ecr.us-east-1.amazonaws.com',
                                ],
                            },

                            # aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 349115202997.dkr.ecr.us-east-1.amazonaws.com

                            # sudo docker build -t word_replacer_api .

                            # sudo docker tag word_replacer_api:latest 349115202997.dkr.ecr.us-east-1.amazonaws.com/word_replacer_api:latest

                            # sudo docker push 349115202997.dkr.ecr.us-east-1.amazonaws.com/word_replacer_api:latest
                            "build": {
                                "commands": [
                                'cd ',
                                'ocker build -t word_replacer_api:$TAG .',
                                'docker push 349115202997.dkr.ecr.us-east-1.amazonaws.com/word_replacer_api:$TAG',
                                ],
                            },
                            "post_build": {
                                "commands": [
                                'kubectl get no',
                                'kubectl set image deployment word_replacer_api flask=word_replacer_api:$TAG',
                                ],
                            },
                            },
                        })
        
  
        build_ecr_image = codebuild.PipelineProject(
                        self,
                        project_name="Build",
                        environment= codebuild.BuildEnvironment(                         
                            compute_type=codebuild.ComputeType.MEDIUM
                            ),
                        environment_variables= None,
                        build_spec= build_spec,
                        id='buildimage'
                    )
        action = codepipeline_actions.CodeBuildAction(
            action_name="BuildImage",
            project=build_ecr_image,
            input=source_output,  # The build action must use the CodeCommitSourceAction output as input.
            outputs=[codepipeline.Artifact()]
        )
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="GIT_Source",
            owner="SanthoshParapatiTR",
            repo="word_replacer_api",
            output=source_output,
            connection_arn="arn:aws:codestar-connections:us-east-1:349115202997:connection/0e1adcf2-f412-4c68-bb27-4c94dc1ffb4e",
                   
        )
 
        
        pipeline = codepipeline.Pipeline(self, "CICD",
        stages=[
            codepipeline.StageProps(
            stage_name="source",
            actions=[source_action]
            ), 
            
            codepipeline.StageProps(
            stage_name="buildiamge",
            actions=[action]
            )
            ]
        )

  
        