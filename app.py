#!/usr/bin/env python3
import os

import aws_cdk as cdk

from word_replacer_api.word_replacer_api_stack import WordReplacerApiStack
from word_replacer_eks_api.infra.vpc import  VPCStack
from word_replacer_eks_api.infra.eks import EKSStack
from word_replacer_eks_api.ci_cd.pipeline import Pipeline


app = cdk.App()
Pipeline(app, 'CICDStack',  
    env=cdk.Environment(account='349115202997', region='us-east-1'),
    )
# WordReplacerApiStack(app, "WordReplacerApiStack", 
#     env=cdk.Environment(account='349115202997', region='us-east-1'),
#     )
# WordReplacerApiStack(app, "WordReplacerApiStack-Sec_Region", 
#     env=cdk.Environment(account='349115202997', region='us-west-1'),
#     )

# primary_region =cdk.Environment(account='349115202997', region='us-east-1')
# vpc_stack = VPCStack(app, "VPCStack",
#      env=primary_region
#      )

# EKSStack(app, "EKSStack",
#     env=primary_region,  vpc=vpc_stack.vpc
#     )


app.synth()
