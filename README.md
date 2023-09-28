# Load data into posgres from SQS (Fetch application)

This repo contains the code for a containerized app that takes sqs messages from a container running an image called `fetchdocker/data-takehome-localstack`, mask certain fields in a way that you can still tell if two records are duplicated and load the resulting record into a database running in another container based in this image `fetchdocker/data-takehome-postgres`.

## Running the app
Be sure to have docker installed locally.
Clone the repo using 

    git clone etreandev/fetch-apconzuelo
into your directory of choice, then build the docker image with

    docker-compose build
run it with

    docker-compose up -d 
this will let you keep using your terminal.
To stop the container run 

    docker-compose down
Take a look at the `docker-compose.yml` file to see how the network is defined so that the containers can talk to each other.


## About etl_app
The main python application works in three steps:
### Extract the messages
Uses the `boto3` library to listen to `http://localstack:4566/000000000000/login-queue` and retrieve the messages, this is accomplished by the function `extract.read_messages_from_sqs` the key part of this function is this:
            response = sqs.receive_message(
            QueueUrl=ENDPOINT_URL,
            MaxNumberOfMessages=max_messages,
        )
Where sqs is an instance of `boto3.client` instanciated for `sqs` connection.
### Transform the messages
Since we want the data to be masked but still have the capacity to differentiate the information I went for hashing the data with functions from the `hashlib` module, in the module `transform` I define this function to apply the mask

    def apply_mask(message: Dict) -> Dict:

        # Initialize masked_data:
        masked_data = {
            "masked_ip"       : hashlib.sha256(message.get("ip","unknown").encode("utf-8")).hexdigest(),
            "masked_device_id": hashlib.sha256(message.get("device_id","unknown").encode("utf-8")).hexdigest(),
            "create_date"     : datetime.now()
        }
    
        # Update the message dict with masked data and return
        return message | masked_data

After this we can transform each message into a tuple ready to be loaded:
    
    (
        message_body_masked["user_id"],
        message_body_masked["device_type"],
        message_body_masked["masked_ip"],
        message_body_masked["masked_device_id"],
        message_body_masked["locale"],
        app_version,
        message_body_masked["create_date"],
    )
### Load each message
This is done via `psycopg2-binary` via the `load` module

    def load_messages(messages, connection_params):
        # SQL query to insert records into the 'user_logins' table
        insert_query = """
        INSERT INTO user_logins (
            user_id,
            device_type,
            masked_ip,
            masked_device_id,
            locale,
            app_version,
            create_date
        ) VALUES %s;
    """ 

        # Connect to the Postgres database
        with psycopg2.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                # Execute the insert query with the records as tuples
                execute_values(cur, insert_query, messages)
            # Commit the transaction
            conn.commit()
## Questions
### How would you deploy this application in production?
First, there are some parameters that I hardcoded that should not, such as the `./cfg/db_config.json` file, the contents of that file should be stored as secrets on the production server, after the repo is deployed to prod, the PROD's `docker-compose` file should be updated to build this image in production.

### What other components would you want to add to make this production ready?
Logging: I don't have any in the current state but this should be critical when deploying.
Swarm: I can see this app needing to scale to accomodate a lot of incoming queries, so horizontal scaling would be necessary for an adequate functioning.
CI/CD pipeline to automate deployment process.

### How can this application scale with a growing dataset.
A) Add more servers to handle volume of queues.
B) Increase DB performance by making it transactional.
D) Add job monitoring like with AWS Glue, if we are dealing with a ton of data we may consider using Kafka to ingest the data.

### How can PII be recovered later on?
We would need to re design this, I would remove the hashing part of the code and instead building a view on top of the table that applied masking, that way we could still access the PII if needed.

### What are the assumptions you made?
1. The source always yield data in the same structure.
2. The etl-app container will only run this app.
3. That the encryption process meets the sufficient security standard.