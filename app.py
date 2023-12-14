#!/usr/bin/env python3

import aws_cdk as cdk

from game_dev_infrastructure.cognito_stack import CognitoStack
from game_dev_infrastructure.frontend_stack import FrontendStack
from aws_config import AWS_CONFIG

app = cdk.App()
env = cdk.Environment(region=AWS_CONFIG["REGION"], account=AWS_CONFIG["ACCOUNT_ID"])
CognitoStack(app, "CognitoStack", env=env)
FrontendStack(app, "FrontendStack", env=env)
app.synth()
