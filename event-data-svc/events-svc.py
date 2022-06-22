
# Copyright(c) 2022, Oracle and / or its affiliates.
# All rights reserved. The Universal Permissive License(UPL), Version 1.0 as shown at http: // oss.oracle.com/licenses/upl
#
#


from importlib.metadata import metadata
import json
import os
from sqlite3 import Timestamp
from flask import Flask, request, Response
import configparser
from decimal import *
import logging
import sys
from datetime import datetime, date, time


# define constants rather than embedding repeated string literals
DT_FORMAT = "%d/%m/%Y, %H:%M:%S"
TYPE_CONST = "type"
ID_CONST = "id"
GEOMETRY = "geometry"
EVPROPERTIES = "properties"
CONTENT_TYPE = "application/json"
GET = "GET"
DELETE = "DELETE"
MINTIME = "mintime"
MAXTIME = "maxtime"
TIME = "time"
TSUNAMI = "tsunami"
STATUS = "status"
MIN = "min"
MAX = "max"
MINMAG = "minmag"
MAXMAG = "maxmag"
MAG = "mag"
MAGTYPE = "magType"
ALERT = "alert"
HOST = 'host'
PORT = 'port'
SERVER = 'server'

app = Flask(__name__)


"""
Load the configuration from the event-svc configuration file.
The configuration needs to include:
  - server
  - host
  - port
  - source data file
"""


def get_config():
    config = configparser.RawConfigParser()
    config.read('event-svc.cfg')

    return config


def load_data(config):
    # Opening JSON file
    filehandle = open(config.get('data', 'file'))
    logger.info("using data set %s", filehandle)
    eventdata = json.load(filehandle)
    filehandle.close()

    return eventdata

# separate the metadata record from the events


def extract_metadata(eventdata):
    for event in eventdata:
        if (event[TYPE_CONST] == "FeatureCollection"):
            return event

    logger.info("No metadata found")
    return None


def convert_time(epoch_time):
    datestr = None
    if (epoch_time != None):
        dateobj = datetime.fromtimestamp(epoch_time/1000)
        datestr = dateobj.strftime(DT_FORMAT)
        logger.debug("epoch time %s is %s", str(epoch_time), datestr)

    return datestr


def cleanse_data(eventdata):
    messages = "cleansing data -\n"
    cleandata = []

    for event in eventdata:
        if (event[TYPE_CONST] == "FeatureCollection"):
            messages += "Located meta data entry\n"
        elif (event[TYPE_CONST] == "Feature"):
            properties = event[EVPROPERTIES]
            properties[ID_CONST] = event[ID_CONST]
            properties[GEOMETRY] = event[GEOMETRY]

            # convert milliseconds from epoch to a string representation
            properties[TIME] = convert_time(properties[TIME])
            properties['updated'] = convert_time(properties["updated"])

            cleandata.append(properties)
        else:
            messages += "Unexpected event type " + event[TYPE_CONST] + "\n"

    logger.debug(messages)

    return cleandata


@ app.route('/health', strict_slashes=False)
def health():
    status = dict()

    if (eventdata != None):
        status['event-data'] = len(eventdata)
    status['config'] = config

    json = json.dumps(status, indent=2, sort_keys=False)
    logger.debug(json)
    return json


@ app.route('/test', strict_slashes=False)
def test():
    return "confirming, test ok"


@ app.route('/metadata', strict_slashes=False)
def get_metadata():
    return metadata


def string_element(properties, testvalue, attributename):
    result = False
    value = properties[attributename]
    if (value != None) and (testvalue != None):
        value = str(value)
        value = value.lower()
        testvalue = str(testvalue)
        testvalue = testvalue.lower()

        result = (testvalue == value)

    return result


def boolean_element(properties, testvalue, attributename):
    result = False
    value = properties[attributename]
    if (value != None) and (testvalue != None):
        value = str(value)
        value = value.lower()
        testvalue = str(testvalue)
        testvalue = testvalue.lower()
        if (testvalue == "true"):
            testvalue = "1"
        if (testvalue == "false"):
            testvalue = "0"

        logger.debug("valuating %s against %s for %s",
                     attributename, testvalue, str(value))
        result = (testvalue == value)

    return result


def numeric_element(properties, testvalue, attributename):
    result = False
    actualattributename = attributename
    if attributename in OPERATOR_CRITERIA_MAP:
        actualattributename = OPERATOR_CRITERIA_MAP[attributename]

    value = properties[actualattributename]
    if (value != None) and (testvalue != None):
        try:
            value = Decimal(value)
            testvalue = Decimal(testvalue)

        except ValueError:
            logger.debug("Value not numeric " +
                         str(value) + " or " + testvalue)

        if attributename.startswith(MIN):
            result = (value <= testvalue)
        elif attributename.startswith(MAX):
            result = (value >= testvalue)
        else:
            result = (value == testvalue)

    return result


OPERATOR_CRITERIA_MAP = {MINTIME: TIME,
                         MAXTIME: TIME,
                         MINMAG: MAG,
                         MAXMAG: MAG}

CRITERIA_MAP = {MINTIME: numeric_element,
                MAXTIME: numeric_element,
                TIME: numeric_element,
                TSUNAMI: boolean_element,
                STATUS: string_element,
                TYPE_CONST: string_element,
                MINMAG: numeric_element,
                MAXMAG: numeric_element,
                MAG: numeric_element,
                MAGTYPE: string_element,
                ALERT: string_element}


