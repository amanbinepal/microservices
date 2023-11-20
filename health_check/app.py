import yaml
import logging
import logging.config
import requests
import os
import time
from threading import Thread
from flask_cors import CORS
import connexion

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


def check_health(url):
    try:
        response = requests.get(url, timeout=5)
        return "Running" if response.status_code == 200 else "Down"
    except requests.RequestException as e:
        logger.error(f"Failed to reach {url}: {e}")
        return "Down"


def update_services_status():
    while True:
        logger.info("Updating service statuses")
        for service, url in app_config['services'].items():
            status = check_health(url)
            services_status[service] = status
            logger.info(f"Status of {service}: {status}")
        services_status["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        time.sleep(20)

def get_status():
    """ Get Status of All Services """
    logger.info("Health status of all services retrieved")
    return services_status

services_status = {
    "receiver": "Down",
    "storage": "Down",
    "processing": "Down",
    "audit": "Down",
    "last_updated": None
}

Thread(target=update_services_status, daemon=True).start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('openapi.yaml', 
            strict_validation=True, 
            validate_responses=True)

if __name__ == '__main__':
    app.run(port=8120)
