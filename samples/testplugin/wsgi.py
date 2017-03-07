#!/usr/bin/python
import sys
import test_module
def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!\n'
    output = output + str(environ) + '\n' +  str(test_module.blah()) + '\n' + str(sys.path) + '\n'
    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]
