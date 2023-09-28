import json
import hashlib
from typing import List, Dict
from datetime import datetime


# Find out if the message is valid
def is_valid(message: Dict):
    for key in message:
        if message.get(key) is None:
            return False
    return True


# Function to mask PII data in the input dictionary
def apply_mask(message: Dict) -> Dict:

    # Initialize masked_data:
    masked_data = {
        "masked_ip"       : hashlib.sha256(message.get("ip","unknown").encode("utf-8")).hexdigest(),
        "masked_device_id": hashlib.sha256(message.get("device_id","unknown").encode("utf-8")).hexdigest(),
        "create_date"     : datetime.now()
    }
    
    # Update the message dict with masked data and return
    return message | masked_data


# Transform the dict data into a record we can send to postgres
def transform_to_tuple( message_body_masked: Dict ):

    # Convert the app version to an integer by removing the dots
    app_version = int(message_body_masked.get("app_version").replace(".", ""))

    # Return a Tuple ready to be inserted in postgres
    return (
        message_body_masked["user_id"],
        message_body_masked["device_type"],
        message_body_masked["masked_ip"],
        message_body_masked["masked_device_id"],
        message_body_masked["locale"],
        app_version,
        message_body_masked["create_date"],
    )


# Take the SQS response and turn it to a list of records
def transform_messages( sqs_response: List[Dict] )->List:
    # Initialize a list of messages
    messages = []

    # Extract the data from every message:
    for message in sqs_response:
        # Get only the body of each response
        message_body = json.loads(message["Body"])
        # Proceed only if there is any data to process
        if is_valid(message_body):

            # Apply the masking Logic
            message_body_masked = apply_mask(message_body)
            # Create a MessageRecord out of the masked data
            message_tuple = transform_to_tuple(message_body_masked)

            # Append to messages
            messages.append(message_tuple)

    return messages