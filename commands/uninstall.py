#!/usr/bin/env python

import argparse
import logging
import scalr_server_config as cfg

from common import *

def process(args, loglevel):
    parser = argparse.ArgumentParser(
        description="Uninstall a Scalr plugin"
    )
    parser.add_argument("pluginName", metavar="NAME", help="Uninstall plugin NAME")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbosity")
    parser.add_argument("--instanceId", "-i", metavar="INDEX", help="Uninstall plugin instance INDEX")
    parser.add_argument("--all", "-a", action="store_true", help="Uninstall all plugin instances")
    newArgs = parser.parse_args(args=args)
    config = cfg.ScalrServerPluginsConfiguration()
    if not config.checkConfig():
        logging.error("Configuration is incorrect")
        return
    if newArgs.all and not newArgs.instanceId is None:
        logging.error("Invalid arguments, can't have --all and --instanceId at the same time")
        return

    plugin_name = newArgs.pluginName

    if not exists(config, plugin_name):
        logging.error("No instances of this plugin to delete")
        return

    if newArgs.all:
        try:
            remove_plugin(config, plugin_name)
        except Exception as e:
            logging.error("Error deleting directory %s: %s", plugin_dir(config, plugin_name), e.message)
            return
        logging.info("All instances of plugin %s successfully uninstalled", plugin_name)
        return

    available_instances = installed_instances(config, plugin_name)
    if not newArgs.instanceId:
        if len(available_instances) == 0:
            logging.info("No available instance for plugin %s. Deleting the enclosing folder.", plugin_name)
            remove_plugin(config, plugin_name)
            return
        plugin_instance = available_instances[0]
        print 'Available instances for plugin: %s' % available_instances
        print 'Please choose one to delete [=%s]' % plugin_instance
        s = raw_input('-->')
        if len(s) > 0 and s in available_instances:
            plugin_instance = s
        elif len(s) > 0:
            logging.error("Wrong instance chosen.")
            return
        remove_instance(config, plugin_name, plugin_instance)
        logging.info('Successfully uninstalled instance %s of plugin %s.', plugin_instance, plugin_name)
    else:
        plugin_instance = newArgs.instanceId
        if not plugin_instance in available_instances:
            logging.error('Instance {} of plugin {} doesn\'t exist'.format(plugin_instance, plugin_name))
            return
        remove_instance(config, plugin_name, plugin_instance)
        logging.info("Successfully uninstalled instance %s of plugin %s.", plugin_instance, plugin_name)
