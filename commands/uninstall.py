#!/usr/bin/env python

import argparse
import logging
import os
import shutil
import scalr_server_config as cfg

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
            logging.error("Error deleting directory %s: %s", plugin_dir ,e.message)
            return
        logging.info("All instances of plugin %s successfully uninstalled", plugin_name)
        return

    available_instances = installed_instances(config, plugin_name)
    if not newArgs.instanceId:
        if len(available_instances) == 0:
            logging.info("No available instance for plugin $s. Deleting the enclosing folder.", plugin_name)
            shutil.rmtree(plugin_dir)
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

def exists(config, plugin_name):
    return os.path.isdir(plugin_dir(config, plugin_name))

def plugin_dir(config, plugin_name):
    return os.path.join(config.plugins_base_dir, plugin_name)

def instance_dir(config, plugin_name, plugin_instance):
    return os.path.join(config.plugins_base_dir, plugin_name, plugin_instance)

def installed_instances(config, plugin_name):
    return [s for s in os.listdir(plugin_dir(config, plugin_name))]

def remove_instance(config, plugin_name, plugin_instance):
    shutil.rmtree(instance_dir(config, plugin_name, plugin_instance))
    # Removing associated config
    # TODO: deduplicate code with install.py
    httpd_config_file = os.path.join(config.httpd_config_dir, plugin_name, '{}.conf'.format(plugin_instance))
    os.remove(httpd_config_file)

    if len(installed_instances(config, plugin_name)) == 0:
        remove_plugin(config, plugin_name)

def remove_plugin(config, plugin_name):
    shutil.rmtree(plugin_dir(config, plugin_name))
    httpd_config_dir = os.path.join(config.httpd_config_dir, plugin_name)
    shutil.rmtree(httpd_config_dir)
