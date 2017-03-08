#!/usr/bin/env python

import logging
import scalr_server_config as cfg
import scalr_server_repository as repo

def process(args, loglevel):
    config = cfg.ScalrServerPluginsConfiguration()
    if not config.checkConfig():
        logging.error("Configuration is incorrect")
        return
    repository = repo.repositories()[config.repository_type]()
    print "Available plugins are:"
    l = repository.list_available_plugins()
    for p in l:
        print p



