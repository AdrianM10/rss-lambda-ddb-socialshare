from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _alambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda_event_sources as lambda_event_sources,
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
            stream=dynamodb.StreamViewType.NEW_IMAGE,
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
            description="Invoke Lambda function every 10 minutes",
        )

        # Add 'RSSLambdaDDBFunc' as target to schedule rule
        rule.add_target(targets.LambdaFunction(lambda_ddb_function))

        # Create Lambda function share Post(s) on X
        lambda_share_function = _alambda.PythonFunction(
            self,
            "LambdaShareFunc",
            entry="./lambda_x_share_func",
            function_name="LambdaDDBStreamShare",
            description="SHare post data using DynamoDB Streams to X",
            runtime=_lambda.Runtime.PYTHON_3_12,
            index="lambda_handler.py",
            handler="lambda_handler",
            timeout=Duration.seconds(600),
        )

        # Permissions for LambdaShareFunc to read DynamoDB stream
        table.grant_read_data(lambda_share_function)

        # Permissions for LambdaShareFunc to access SSM Parameter Store
        ssm_policy_statement = iam.PolicyStatement(
            actions=[
                "ssm:GetParameter",
            ],
            resources=["*"],
        )

        lambda_share_function.role.add_to_policy(ssm_policy_statement)

        # DynamoDB stream trigger to 'lambda_share_function'
        lambda_share_function.add_event_source(
            lambda_event_sources.DynamoEventSource(
                table, batch_size=1, starting_position=_lambda.StartingPosition.LATEST
            )
        )

    
