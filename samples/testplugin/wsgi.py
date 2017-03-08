#!/usr/bin/python

import json
import Flask # dependency test
import os
import sys
import test_module

settings = {}

def application(environ, start_response):
    status = '200 OK'
    output = 'Hello {}!\n'.format(settings.get('NAME'))
    output = output + str(environ) + '\n' +  str(test_module.blah()) + '\n' + str(sys.path) + '\n'
    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]

config_file = os.path.join(__file__, 'settings.json')
with open(config_file) as f:
    settings = json.loads(f.read())
