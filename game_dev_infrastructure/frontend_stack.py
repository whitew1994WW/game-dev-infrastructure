from aws_cdk import Stack
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_iam as aws_iam
from aws_cdk import RemovalPolicy
from aws_cdk import aws_cloudfront
from aws_cdk import Duration



class FrontendStack(Stack):
    def __init__(self, scope: Construct, id: str, api_gateway_id: str, **kwargs) -> None:
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


        api_origin = cdk.aws_cloudfront_origins.HttpOrigin(
            f"{api_gateway_id}.execute-api.{self.region}.{cdk.Aws.URL_SUFFIX}",
            origin_path='/prod',
            protocol_policy=cdk.aws_cloudfront.OriginProtocolPolicy.HTTPS_ONLY,
        )

                # CloudFront Security & Headers
        security_headers_beahaviour = aws_cloudfront.ResponseSecurityHeadersBehavior(
            content_type_options=aws_cloudfront.ResponseHeadersContentTypeOptions(
                override=True,
            ),
            frame_options=aws_cloudfront.ResponseHeadersFrameOptions(
                frame_option=aws_cloudfront.HeadersFrameOption.DENY, override=True
            ),
            strict_transport_security=aws_cloudfront.ResponseHeadersStrictTransportSecurity(
                access_control_max_age=Duration.seconds(31536000),
                preload=True,
                include_subdomains=True,
                override=True,
            ),
            xss_protection=aws_cloudfront.ResponseHeadersXSSProtection(
                protection=True,
                mode_block=True,
                override=True,
            ),
            referrer_policy=aws_cloudfront.ResponseHeadersReferrerPolicy(
                referrer_policy=aws_cloudfront.HeadersReferrerPolicy.SAME_ORIGIN,
                override=True,
            ),
        )

        cloudfront_response_headers_policy = aws_cloudfront.ResponseHeadersPolicy(
            self,
            "CloudFrontResponseHeadersPolicy",
            comment="Security response headers for shopping list",
            custom_headers_behavior=aws_cloudfront.ResponseCustomHeadersBehavior(
                custom_headers=[
                    aws_cloudfront.ResponseCustomHeader(
                        header="server", value="time for cupcakes?", override=True
                    )
                ]
            ),
            security_headers_behavior=security_headers_beahaviour,
        )

        # Create a CloudFront distribution with the S3 bucket as the origin
        distribution = cdk.aws_cloudfront.Distribution(self, "FrontendDistribution",
            default_behavior=cdk.aws_cloudfront.BehaviorOptions(
                origin=cdk.aws_cloudfront_origins.S3Origin(website_bucket, origin_access_identity=origin_access_identity),
                viewer_protocol_policy=cdk.aws_cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cdk.aws_cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=cdk.aws_cloudfront.CachePolicy.CACHING_OPTIMIZED
            ),
            additional_behaviors={
                "api/*": cdk.aws_cloudfront.BehaviorOptions(
                    origin=api_origin,
                    allowed_methods=cdk.aws_cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cdk.aws_cloudfront.CachePolicy.CACHING_DISABLED,
                    viewer_protocol_policy=cdk.aws_cloudfront.ViewerProtocolPolicy.HTTPS_ONLY
                )
            },

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