@app.route('/event', methods=[GET], strict_slashes=False)
def get_event():
    logger.debug("Get event - args are %s", str(request.args))
    response_code = 404

    matched_event = None
    event_id = ''
    if (request.args != None) and (len(request.args) > 0) and ID_CONST in request.args:
        event_id = request.args.get(ID_CONST)
        for event in eventdata:
            if (event[ID_CONST] != None) and (event[ID_CONST] == event_id):
                matched_event = event
                response_code = 200
                break

    else:
        logger.debug("No id set - returning 204 with empty string")
        response_code = 404

    responsestr = ""
    if (matched_event != None) and len(matched_event) > 0:
        responsestr = json.dumps(matched_event, indent=2, sort_keys=True)

    else:
        logger.info("No Id match for " + event_id)
        responsestr = ''

    response = Response(response=responsestr,
                        status=response_code,
                        content_type=CONTENT_TYPE)
    logger.debug("Returning response object:" + str(response))

    return response


@app.route('/event', methods=[DELETE], strict_slashes=False)
def delete_event():
    logger.debug("delete event - args are %s", str(request.args))

    response_code = 410
    event_id = ''
    logger.debug("Pre-deletion count - %d", len(eventdata))
    if (request.args != None) and (len(request.args) > 0) and ID_CONST in request.args:
        # special case
        event_id = request.args[ID_CONST]
        for event in eventdata:
            if (event[ID_CONST] != None) and (event[ID_CONST] == event_id):
                eventdata.remove(event)
                response_code = 202
                break
    else:
        logger.debug("No delete criteria set returning everything")

    record_count = len(eventdata)
    logger.debug("POST-deletion count - %d", record_count)

    response = Response(response=json.dumps(record_count, indent=2),
                        status=response_code,
                        content_type=CONTENT_TYPE)
    return response


def match_list_to_string(matchedevents):
    responsestr = ""
    if len(matchedevents) > 0:
        responsestr = json.dumps(matchedevents, indent=2, sort_keys=True)

    return responsestr


def create_search_criteria(args):
    searchcriteria = None

    if (args != None) and (len(args) > 0):
        # build the search criteria
        for arg in args:
            # logger.debug("arg evaluating " + arg)
            if searchcriteria == None:
                searchcriteria = dict()

            searchcriteria[arg] = args.get(arg)

    logger.debug("Search criteria is %s", str(searchcriteria))
    return searchcriteria


def apply_criteria(searchcriteria, properties):
    matched = True
    for criteria in searchcriteria:
        if criteria in CRITERIA_MAP:
            matched = CRITERIA_MAP[criteria](
                properties, searchcriteria.get(criteria), criteria)
        else:
            logger.warning("unknown search criteria - " + criteria)
        if matched == False:
            break
            # didn't fail any of the search criteria

    return matched


@app.route('/events', methods=[GET], strict_slashes=False)
def get_events():
    logger.debug("Get events - args are %s", str(request.args))
    response_code = 200

    matchedevents = list()
    searchcriteria = create_search_criteria(request.args)

    if searchcriteria != None:
        # examine each event
        for event in eventdata:
            if (apply_criteria(searchcriteria, event)):
                logger.debug("match for " + str(event))
                matchedevents.append(event)

    else:
        logger.debug("No search criteria set returning everything")
        matchedevents = eventdata

    logger.debug("Get events found %d matches", len(matchedevents))
    responsestr = match_list_to_string(matchedevents)
    logger.debug("Get events returning %s", responsestr)

    return Response(response=responsestr,
                    status=response_code,
                    content_type=CONTENT_TYPE)


@app.route('/latestEvent', methods=[GET], strict_slashes=False)
def get_latest_event():
    logger.debug("Get latest event ")

    response_code = 404
    latest_event = None
    latest_event_dtg = None

    for event in eventdata:
        current_event_dtg_str = event.get('time')

        if (current_event_dtg_str != None):
            current_event_dtg = datetime.strptime(
                current_event_dtg_str, DT_FORMAT)

            if (latest_event_dtg == None) or (current_event_dtg > latest_event_dtg):
                latest_event_dtg = current_event_dtg
                latest_event = event
                response_code = 200

    responsestr = json.dumps(latest_event, indent=2, sort_keys=True)
    logger.debug(responsestr)

    response = Response(response=responsestr,
                        status=response_code,
                        content_type=CONTENT_TYPE)
    return (response)


@ app.route('/raw', methods=[GET], strict_slashes=False)
def raw():
    pretty_str = json.dumps(eventdata, indent=2, sort_keys=True)
    logger.debug(pretty_str)
    logger.debug("Record count="+str(len(eventdata)))
    return (pretty_str)


@ app.errorhandler(404)
def page_not_found(error):
    logger.warning("Error handler caught request : %s", str(request.data))
    return 'URL not found', 404

# start the app up


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.debug("========== Preparing ==========")

config = get_config()
os.environ[HOST] = config.get(SERVER, HOST)
os.environ[PORT] = config.get(SERVER, PORT)
eventdata = load_data(config)
metadata = extract_metadata(eventdata)
eventdata = cleanse_data(eventdata)
pretty_events_str = json.dumps(eventdata, indent=2, sort_keys=True)
pretty_metadata_str = json.dumps(metadata, indent=2, sort_keys=True)


logger.debug("Cleansed data:" + pretty_events_str)
logger.debug("==========")
logger.debug("metadata data:" + pretty_metadata_str)
logger.debug("========== ready ==========")

if __name__ == '__main__':
    app.run(debug=config.getint(SERVER, 'debug'),
            port=config.getint(SERVER, PORT),
            host=config.get(SERVER, HOST))
