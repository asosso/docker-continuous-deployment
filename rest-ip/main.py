"""
flask webapp, registered as a consul client
"""

from flask import Flask, jsonify, request
import logging
import os
from consulclient import register, deregister
from redis import StrictRedis
import datetime
import time

PORT = 8000

API_V1 = '/api/v1/'

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__, static_url_path='')

register(PORT, os.environ['TAGS'].split(',') if os.environ.has_key('TAGS') else None)

REDIS = StrictRedis(host='redis', port=6379, db=0)

# REST endpoints
@app.route(API_V1 + "health", methods=['GET'])
def health():
    """
    healthcheck endpoint
    """
    return jsonify(health=True)

@app.route(API_V1 + "ip")
def index():
    """
    RESTful webservice
    """
    last_ip = REDIS.get('ip')
    time = REDIS.get('time')
    REDIS.set('ip', request.remote_addr)
    REDIS.set('time', datetime.datetime.now().strftime("%H:%M:%S"))
    return jsonify(version='1.0', \
        kind=os.environ['TAGS'], \
        last_ip=last_ip if last_ip else None, \
        time=time if time else None)

@app.errorhandler(Exception)
def handle_generic_error(err):
    """
    default exception handler
    """
    return 'error: ' + str(err), 500

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', debug=True, threaded=True, port=PORT)
    finally:
        deregister()
        time.sleep(15)
        logging.warn('shutting down')
