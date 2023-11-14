import connexion
import json
import os
import datetime
import yaml
from connexion import NoContent
import requests
import logging.config
import logging
import uuid
from pykafka import KafkaClient
from pykafka.exceptions import KafkaException
import time
#from flask_cors import CORS, cross_origin

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open('app_conf.yaml', 'r') as f:
        app_config = yaml.safe_load(f.read())


with open('log_conf.yaml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

#with open('app_conf.yaml', 'r') as f:
#        app_config = yaml.safe_load(f.read())

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
                        return client,producer
                except KafkaException:
                        logger.error(f"Unable to connect to Kafka, retrying in {retry_wait} seconds")
                        time.sleep(retry_wait)
                        retry_count += 1
        raise Exception("Maximum retries reached. Failed to connect to Kafka")

kafka_client,producer = kafka_init()
#topic = kafka_client.topics[str.encode(app_config['events']['topic'])]
#producer = topic.get_sync_producer()

def select_car(body):
    """ Selects car for the user """
    trace_id = uuid.uuid4()
    body['trace_id'] = str(trace_id)
    logger.info(f'Recieved event car_choice request with a trace_id of {str(trace_id)}')
    #headers = {'Content-Type': 'application/json'}

    #client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    #topic = client.topics[str.encode(app_config['events']['topic'])]
    #producer = topic.get_sync_producer()
    msg = {
       "type": "car_choice",
       "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
       "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info(f'Returned event car_choice response {str(trace_id)} with a status code of 201')
    
    return NoContent, 201

    
#     response_select = requests.post(app_config['eventstore1']['url'], json=body, headers=headers)
#     logger.info(f'Returned event car_choice response {str(trace_id)} with a status code of {response_select.status_code}')
#     return NoContent, response_select.status_code


def select_time(body):
    """ Receives the requested time from the user """
    trace_id = uuid.uuid4()
    body['trace_id'] = str(trace_id)
    logger.info(f'Recieved event time_choice request with a trace_id of {str(trace_id)}')
    #headers = {'Content-Type': 'application/json'}

    #client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    #topic = client.topics[str.encode(app_config['events']['topic'])]
    #producer = topic.get_sync_producer()
    msg = {
       "type": "schedule_choice",
       "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
       "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info(f'Returned event time_choice response {str(trace_id)} with a status code of 201')
    
    return NoContent, 201  # Hardcoded status code

    
#     response_sched = requests.post(app_config['eventstore2']['url'], json=body, headers=headers)
#     logger.info(f'Returned event time_choice response {str(trace_id)} with a status code of {response_sched.status_code}')
#     return NoContent, response_sched.status_code

app = connexion.FlaskApp(__name__, specification_dir='')
#CORS(app.app)
#app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("BINEPAL2003-CarRequests-1.0.0-swagger.yaml",
        strict_validation=True,
        validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080)