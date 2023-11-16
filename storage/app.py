import connexion
import json
import os
import datetime
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from car_choice import CarChoice
from schedule_choice import ScheduleChoice
import yaml
import logging.config
import logging
import uuid
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import time
import pykafka
#from flask_cors import CORS, cross_origin
from sqlalchemy import and_

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

DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
#logger = logging.getLogger('basicLogger')
logger.info(f"Connected to MySQL database at {app_config['datastore']['hostname']}:{app_config['datastore']['port']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

#with open('log_conf.yaml', 'r') as f:
#        log_config = yaml.safe_load(f.read())
#        logging.config.dictConfig(log_config)

# def select_car(body):
#     """ Selects car for the user """
#     session = DB_SESSION()
#     car_choice = CarChoice(body['car_id'], body['type'], body['passenger_capacity'], body['year'], body['make'], body['model'], body['trace_id'])
#     session.add(car_choice)
#     session.commit()
#     session.close()
#     logger.debug(f"Stored car choice with a trace id of {body['trace_id']}")
#     return NoContent, 201

# def select_time(body):
#     """ Receives the requested time from the user """
#     session = DB_SESSION()
#     schedule_choice = ScheduleChoice(body['sched_id'],body['location'], body['start_time'], body['days'], body['est_kms'], body['end_time'], body['trace_id'])
#     session.add(schedule_choice)
#     session.commit()
#     session.close()
#     logger.debug(f"Stored schedule choice with a trace id of {body['trace_id']}")
#     return NoContent, 201

def get_car(start_timestamp, end_timestamp):
        """ Gets the car choice for the user """
        session = DB_SESSION()
        start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        car_choices = session.query(CarChoice).filter(and_(CarChoice.date_created >= start_timestamp_datetime), (CarChoice.date_created < end_timestamp_datetime))
        results_list = []
        for car_choice in car_choices:
                results_list.append(car_choice.to_dict())
        session.close()
        logger.info(f"Query for car choices for start time {start_timestamp} returns {len(results_list)} results")
        logger.info(results_list)
        return results_list, 200

def get_schedule(start_timestamp, end_timestamp):
        """ Gets the schedule choice for the user """
        session = DB_SESSION()
        start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        schedule_choices = session.query(ScheduleChoice).filter(and_(ScheduleChoice.date_created >= start_timestamp_datetime, ScheduleChoice.date_created < end_timestamp_datetime))
        results_list = []
        #print(schedule_choices)
        for schedule_choice in schedule_choices:
                #print(schedule_choice)
                results_list.append(schedule_choice.to_dict())
        session.close()
        logger.info(f"Query for schedule choices after {start_timestamp} returns {len(results_list)} results")
        logger.info(results_list)
        return results_list, 200
def process_messages():
        """ Process event messages """
        max_retries = app_config["kafka"]["max_retries"]
        retry_wait = app_config["kafka"]["retry_wait"]
        hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"]) 
        retry_count = 0
        client = None
        while retry_count < max_retries:
                try:
                        logger.info("Trying to connect to kafka")
                        client = KafkaClient(hosts=hostname)
                        topic = client.topics[str.encode(app_config["events"]["topic"])]
                        consumer = topic.get_simple_consumer(consumer_group=b'event_group',reset_offset_on_start=False,auto_offset_reset=OffsetType.LATEST)
                        logger.info("Successfully connected to kafka")
                        break
                except:
                        logger.error(f"Unable to connect to kafka, retrying in {retry_wait} seconds")
                        time.sleep(retry_wait)
                        retry_count += 1
        if client is None:
                logger.error(f"Unable to connect to kafka after {max_retries} retries")
                return
        #client = KafkaClient(hosts=hostname)
        #topic = client.topics[str.encode(app_config["events"]["topic"])]
        consumer = topic.get_simple_consumer(consumer_group=b'event_group',reset_offset_on_start=False,auto_offset_reset=OffsetType.LATEST)
        session = DB_SESSION()
        for msg in consumer:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                payload = msg["payload"]
                if msg["type"] == "car_choice":
                        #logger.info("Received car choice request event with a unique id of %s" % msg["id"])
                        #session = DB_SESSION()
                        car_choice = CarChoice(payload['car_id'], payload['type'], payload['passenger_capacity'], payload['year'], payload['make'], payload['model'], payload['trace_id'])
                        session.add(car_choice)
                        session.commit()
                        #session.close()
                        logger.debug(f"Stored car choice with a trace id of {payload['trace_id']}")
                elif msg["type"] == "schedule_choice":
                        #logger.info("Received schedule choice request event with a unique id of %s" % msg["id"])
                        #session = DB_SESSION()
                        schedule_choice = ScheduleChoice(payload['sched_id'],payload['location'], payload['start_time'], payload['days'], payload['est_kms'], payload['end_time'], payload['trace_id'])
                        session.add(schedule_choice)
                        session.commit()
                        #session.close()
                        logger.debug(f"Stored schedule choice with a trace id of {payload['trace_id']}")
                        
                else:
                        logger.error("Received event with unknown type")
                consumer.commit_offsets()
        session.close()
        logger.warn("Shutdown of consumer thread complete")


app = connexion.FlaskApp(__name__, specification_dir='')
#CORS(app.app)
#app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("BINEPAL2003-CarRequests-1.0.0-swagger.yaml",
        strict_validation=True,
        validate_responses=True)
if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)