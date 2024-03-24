import aws_cdk as core
import aws_cdk.assertions as assertions

from rss_lambda_ddb_socialshare.rss_lambda_ddb_socialshare_stack import RssLambdaDdbSocialshareStack

# example tests. To run these tests, uncomment this file along with the example
# resource in rss_lambda_ddb_socialshare/rss_lambda_ddb_socialshare_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RssLambdaDdbSocialshareStack(app, "rss-lambda-ddb-socialshare")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
