import tweepy
import boto3
import time


def lambda_handler(event, context):
    for record in event["Records"]:
        dynamodb_data = record["dynamodb"]
        print("-------------------------------------------")

        # Extract and print PostId
        post_id_value = dynamodb_data["Keys"]["PostId"]["S"]
        print("Post ID:", post_id_value)

        # Initialize 'Title' with a default value
        title_value = None

        # Extract and print 'title_value'
        if "NewImage" in dynamodb_data:
            title_value = dynamodb_data["NewImage"].get("Title", {}).get("S")
            print("Title:", title_value)
        else:
            print("NewImage data not found in the record")

        # Initialize 'Link' with a default value
        link_value = None

        # Extract and print 'Link'
        if "NewImage" in dynamodb_data:
            link_value = dynamodb_data["NewImage"].get("Link", {}).get("S")
            print("Link:", link_value)
        else:
            print("NewImage data not found in record")

        print("-------------------------------------------")

        # Send Payload to X
        if title_value is not None and link_value is not None:

            # Initialize SSM client
            ssm_client = boto3.client("ssm", region_name="af-south-1")

            # Retrieve secrets from SSM Parameter store
            consumer_key = ssm_client.get_parameter(
                Name="/x/consumer_key", WithDecryption=True
            )["Parameter"]["Value"]
            consumer_secret = ssm_client.get_parameter(
                Name="/x/consumer_secret", WithDecryption=True
            )["Parameter"]["Value"]
            access_token = ssm_client.get_parameter(
                Name="/x/access_token", WithDecryption=True
            )["Parameter"]["Value"]
            access_token_secret = ssm_client.get_parameter(
                Name="/x/access_token_secret", WithDecryption=True
            )["Parameter"]["Value"]

            client = tweepy.Client(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
            )

            response = client.create_tweet(text=f"{title_value} {link_value}")

            print(f"https://twitter.com/user/status/{response.data['id']}")

            time.sleep(30)

    return "Successfully processed {} records.".format(len(event["Records"]))
