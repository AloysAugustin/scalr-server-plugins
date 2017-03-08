#!/usr/bin/env python

from common import *

def setup_parser(parser):
    parser.description = 'Inspect a plugin instance'
    parser.add_argument("pluginName", metavar="NAME", help="Inspect plugin NAME")
    parser.add_argument("--instanceId", "-i", metavar="INDEX", help="Inspect plugin instance INDEX")

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

    plugin_settings_path = instance_config_path(config, plugin_name, plugin_instance)
    print 'Instance {} of plugin {} is installed at: {}'.format(plugin_instance, plugin_name, instance_dir(config, plugin_name, plugin_instance))
    print 'Instance {} of plugin {} settings:'.format(plugin_instance, plugin_name)
    with open(plugin_settings_path) as f:
        print f.read()
