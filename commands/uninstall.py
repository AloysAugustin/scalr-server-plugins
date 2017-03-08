#!/usr/bin/env python

import argparse
import logging

from common import *

def setup_parser(parser):
    parser.description = "Uninstall a Scalr plugin"
    parser.add_argument("pluginName", metavar="name", help="Name of the plugin to uninstall")
    parser.add_argument("--instanceId", "-i", metavar="INDEX", help="Index of the plugin instance to uninstall")
    parser.add_argument("--all", "-a", action="store_true", help="Uninstall all instances of this plugin")

def process(args, config):
    if args.all and not args.instanceId is None:
        logging.error("Invalid arguments, can't have --all and --instanceId at the same time")
        return

    plugin_name = args.pluginName
    if not exists(config, plugin_name):
        logging.error("No instances of this plugin to delete")
        return

    if args.all:
        try:
            remove_plugin(config, plugin_name)
            reload_config()
        except Exception as e:
            logging.error("Error deleting directory %s: %s", plugin_dir(config, plugin_name), e.message)
            return
        logging.info("All instances of plugin %s successfully uninstalled", plugin_name)
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

    remove_instance(config, plugin_name, plugin_instance)
    reload_config()
    logging.info("Successfully uninstalled instance %s of plugin %s.", plugin_instance, plugin_name)
