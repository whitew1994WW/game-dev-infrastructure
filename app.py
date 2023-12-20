#!/usr/bin/env python3

import aws_cdk as cdk

from game_dev_infrastructure.backend_stack import BackendStack
from game_dev_infrastructure.frontend_stack import FrontendStack
from aws_config import AWS_CONFIG

app = cdk.App()
env = cdk.Environment(region=AWS_CONFIG["REGION"], account=AWS_CONFIG["ACCOUNT_ID"])
cognito_stack = BackendStack(app, "CognitoStack", env=env)
frontend_stack = FrontendStack(app, "FrontendStack", env=env, api_gateway_id=cognito_stack.api_gateway_id)
app.synth()
