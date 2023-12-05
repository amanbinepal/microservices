import datetime
import json
import logging
import logging.config
import os
import time
import uuid

import connexion
import yaml
from connexion import NoContent
from pykafka import KafkaClient
from pykafka.exceptions import KafkaException

def health_check():
    """ Health Check Endpoint """
    return '', 200

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s", app_conf_file)
logger.info("Log Conf File: %s", log_conf_file)

def kafka_init():
    max_retries = app_config['kafka']['max_retries']
    retry_wait = app_config['kafka']['retry_wait']
    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.info("Trying to connect to Kafka")
            client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
            topic = client.topics[str.encode(app_config['events']['topic'])]
            producer = topic.get_sync_producer()
            logger.info("Successfully connected to Kafka")
            #remove this
            print("Lol")
            print("Super")
            print("Duper")
            print("cool")
            print("beans")
            return client, producer
        except KafkaException:
            logger.error("Unable to connect to Kafka, retrying in %d seconds", retry_wait)
            time.sleep(retry_wait)
            retry_count += 1
    raise Exception("Maximum retries reached. Failed to connect to Kafka")

kafka_client, producer = kafka_init()

def select_car(body):
    """ Selects car for the user """
    trace_id = uuid.uuid4()
    body['trace_id'] = str(trace_id)
    logger.info("Received event car_choice request with a trace_id of %s", str(trace_id))
    msg = {
        "type": "car_choice",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info("Returned event car_choice response %s with a status code of 201", str(trace_id))
    return NoContent, 201

def select_time(body):
    """ Receives the requested time from the user """
    trace_id = uuid.uuid4()
    body['trace_id'] = str(trace_id)
    logger.info("Received event time_choice request with a trace_id of %s", str(trace_id))
    msg = {
        "type": "schedule_choice",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info("Returned event time_choice response %s with a status code of 201", str(trace_id))
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("BINEPAL2003-CarRequests-1.0.0-swagger.yaml",
            base_path="/receiver",
            strict_validation=True,
            validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080)
