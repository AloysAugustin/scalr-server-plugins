#!/usr/bin/env python

import logging

from common import *
import scalr_server_config as cfg

def process(args, loglevel):
    config = cfg.ScalrServerPluginsConfiguration()
    if not config.checkConfig():
        logging.error("Configuration is incorrect")
        return

    print('Installed instances per plugin are:')
    for plugin in installed_plugins(config):
        print plugin, ': ', str(installed_instances(config, plugin))
