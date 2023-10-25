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

with open('app_conf.yaml', 'r') as f:
        app_config = yaml.safe_load(f.read())

DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
logger = logging.getLogger('basicLogger')
logger.info(f"Connected to MySQL database at {app_config['datastore']['hostname']}:{app_config['datastore']['port']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

with open('log_conf.yaml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

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

def get_car(timestamp):
        """ Gets the car choice for the user """
        session = DB_SESSION()
        timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        car_choices = session.query(CarChoice).filter(CarChoice.date_created >= timestamp_datetime)
        results_list = []
        for car_choice in car_choices:
                results_list.append(car_choice.to_dict())
        session.close()
        logger.info(f"Query for car choices after {timestamp} returns {len(results_list)} results")
        logger.info(results_list)
        return results_list, 200

def get_schedule(timestamp):
        """ Gets the schedule choice for the user """
        session = DB_SESSION()
        timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        schedule_choices = session.query(ScheduleChoice).filter(ScheduleChoice.date_created >= timestamp_datetime)
        results_list = []
        for schedule_choice in schedule_choices:
                results_list.append(schedule_choice.to_dict())
        session.close()
        logger.info(f"Query for schedule choices after {timestamp} returns {len(results_list)} results")
        logger.info(results_list)
        return results_list, 200
def process_messages():
        """ Process event messages """
        while True:
                try:
                        hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"]) 
                        client = KafkaClient(hosts=hostname)
                        topic = client.topics[str.encode(app_config["events"]["topic"])]
                        consumer = topic.get_simple_consumer(consumer_group=b'event_group',reset_offset_on_start=False,auto_offset_reset=OffsetType.LATEST)
                        for msg in consumer:
                                msg_str = msg.value.decode('utf-8')
                                msg = json.loads(msg_str)
                                payload = msg["payload"]
                                if msg["type"] == "car_choice":
                                        #logger.info("Received car choice request event with a unique id of %s" % msg["id"])
                                        session = DB_SESSION()
                                        car_choice = CarChoice(payload['car_id'], payload['type'], payload['passenger_capacity'], payload['year'], payload['make'], payload['model'], payload['trace_id'])
                                        session.add(car_choice)
                                        session.commit()
                                        session.close()
                                        logger.debug(f"Stored car choice with a trace id of {payload['trace_id']}")
                                elif msg["type"] == "schedule_choice":
                                        #logger.info("Received schedule choice request event with a unique id of %s" % msg["id"])
                                        session = DB_SESSION()
                                        schedule_choice = ScheduleChoice(payload['sched_id'],payload['location'], payload['start_time'], payload['days'], payload['est_kms'], payload['end_time'], payload['trace_id'])
                                        session.add(schedule_choice)
                                        session.commit()
                                        session.close()
                                        logger.debug(f"Stored schedule choice with a trace id of {payload['trace_id']}")
                                        
                                else:
                                        logger.error("Received event with unknown type")
                                consumer.commit_offsets()
                        logger.warn("Shutdown of consumer thread complete")
                except pykafka.exceptions.NoBrokersAvailableError:
                        logger.warn("Unable to connect to Kafka broker. Retrying connection in 5 seconds")
                        time.sleep(5)


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("BINEPAL2003-CarRequests-1.0.0-swagger.yaml",
        strict_validation=True,
        validate_responses=True)
if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)