from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _alambda,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct


class RssLambdaDdbSocialshareStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB Table
        table = dynamodb.Table(
            self,
            "Posts",
            table_name="Posts",
            partition_key=dynamodb.Attribute(
                name="PostId", type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Create Lambda Function that creates records in DynamoDB
        lambda_ddb_function = _alambda.PythonFunction(
            self,
            "RSSLambdaDDBFunc",
            entry="./lambda_rss_ddb_func",
            function_name="rss_lambda_ddb_func",
            description="Lambda function to call RSS feed and store data in DynamoDB",
            runtime=_lambda.Runtime.PYTHON_3_12,
            index="lambda_handler.py",
            handler="lambda_handler",
            timeout=Duration.seconds(300),
        )

        # Permissions for 'RSSLambdaDDBFunc' to access DynamoDB
        table.grant_full_access(lambda_ddb_function)

        # Schedule 'RSSLambdaDDBFunc' to run every 10 minutes
        rule = events.Rule(
            self,
            "ScheduleRule",
            schedule=events.Schedule.cron(
                minute="0/10", hour="*", month="*", week_day="*", year="*"
            ),
            description="Invoke Lambda function every 10 minutes"
        )

        # Add 'RSSLambdaDDBFunc' as target to schedule rule
        rule.add_target(targets.LambdaFunction(lambda_ddb_function))

