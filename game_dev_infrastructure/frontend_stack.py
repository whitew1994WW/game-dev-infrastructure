from aws_cdk import Stack
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_iam as aws_iam
from aws_cdk import RemovalPolicy



class FrontendStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an Origin Access Identity for CloudFront
        origin_access_identity = cdk.aws_cloudfront.OriginAccessIdentity(self, "OAI")

        # Create an S3 bucket for the React app, allow all headers
        website_bucket = s3.Bucket(self, "ReactAppBucket",
            website_index_document="index.html",
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Adjust as necessary
            auto_delete_objects=True,
            public_read_access=True
        )

        # Create an S3 bucket for the CloudFront logs with ACLs
        logs_bucket = s3.Bucket(self, "CloudFrontLogBucket",
            removal_policy=RemovalPolicy.DESTROY, # Or use RETAIN as per your use case
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            access_control=s3.BucketAccessControl.LOG_DELIVERY_WRITE # This is important for log delivery
        )

        # Grant the OAI permission to read the S3 bucket
        website_bucket.grant_read(origin_access_identity)

        # Create API Gateway
        api = cdk.aws_apigateway.RestApi(self, "FrontendApi",
            rest_api_name="FrontendApi",
            description="This is the Frontend API Gateway"
        )

        # Create a python Lambda function to handle the API Gateway requests
        handler = cdk.aws_lambda.Function(
            self, 
            "FrontendHandler",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=cdk.aws_lambda.Code.from_asset("lambda_code"),
            environment={
                "BUCKET": website_bucket.bucket_name
            }
        )
        # Create a CloudFront distribution with the S3 bucket as the origin
        distribution = cdk.aws_cloudfront.Distribution(self, "FrontendDistribution",
            default_behavior=cdk.aws_cloudfront.BehaviorOptions(
                origin=cdk.aws_cloudfront_origins.S3Origin(website_bucket, origin_access_identity=origin_access_identity),
                viewer_protocol_policy=cdk.aws_cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cdk.aws_cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=cdk.aws_cloudfront.CachePolicy.CACHING_OPTIMIZED
            ),
            default_root_object="index.html"
        )

        cdk.CfnOutput(
            self,
            "BucketName",
            export_name="FrontendBucketName",
            value=website_bucket.bucket_name,
        )

        cdk.CfnOutput(
            self,
            "BucketArn",
            export_name="FrontendBucketArn",
            value=website_bucket.bucket_arn,
        )

        cdk.CfnOutput(
            self,
            "BucketUrl",
            export_name="FrontendBucketURL",
            value=website_bucket.s3_url_for_object(),
        )

        cdk.CfnOutput(
            self,
            "DistributionId",
            export_name="FrontendDistributionId",
            value=distribution.distribution_id,
        )
        
        cdk.CfnOutput(
            self,
            "DomainName",
            export_name="FrontendDomainName",
            value=distribution.domain_name,
        )