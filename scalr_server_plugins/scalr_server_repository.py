#!/usr/bin/env python

import utils
import os
import zipfile
import tarfile
import urllib2
import StringIO
from contextlib import closing
from yaml import safe_load
import logging

@utils.singleton
def repositories():
    return dict()

def registerRepository(name):
    def _registerRepository(cls):
        repositories()[name] = cls
        return cls
    return _registerRepository

@registerRepository('internal')
@utils.singleton
class ScalrServerPluginsInternalRepository:
    def __init__(self):
        repo_url = 'https://raw.githubusercontent.com/scalr-tutorials/scalr-plugin-repository/master/plugins.yml'
        logging.info('Loading plugins list...')
        with closing(urllib2.urlopen(repo_url)) as repodata:
            self.repo_data = safe_load(repodata.read())
            self.plugins = self.repo_data['plugins']
            logging.info('Plugin list loaded successfully.')

    def list_available_plugins(self):
        return [p['name'] for p in self.plugins]

    def install_plugin_in_dir(self, plugin_name, target_dir):
        plugin = None
        for p in self.plugins:
            if p['name'] == plugin_name:
                plugin = p
                break
        if plugin is None:
            raise Exception("Plugin Not Found")

        with closing(urllib2.urlopen(plugin['url'])) as f:
            if plugin['archive-type'] == 'zip':
                data = StringIO.StringIO()
                data.write(f.read())
                z = zipfile.ZipFile(data)
                z.extractall(target_dir)
            else:
                raise Exception('Unsupported Archive type')
