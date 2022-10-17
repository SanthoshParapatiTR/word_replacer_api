#!/usr/bin/env python3
import os

import aws_cdk as cdk

from word_replacer_api.word_replacer_api_stack import WordReplacerApiStack


app = cdk.App()
WordReplacerApiStack(app, "WordReplacerApiStack", 
    env=cdk.Environment(account='349115202997', region='us-east-1'),
    )

app.synth()
