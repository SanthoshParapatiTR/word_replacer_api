import aws_cdk as cdk
from constructs import Construct   
from aws_cdk import  Stack, aws_codebuild as codebuild, aws_codepipeline  as codepipeline, aws_codepipeline_actions as codepipeline_actions


class CICDStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        source_output = codepipeline.Artifact(artifact_name='app_source')
        build_spec = codebuild.BuildSpec.from_object({
                    "version": "0.2",
                    "phases": {
                        "pre_build": {
                        "commands": [ 
                            "export TAG=${CODEBUILD_BUILD_NUMBER}",
                            "export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output=text)",
                            "apt-get update && apt-get -y install jq python3-pip python3-dev && pip3 install --upgrade awscli",
                            "curl -sS -o kubectl https://amazon-eks.s3-us-west-2.amazonaws.com/1.14.6/2019-08-22/bin/linux/amd64/kubectl",
                            "chmod +x ./kubectl " , 
                            "echo Logging in to Amazon ECR",
                            "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 349115202997.dkr.ecr.us-east-1.amazonaws.com"
                        ]
                        },
                        "build": {
                        "commands": [ 
                            "cd word_replacer_eks_api/word_replacer_app/",
                            "docker build -t word_replacer_api:$TAG .",
                            "docker tag word_replacer_api:$TAG 349115202997.dkr.ecr.us-east-1.amazonaws.com/word_replacer_api:$TAG",
                            "docker push 349115202997.dkr.ecr.us-east-1.amazonaws.com/word_replacer_api:$TAG"
                        ]
                        
                        },
                        "post_build": {
                        "commands": [
                            "aws sts assume-role --role-arn arn:aws:iam::349115202997:role/VPCEKS-EKSVPCEKSDED15206-ClusterAdminRole047D4FCA-XCOTSMISXLJX --role-session-name codebuild-kubectl --duration-seconds 900",
                            "aws eks update-kubeconfig --name EKS_Cluster-VPCEKS --region us-east-1 --role-arn arn:aws:iam::349115202997:role/VPCEKS-EKSVPCEKSDED15206-ClusterAdminRole047D4FCA-XCOTSMISXLJX",
                            "export KUBECONFIG=/root/.kube/config",
                            "cd word_replacer_eks_api/word_replacer_app/",
                            "kubectl apply -f deployment.yml ",
                            "kubectl set image deployment word-replacer-api word-replacer-api=word_replacer_api:$TAG"
                        ]
                        }
                    }
                }
             )
                            
  
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

  
        