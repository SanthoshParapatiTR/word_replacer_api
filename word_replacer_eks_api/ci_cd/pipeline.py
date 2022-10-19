 
from word_replacer_eks_api.infra.vpc import  VPCStack
from word_replacer_eks_api.infra.eks import EKSStack
from word_replacer_eks_api.ci_cd.ci_cd import CICDStack

import aws_cdk as cdk
from constructs import Construct   
from aws_cdk import pipelines, Stack, aws_codebuild as codebuild,aws_codepipeline  as codepipeline, aws_codepipeline_actions as codepipeline_actions


class Pipeline(Stack): 
        
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
 
        pipeline = pipelines.CodePipeline(self, "Pipeline",
            synth=pipelines.CodeBuildStep("Synth", 
                input=pipelines.CodePipelineSource.connection("SanthoshParapatiTR/word_replacer_api", "master",
                    connection_arn="arn:aws:codestar-connections:us-east-1:349115202997:connection/0e1adcf2-f412-4c68-bb27-4c94dc1ffb4e"
                ),
                commands=[
                "npx npm install",
                "pip install -r requirements.txt",
                "npm install -g aws-cdk",
                "cdk synth",
            ],
            primary_output_directory="cdk.out",
            

            )
        )
        
        primary_region =cdk.Environment(account='349115202997', region='us-east-1')   
        pipeline.add_stage(Deploy_VPC_EKS(self, "VPCEKS", 
                    env=primary_region, 
                ))
        pipeline.add_stage(CI_CDStack(self, "CICD", 
                    env=primary_region, 
                ))
       
class Deploy_VPC_EKS(cdk.Stage): 
    def __init__(
            self,
            scope: Construct,
            id_: str,
            *,
            env: cdk.Environment,
            outdir: str = None, 
            
    ):
        super().__init__(scope, id_, env=env, outdir=outdir)
 
        vpc_stack = VPCStack(self, "VPC", env=env )


        eks_stack = cdk.Stack(self, "EKS")
        eks_stack.add_dependency(vpc_stack)
 
        EKSStack(scope=eks_stack,
                       construct_id=id_,
                       vpc=vpc_stack.vpc, 
                        env = env
                       )

class CI_CDStack(cdk.Stage): 
    def __init__(
            self,
            scope: Construct,
            id_: str,
            *,
            env: cdk.Environment,
            outdir: str = None, 
            
    ):
        super().__init__(scope, id_, env=env, outdir=outdir)
        CICDStack(self, 'BuildImage', env = env)