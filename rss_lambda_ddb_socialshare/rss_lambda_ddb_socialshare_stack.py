from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
)
from constructs import Construct


class RssLambdaDdbSocialshareStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB Table
        table = dynamodb.Table(
            self,
            "Posts",
            partition_key=dynamodb.Attribute(
                name="PostId", type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY,
        )
