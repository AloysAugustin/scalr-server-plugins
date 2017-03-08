#!/usr/bin/env python

import logging
import argparse
import os

from common import *
import install

def setup_parser(parser):
    parser.description = 'Reconfigure an existing Scalr plugin instance'
    parser.add_argument("pluginName", metavar="NAME", help="Reconfigure plugin NAME")
    parser.add_argument("--instanceId", "-i", metavar="INDEX", help="Reconfigure plugin instance INDEX")

def process(args, config):
    plugin_name = args.pluginName

    if not exists(config, plugin_name):
        logging.error("This plugin is not installed in the first place")
        return

    if not args.instanceId:
        plugin_instance = prompt_for_instance(config, plugin_name)
        if not plugin_instance:
            logging.error('Invalid instance selected, aborting')
            return
    else:
        plugin_instance = args.instanceId
        if not plugin_instance in installed_instances(config, plugin_name):
            logging.error('Instance {} of plugin {} doesn\'t exist'.format(plugin_instance, plugin_name))
            return

    install.configure(config, plugin_name, plugin_instance)
