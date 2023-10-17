import connexion
import json
import os
import datetime
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from base import Base
# from car_choice import CarChoice
# from schedule_choice import ScheduleChoice
import yaml
import logging.config
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import uuid
import requests

with open('app_conf.yaml', 'r') as f:
        app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')


def populate_stats():
        """ Periodically update stats """
        logger.info("Start Periodic Processing")
        if os.path.exists(app_config['datastore']['filename']):
                with open(app_config['datastore']['filename'], 'r') as file:
                        stats = json.load(file)
        else:
               stats = {
                "num_car_selections": 0,
                "max_est_kms": 0,
                "num_schedule_choices": 0,
                "max_days_scheduled": 0,
                "last_updated": ""
                }
               with open(app_config['datastore']['filename'], 'w') as file:
                          json.dump(stats, file)
        current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        #print(app_config['eventstore1']['url'])
        #print(app_config['eventstore2']['url'])

        response_car_select = requests.get(app_config['eventstore1']['url'], params={'timestamp': current_time})
        response_schedule_choice = requests.get(app_config['eventstore2']['url'], params={'timestamp': current_time})
        #print(response_car_select)
        #print(response_schedule_choice)


        if response_car_select.status_code == 200 and response_schedule_choice.status_code == 200:
                car_select_events = response_car_select.json()
                #print(car_select_events)
                #print(response_car_select.json())
                schedule_choice_events = response_schedule_choice.json()
                #print(schedule_choice_events)
                #print(response_schedule_choice.json())
                logger.info(f"Received {len(car_select_events)} car selection events and {len(schedule_choice_events)} schedule choice events")

                total_car_selections = len(car_select_events)
                total_schedule_choices = len(schedule_choice_events)
                if schedule_choice_events:
                        max_est_kms = max([event['est_kms'] for event in schedule_choice_events])
                        max_days_scheduled = max([event['days'] for event in schedule_choice_events])
                else:
                        logger.info("No requests to process")
                        max_est_kms = 0
                        max_days_scheduled = 0


                stats['num_car_selections'] += total_car_selections
                stats['num_schedule_choices'] += total_schedule_choices
                stats['max_est_kms'] = max(stats['max_est_kms'], max_est_kms)
                stats['max_days_scheduled'] = max(stats['max_days_scheduled'], max_days_scheduled)
                stats['last_updated'] = current_time

                # updated_stats = {
                #         "num_car_selections": len(car_select_events),
                #         "max_passenger_capacity": max([event['passenger_capacity'] for event in car_select_events]),
                #         "num_schedule_choices": len(schedule_choice_events),
                #         "max_days_scheduled": max([event['days'] for event in schedule_choice_events]),
                #         "last_updated": current_time
                # }        
               
                with open(app_config['datastore']['filename'], 'w') as file:
                        json.dump(stats, file)
                logger.debug(f"Updated stats: {stats}")
        else:
                logger.error(f"Error with GET from event store. Car select status code: {response_car_select.status_code}. Schedule choice status code: {response_schedule_choice.status_code}")
        
        logger.info("End Periodic Processing")

       
def init_scheduler():
        sched = BackgroundScheduler(daemon=True)
        sched.add_job(populate_stats,'interval',seconds=app_config['scheduler']['period_sec'])
        sched.start()

def get_stats():
    logger.info("Request for statistics received.")

    if os.path.exists(app_config['datastore']['filename']):
        with open(app_config['datastore']['filename'], 'r') as file:
            stats = json.load(file)
    else:
        logger.error("Statistics file does not exist.")
        return NoContent, 404, "Statistics do not exist"

    logger.debug(f"Statistics: {stats}")
    logger.info("Request for statistics completed.")
    return stats, 200


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("BINEPAL2003-CarRequests-1.0.0-swagger.yaml",
        strict_validation=True,
        validate_responses=True)
if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)