import yaml
from pykafka import KafkaClient
import logging
import logging.config
import json
from connexion import NoContent
import connexion
import swagger_ui_bundle

with open('app_conf.yaml', 'r') as f:
        app_config = yaml.safe_load(f.read())


with open('log_conf.yaml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')

def get_car_selection(index):
    """ Get Car Selection in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving Car Selection at index %d" % int(index))
    try:
        events = []
        #i = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg.get("type") == "car_choice":
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
                events.append(msg)
                if len(events) > int(index):
                #if i == int(index):
                    logger.info("Found Car Selection at index %d" % int(index))
                    return events[int(index)], 200
                    #return msg, 200
            #i = i + 1

    except:
        logger.error("No more messages found")
    logger.error("Could not find Car Selection at index %d" % int(index))
    return { "message": "Not Found"}, 404


def get_car_schedule(index):
    """ Get Car Selection in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving Car Schedule at index %d" % int(index))
    try:
        events = []
        #i = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg.get("type") == "schedule_choice":
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
                events.append(msg)
                #if i == int(index):
                if len(events) > int(index):
                    logger.info("Found Car Schedule at index %d" % int(index))
                    #return msg, 200
                    return events[int(index)], 200
            #i = i + 1

    except:
        logger.error("No more messages found")
    logger.error("Could not find Car Schedule at index %d" % int(index))
    return { "message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
        strict_validation=True,
        validate_responses=True)
if __name__ == "__main__":
    app.run(port=8110)