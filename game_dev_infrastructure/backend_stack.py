"""AWS CDK module for Cognito User Pool and Identity Pool."""
from constructs import Construct
from aws_cdk import (
    aws_cognito as cognito,
    aws_iam as iam,
    aws_s3 as s3,
    Stack,
)
import aws_cdk as cdk


class BackendStack(Stack):
    """AWS CDK stack foyr basic Cognito User Pool and Identity Pool."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """Initialize CognitoStack."""
        super().__init__(scope, construct_id, **kwargs)

        user_pool = self.create_cognito_resources()
        self.create_rest_api_resources(user_pool)

    def create_cognito_resources(self):
        # Create Cognito User Pool with email as username
        user_pool = cognito.UserPool(
            self, "UserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True),
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_digits=True,
                require_lowercase=True,
                require_symbols=True,
                require_uppercase=True,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # Create Cognito User Pool Client and dont generate secret
        user_pool_client = cognito.UserPoolClient(
            self, "UserPoolClient",
            user_pool=user_pool,
            generate_secret=False,
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True
            ),
        )

        # Create Cognito Identity Pool
        identity_pool = cognito.CfnIdentityPool(
            self, "IdentityPool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=user_pool_client.user_pool_client_id,
                    provider_name=user_pool.user_pool_provider_name,
                )
            ],
        )

        # Create Cognito Identity Pool Roles
        authenticated_role = iam.Role(
            self, "CognitoDefaultAuthenticatedRole",
            assumed_by=iam.FederatedPrincipal(
                federated="cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": identity_pool.ref,
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated",
                    },
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity",
            ),
        )

        unauthenticated_role = iam.Role(
            self, "CognitoDefaultUnauthenticatedRole",
            assumed_by=iam.FederatedPrincipal(
                federated="cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": identity_pool.ref,
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "unauthenticated",
                    },
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity",
            ),
        )


        # Create Cognito Identity Pool Roles Mapping
        cognito.CfnIdentityPoolRoleAttachment(
            self, "IdentityPoolRoleAttachment",
            identity_pool_id=identity_pool.ref,
            roles={
                "authenticated": authenticated_role.role_arn,
                "unauthenticated": unauthenticated_role.role_arn,
            },
        )

        # Register outputs
        cdk.CfnOutput(
            self, "UserPoolId",
            value=user_pool.user_pool_id,
        )

        cdk.CfnOutput(
            self, "UserPoolClientId",
            value=user_pool_client.user_pool_client_id,
        )

        cdk.CfnOutput(
            self, "IdentityPoolId",
            value=identity_pool.ref,
        )

        cdk.CfnOutput(
            self, "AuthenticatedRoleName",
            value=authenticated_role.role_name,
        )

        cdk.CfnOutput(
            self, "UnauthenticatedRoleName",
            value=unauthenticated_role.role_name,
        )
        return user_pool
    
    def create_rest_api_resources(self, user_pool):
            
        logs_group = cdk.aws_iam.Group(self, "CloudFrontLogGroup")
        # Create a python Lambda function to handle the API Gateway requests with a maximum timeout of 30 seconds
        handler = cdk.aws_lambda.Function(
            self, 
            "FrontendHandler",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=cdk.aws_lambda.Code.from_asset("lambda_build"),
            timeout=cdk.Duration.seconds(60)
        )
        api_gateway = cdk.aws_apigateway.LambdaRestApi(
            self,
            "ApiGatewayLambda",
            # This might give a type error but it is
            # Completely fine
            handler=handler,
            rest_api_name=f"game-dev-api",
            deploy_options=cdk.aws_apigateway.StageOptions(
                access_log_destination=cdk.aws_apigateway.LogGroupLogDestination(
                    logs_group
                ),
                access_log_format=cdk.aws_apigateway.AccessLogFormat.json_with_standard_fields(
                    http_method=True,
                    ip=True,
                    caller=True,
                    protocol=True,
                    request_time=True,
                    resource_path=True,
                    response_length=True,
                    status=True,
                    user=True,
                ),
            ),
        )


        cdk.CfnOutput(
            self,
            "ApiUrl",
            export_name="ApiUrl",
            value=api_gateway.url,
        )
        stack = cdk.Stack.of(self)
        stack.api_gateway_id = api_gateway.rest_api_id