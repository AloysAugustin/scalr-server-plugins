#!/usr/bin/env python

import os
import logging
import utils
import scalr_server_repository as repo

@utils.singleton
class ScalrServerPluginsConfiguration:
    def __init__(self):
        self.plugins_base_dir = '/opt/scalr-server/var/lib/wsgi'
        self.httpd_config_dir = '/opt/scalr-server/etc/httpd/plugins'
        self.repository_type = 'internal'

    def checkConfig(self):
        if not os.path.isdir(self.plugins_base_dir):
            logging.error("Unexisting plugins_base_dir %s", self.plugins_base_dir)
            return False
        if not os.path.isdir(self.httpd_config_dir):
            logging.error("Unexisting httpd_config_dir %s", self.httpd_config_dir)
            return False
        if not self.repository_type in repo.repositories().keys():
            logging.error("Using an unregistered repository type")
            return False
        return True

    def setRepositoryType(self,repository_type):
        self.repository_type = repository_type

    def getRepository(self):
        return repo.repositories()[self.repository_type]()

    def setBasePath(self, path):
        self.plugins_base_dir = os.path.expanduser(path + self.plugins_base_dir)
        self.httpd_config_dir = os.path.expanduser(path + self.httpd_config_dir)
