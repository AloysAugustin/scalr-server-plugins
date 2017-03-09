#!/usr/bin/env python

import logging

def setup_parser(parser):
    parser.description = 'List the plugins available in the repository'

def process(args, config):
    repository = config.getRepository()
    print "Available plugins are:"
    l = repository.list_available_plugins()
    for p in l:
        print p
    return 0
