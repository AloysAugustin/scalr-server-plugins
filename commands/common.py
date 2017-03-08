#!/usr/bin/env python

import errno
import logging
import os
import shutil
import subprocess

def exists(config, plugin_name):
    return os.path.isdir(plugin_dir(config, plugin_name))

def plugin_dir(config, plugin_name):
    return os.path.join(config.plugins_base_dir, plugin_name)

def instance_dir(config, plugin_name, plugin_instance):
    return os.path.join(config.plugins_base_dir, plugin_name, plugin_instance)

def installed_instances(config, plugin_name):
    if exists(config, plugin_name):
        return [s for s in os.listdir(plugin_dir(config, plugin_name))]
    return []

def create_instance_dir(config, plugin_name, plugin_instance):
    create_dir(instance_dir(config, plugin_name, plugin_instance))

def remove_instance(config, plugin_name, plugin_instance):
    remove_dir(instance_dir(config, plugin_name, plugin_instance))
    remove_file(httpd_config_file(config, plugin_name, plugin_instance))

    if len(installed_instances(config, plugin_name)) == 0:
        remove_plugin(config, plugin_name)

def create_plugin_dir(config, plugin_name):
    create_dir(plugin_dir(config, plugin_name))

def remove_plugin(config, plugin_name):
    remove_dir(plugin_dir(config, plugin_name))
    remove_dir(httpd_config_dir(config, plugin_name))

def httpd_config_dir(config, plugin_name):
    return os.path.join(config.httpd_config_dir, plugin_name)

def httpd_config_file(config, plugin_name, plugin_instance):
    return os.path.join(config.httpd_config_dir, plugin_name, '{}.conf'.format(plugin_instance))

def reload_config():
    logging.info('Restarting httpd...')
    subprocess.check_call(['/usr/bin/scalr-server-manage', 'restart', 'httpd'])

def create_dir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # It's ok if dir already exist
        if exc.errno != errno.EEXIST:
            raise

def remove_dir(path):
    try:
        shutil.rmtree(path)
    except OSError as exc: # It's ok if dir doesn't exist
        if exc.errno != errno.ENOENT:
            raise

def remove_file(path):
    try:
        os.remove(path)
    except OSError as exc: # It's ok if file doesn't exist
        if exc.errno != errno.ENOENT:
            raise
