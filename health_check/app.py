import yaml
import logging
import logging.config
import requests
import os
import time
from threading import Thread
from flask_cors import CORS
import connexion
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json

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

# services_status = {
#     "receiver": "Down",
#     "storage": "Down",
#     "processing": "Down",
#     "audit_log": "Down",
#     "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
# }

try:
    with open('services_status.json', 'r') as json_file:
        services_status = json.load(json_file)
except (FileNotFoundError, json.JSONDecodeError):
    # Initialize with default values if not found
    services_status = {
        "receiver": "Down",
        "storage": "Down",
        "processing": "Down",
        "audit_log": "Down",
        "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }

def check_health(url):
    try:
        response = requests.get(url, timeout=5)
        return "Running" if response.status_code == 200 else "Down"
    except requests.RequestException as e:
        logger.error(f"Failed to reach {url}: {e}")
        return "Down"


def update_services_status():
    #while True:
    logger.info("Updating service statuses")
    for service, url in app_config['services'].items():
        status = check_health(url)
        services_status[service] = status
        logger.info(f"Status of {service}: {status}")
    services_status["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        #time.sleep(app_config['scheduler']['period_sec'])
    
    with open('services_status.json', 'w') as json_file:
        json.dump(services_status, json_file)

def init_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        update_services_status,
        'interval',
        seconds=app_config['scheduler']['period_sec']
    )
    scheduler.start()

def get_status():
    """ Get Status of All Services """
    #update_services_status() #temp commented out, uncomment to revert
    logger.info("Health status of all services retrieved")
    with open('services_status.json', 'r') as json_file:
        current_status = json.load(json_file)
    return current_status, 200 #added 200, remove to revert
    #return services_status, 200 #added 200, remove to revert

# services_status = {
#     "receiver": "Down",
#     "storage": "Down",
#     "processing": "Down",
#     "audit_log": "Down",
#     "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
# }

#Thread(target=update_services_status, daemon=True).start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('openapi.yaml', 
            strict_validation=True, 
            validate_responses=True)

if __name__ == '__main__':
    update_services_status()
    init_scheduler()
    app.run(port=8120)
