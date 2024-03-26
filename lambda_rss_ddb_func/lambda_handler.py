import boto3
import requests
import re
import xml.etree.ElementTree as ET


def lambda_handler(event, context):
    posts = get_posts()
    print(posts)

    # Call function to update DynamoDB
    update_ddb(posts)


def get_posts():
    """Retrieve posts from a website's XML feed and parse the data into a list of dictionaries"""
    response = requests.get("https://hypebeast.com/feed")

    tree = ET.ElementTree(ET.fromstring(response.content))
    root = tree.getroot()

    channel = root.find("channel")

    # Create a list to store posts
    posts = []

    # Loop through all items in channel and append to 'posts' list
    for item in channel.findall("item"):

        # Extract post Id from guid
        guid_element = item.find("guid")

        post_data = {
            "PostId": extract_post_id_from_guid(guid_element.text),
            "Title": item.find("title").text,
            "Link": item.find("link").text,
        }
        posts.append(post_data)
    return posts


def extract_post_id_from_guid(guid):
    """Extract post id from guid element in XML"""
    match = re.search(r"\?post=(\d+)", guid)
    if match:
        return match.group(1)
    else:
        return None


def update_ddb(posts):
    """Update DynamoDB Table with post data"""

    ddb = boto3.resource("dynamodb")

    table_name = "Posts"

    table = ddb.Table(table_name)

    # Insert data into DynamoDB Table
    for post in posts:
        table.put_item(Item=post)
        print(f"Successfully put item : {post['PostId']}\n")

    # Scan DynamoDB Table
    scanResponse = table.scan()
    items = scanResponse["Items"]
    for item in items:
        print(f"{item}\n")
