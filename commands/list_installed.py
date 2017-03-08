#!/usr/bin/env python

import logging

from common import *

def setup_parser(parser):
    parser.description = 'List installed plugins and instances'

def process(args, config):
    plugins = installed_plugins(config)
    if len(plugins) == 0:
        print('No plugins are currently installed')
        return
    print('Installed instances per plugin are:')
    for plugin in plugins:
        print plugin, ': ', str(installed_instances(config, plugin))
