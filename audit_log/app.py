import json
import logging
import logging.config
import os
import connexion
from flask_cors import CORS
import yaml
from pykafka import KafkaClient

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

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

def get_car_selection(index):
    """ Get Car Selection in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving Car Selection at index %d" % int(index))
    try:
        events = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg.get("type") == "car_choice":
                events.append(msg)
                if len(events) > int(index):
                    logger.info("Found Car Selection at index %d" % int(index))
                    return events[int(index)], 200

    except:
        logger.error("No more messages found")
    logger.error("Could not find Car Selection at index %d" % int(index))
    return { "message": "Not Found"}, 404


def get_car_schedule(index):
    """ Get Car Selection in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving Car Schedule at index %d" % int(index))
    try:
        events = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg.get("type") == "schedule_choice":
                events.append(msg)
                if len(events) > int(index):
                    logger.info("Found Car Schedule at index %d" % int(index))
                    return events[int(index)], 200

    except:
        logger.error("No more messages found")
    logger.error("Could not find Car Schedule at index %d" % int(index))
    return { "message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml",
        base_path="/audit_log",
        strict_validation=True,
        validate_responses=True)
if __name__ == "__main__":
    app.run(port=8110)