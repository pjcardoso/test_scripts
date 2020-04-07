#!/usr/bin/python
import requests
import json
import time
import calendar
from sys import argv
import datetime
import argparse
import logging
import yaml
import csv


# loadYaml reads data from a config yml file
def loadYaml():
    try:
        with open('testerscript1-config.yml', 'r') as y:
            stream = y.read()
        data = yaml.load(stream)
        return data
    except Exception as e:
        log.error('Configuration file is missing.')
        sys.exit(1)

# reads lines from a given test file and returns a list
def readTests(filename):
    tests = []
    with open(filename, 'r') as file:
        for line in file:
            data = line.strip().split(',')
            tests.append(data)
    return tests

# urlCall creates and performs the http post request to environment to be tested
def urlTestCall(internalCode, status, message, result_status, result_responseCode, result_cancellationReason ):
    env_api = 'http://%s/%s/%s' % (data[project]['env_host'], data[project]['env_uri'], '1234-4321-1234')
    #dump test body, this will not interfer in results
    body = '{ "data": { "pdv_custCode": "SP10_TLTOTI_TL0155_A001", "pdv_stateCode": "SP", "customer_socialSecNo": "19566162847", "customer_name": "ADRIANA ANTUNES DE CAMPOS", "customer_motherName": "ANGELA MARIA LAURIA DE CAMPOS", "customer_birthDate": "26/02/1977", "contract_msisdn": "21982333333", "customer_address_postalCode": "13190000", "plan_segment": "CONTROLE" } }' 
    # actual request
    key = '%s%s%s' % (status,internalCode, message)
    try:
        res = requests.post(env_api, data=body)
        if res.status_code != 200:
            print('Test eligibility failed | test=\"'+ key+'\" | HTTP_STATUS_CODE='+str(res.status_code))
            logging.error('Test eligibility failed | test=\"'+ key + '\" | HTTP_STATUS_CODE='+str(res.status_code))
        else:
            print('Test eligibility for test=\"'+ key + '\" sent successfully | HTTP_STATUS_CODE='+str(res.status_code))
            logging.info('Test eligibility for test=\"'+ key + '\" sent successfully | HTTP_STATUS_CODE='+str(res.status_code))
            result2 = res.text
            #result3 = result2.decode('utf8').text
            result = res.json()
            #print(result)
            status_check = 'WRONG'
            status_responseCode = 'WRONG'
            status_cancellation_reason = 'WRONG'
            #cr = result['data']['cancellation_reason'].encode('utf8')
            if result_status == result['status']:
               status_check = 'PASSED' 
            if result_responseCode == result['responseCode']:
               status_responseCode = 'PASSED' 
            if result_cancellationReason == result['data']['cancellation_reason'].encode('utf8'):
               status_cancellation_reason = 'PASSED' 
            print('test results status: expected->{} result->{} overwall->{}'.format(result_status, result['status'], status_check))
            print('test results responseCode: expected->{} result->{} overwall->{}'.format(result_responseCode, result['responseCode'], status_responseCode))
            print('test results cancellation_reason: expected->{} result->{} overwall->{}'.format(result_cancellationReason,result['data']['cancellation_reason'].encode('utf8'), status_cancellation_reason))
            print('\n')
    except requests.exceptions.RequestException as e:
        print(e)
        logging.error(e)

# urlCall creates and performs the http post request to simulator environment to set desired response
def urlPrepSim(internalCode, status, message):
    sim_api = 'http://%s/%s' % (data[project]['sim_host'], data[project]['sim_uri'])
    if status != 200:
	body = '{ "id" : "eaa1c88f-d9ec-4523-89fd-1186444fd595", "request" : { "urlPathPattern" : "/b2b2c/v5/eligibility", "method" : "POST" }, "response" : { "status" : 200, "body" : "{\\"type\\":\\"error\\",\\"message\\":\\"%s\\",\\"internalCode\\":\\"%s\\",\\"transactionId\\":\\"Id-d020615e974dccc6d9ef720e\\",\\"status\\":\\"%s\\"}", "headers" : { "Content-Type" : "application/json" } }, "uuid" : "eaa1c88f-d9ec-4523-89fd-1186444fd595", "priority" : 1 }' % (message, internalCode, status)
    else:
    	body = '{ "id" : "eaa1c88f-d9ec-4523-89fd-1186444fd595", "request" : { "urlPathPattern" : "/b2b2c/v5/eligibility", "method" : "POST" }, "response" : { "status" : 200, "body" : "{\\"type\\":\\"error\\",\\"message\\":\\"%s\\",\\"transactionId\\":\\"Id-d020615e974dccc6d9ef720e\\",\\"status\\":\\"%s\\",\\"approval\\":[{\\"reasonCode":\\"%s\\",\\"description\\":\\"LOW\\"}]}", "headers" : { "Content-Type" : "application/json" } }, "uuid" : "eaa1c88f-d9ec-4523-89fd-1186444fd595", "priority" : 1 }' % (message, status, internalCode)
    # actual request
    try:
        res = requests.post(sim_api, data=body)
        if res.status_code != 201:
            print('prepSim failed | body=' + body + ' | status=' + status + '  | message=' + message + ' | HTTP_STATUS_CODE='+str(res.status_code))
            logging.error('prepsim failed | HTTP_STATUS_CODE='+str(res.status_code))
        else:
            print('prepSim sent successfully | HTTP_STATUS_CODE='+str(res.status_code))
            logging.info('prepSim sent successfully | HTTP_STATUS_CODE='+str(res.status_code))
    except requests.exceptions.RequestException as e:
        print(e)
        logging.error(e)



if __name__ == '__main__':
    logging.basicConfig(filename='tester_script_1.log',
                        format='%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s', filemode='w', level=logging.DEBUG)
    argparser = argparse.ArgumentParser('tester_script_1.py')
    argparser.add_argument(
        '--project', help='Specify the project', required=True)
    argparser.add_argument(
        '--input-file', help='Test csv Input file to be used', required=True)
    argparser.add_argument(
        '--only-failed', help='Prints only failed requests', required=False)
    parameters = argparser.parse_args()
    filename = parameters.input_file
    project = parameters.project

    print("Starting at " + time.strftime("%c") + ' UTC')
    logging.info("Starting at " + time.strftime("%c") + ' UTC')
    
    print("Reading config.yml file for parameters...")
    logging.info("Reading config.yml file for parameters...")
    data = loadYaml()
     
    print("Reading tests from the file...")
    logging.info("Reading tests from the file")

    count = 0
    tests = readTests(filename)

    print("Processing tests...")
    logging.info("Processing tests")

    for test in tests:
        time.sleep(1)
        status = test[0]
        internalCode = test[1]
        message = test[2]
        result_status = test[3]
        result_responseCode = test[4]
        result_cancellationReason = test[5]
        urlPrepSim(internalCode, status, message)
        urlTestCall(internalCode, status, message,result_status, result_responseCode, result_cancellationReason)

    print("Finished at " + time.strftime("%c") + ' UTC')
    logging.info("Finished at " + time.strftime("%c") + ' UTC')
