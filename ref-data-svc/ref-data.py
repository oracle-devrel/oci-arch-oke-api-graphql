# Copyright(c) 2022, Oracle and / or its affiliates.
# All rights reserved. The Universal Permissive License(UPL), Version 1.0 as shown at http: // oss.oracle.com/licenses/upl
#
# useful resources
# https://flask.palletsprojects.com/en/2.1.x/

from flask import Flask, request, Response
import configparser
import json
import os
import logging
import sys

JSON_TYPE = "application/json"
GET = 'GET'
DELETE = 'DELETE'
CODE = 'code'
NAME = "name"
AKA = 'aka'

app = Flask(__name__)


def getconfig():
    config = configparser.RawConfigParser()
    config.read('ref-data-svc.cfg')

    return config


def loaddata(config):

    # Opening JSON file
    filehandle = open(config.get('providers', 'file'))
    refdata = json.load(filehandle)
    filehandle.close()

    return refdata


def prep_provider_alternates(providerdata):
    updatedprovider = providerdata.copy()

    logger.debug(
        "provider count before setting up alternate replicas=" + str(len(providerdata)))
    for provider in providerdata:
        if AKA in provider:
            aka_list = provider[AKA]
            for aka in aka_list:
                newprovider = provider.copy()
                newprovider[CODE] = aka
                updatedprovider.append(newprovider)

    logger.debug("UPDATED provider count=" + str(len(updatedprovider)))

    return updatedprovider


def get_provider_by(id, element):
    logger.debug("looking for %s in element %s", id, element)
    identified_provider = None
    lower_id = id.lower()

    for provider in providerdata:
        if (provider[element].lower() == lower_id):
            identified_provider = provider
            break

    if (identified_provider == None):
        logger.info("Couldn't locate %s", id)
    return identified_provider


def getCodeList(codes):
    codes_tokens = codes.split(",")
    codes_list = []
    logger.debug("Code tokens=,%s", str(codes_tokens))

    for token in codes_tokens:
        token_stripped = None
        if (token != None):
            token_stripped = token.strip()

        if (token_stripped != None) and (token_stripped != '') and (token_stripped != ','):
            codes_list.append(token_stripped)

    return codes_list


@ app.route('/providers', methods=[GET], strict_slashes=False)
def get_providers():
    response_elements = []
    responsestr = None
    response_code = 404

    logger.debug("Get providers for: %s", str(request.args))
    if (request.args != None) and (len(request.args) > 0) and "codes" in request.args:
        codes = getCodeList(request.args["codes"])
        logger.debug("Locate record with codes: %s", str(codes))

        if (codes != None):
            for code in codes:
                logger.debug("looking for %s", str(code))
                response_element = get_provider_by(
                    code, CODE)
                if (response_element != None):
                    response_elements.append(response_element)

    # build the response string
    logger.debug("Located: %s", str(response_elements))
    if (len(response_elements) > 0):
        responsestr = json.dumps(
            response_elements, indent=2, sort_keys=False)
        response_code = 200

    logger.debug("get provides %s returning:\n%s", str(codes), str)
    response = Response(response=responsestr,
                        status=response_code,
                        content_type=JSON_TYPE)
    return response


@ app.route('/provider', methods=[GET], strict_slashes=False)
def get_provider():
    ref_element = None
    responsestr = None
    response_code = 404

    if (request.args != None) and (len(request.args) > 0):
        for arg in request.args:
            if (arg == CODE):
                ref_element = get_provider_by(request.args[CODE], CODE)
            elif (arg == NAME):
                ref_element = get_provider_by(
                    request.args[NAME], NAME)

    if (ref_element != None):
        responsestr = json.dumps(ref_element, indent=2, sort_keys=False)
        response_code = 200

    response = Response(response=responsestr,
                        status=response_code,
                        content_type=JSON_TYPE)
    return response


def check_akas(aka_list, request_id):
    # if we haven't got the specific provider let's ensure the entry
    #  isn't being referenced in the aka
    for aka_entry in aka_list:
        aka_entry_lower = aka_entry.lower()
        if request_id == aka_entry_lower:
            aka_list.remove(aka_entry)
            logger.debug("removed an aka entry")
    return aka_list


@ app.route('/provider', methods=[DELETE], strict_slashes=False)
def delete_provider():
    response_code = 410
    request_id = None

    logger.debug("PRE-deletion count - %d", len(providerdata))

    if (request.args != None) and (len(request.args) > 0):
        request_id = request.args[CODE]
        logger.debug(request_id)

    if (request_id != None):
        request_id = request_id.lower()

        for provider_entry in providerdata:
            if (provider_entry[CODE].lower() == request_id):
                providerdata.remove(provider_entry)
                response_code = 200
            elif AKA in provider_entry:
                provider_entry[AKA] = check_akas(
                    provider_entry[AKA], request_id)

    record_count = len(providerdata)
    logger.debug("POST-deletion count - %d", record_count)

    response = Response(response=json.dumps(record_count, indent=2),
                        status=response_code,
                        content_type=JSON_TYPE)
    return response


@ app.route('/test/',  methods=[GET], strict_slashes=False)
def test():
    return "confirming, test ok"


@ app.route('/health/',  methods=[GET], strict_slashes=False)
def health():
    status = dict()
    status['provider-data'] = len(providerdata)
    status['config'] = config

    json = json.dumps(status, indent=2, sort_keys=False)
    logger.debug(json)
    return json


@ app.errorhandler(404)
def page_not_found(error):
    logger.warning("Error handler caught request : %s", str(request.data))
    return 'URL not found', 404


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.debug("========== Preparing ==========")

config = getconfig()
os.environ['host'] = config.get('server', 'host')
os.environ['port'] = config.get('server', 'port')

logger.debug("debug ==>" + str(config.get('server', 'debug')))
logger.debug("port ==>" + str(config.getint('server', 'port')))
logger.debug("host ==>" + config.get('server', 'host'))

providerdata = loaddata(config)
providerdata = prep_provider_alternates(providerdata)

logger.debug("========== ready ==========")

if __name__ == '__main__':
    app.run(debug=config.getint('server', 'debug'),
            port=config.getint('server', 'port'),
            host=config.get('server', 'host'))
