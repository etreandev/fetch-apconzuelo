from extract   import read_messages_from_sqs
from transform import transform_messages
from load      import load_messages
from utils     import get_config_data

def main():
    # Get config for the database
    POSTGRES_CONN = get_config_data()
    # print(POSTGRES_CONN.__str__())

    # Extract data
    sqs_response = read_messages_from_sqs()

    # Transform data to records
    messages = transform_messages(sqs_response)

    # Load to database
    load_messages(messages, POSTGRES_CONN)


if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            continue