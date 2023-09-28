from botocore.exceptions import ClientError
import boto3
import os


# Define endpoint_url, in prod they should go into a separate config file
ENDPOINT_URL = "http://localstack:4566/000000000000/login-queue"

# Initialize SQS client with the local endpoint and a region
sqs = boto3.client(
      "sqs"
    , endpoint_url=ENDPOINT_URL
    , region_name="us-east-1"
)

# Function to read messages from the SQS queue
def read_messages_from_sqs(max_messages: int = 15) -> list:
    messages = []
    # Stops the outer while loop if no more messages are found:
    keep_looping = True
    try:
        # Request messages from the SQS queue
        response = sqs.receive_message(
            QueueUrl=ENDPOINT_URL,
            MaxNumberOfMessages=max_messages,
            AttributeNames=[
                'ApproximateNumberOfMessages'
            ]
        )
        remaining_messages = int(response["Attributes"]['ApproximateNumberOfMessages'])
        if remaining_messages == 0:
            keep_looping = False
        # Check if the response contains messages
        if "Messages" in response:
            messages = response["Messages"]
            # Delete each message after it's read from the queue
            for message in messages:
                sqs.delete_message(
                    QueueUrl=ENDPOINT_URL,
                    ReceiptHandle=message["ReceiptHandle"]
                )
    except ClientError as e:
        # Print any errors that occur while reading messages from the queue
        print(f"Error reading messages from SQS: {e}")

    return messages, keep_looping