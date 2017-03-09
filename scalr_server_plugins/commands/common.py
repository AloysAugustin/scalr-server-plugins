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

def installed_plugins(config):
    return [s for s in os.listdir(config.plugins_base_dir)]

def installed_instances(config, plugin_name):
    if exists(config, plugin_name):
        return [s for s in os.listdir(plugin_dir(config, plugin_name))]
    return []

def prompt_for_instance(config, plugin_name):
    available_instances = installed_instances(config, plugin_name)
    if len(available_instances) == 0:
        logging.info("No available instance for plugin %s. Deleting traces of this plugin.", plugin_name)
        remove_plugin(config, plugin_name)
        return None
    plugin_instance = available_instances[0]
    print 'Available instances for plugin: %s' % available_instances
    print 'Please choose one [=%s]' % plugin_instance
    s = raw_input('-->')
    if len(s) > 0 and s in available_instances:
        return s
    elif len(s) > 0:
        return None
    else:
        return plugin_instance

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

def instance_config_path(config, plugin_name, plugin_instance):
    return os.path.join(config.plugins_base_dir, plugin_name, plugin_instance, 'settings.json')

def httpd_config_dir(config, plugin_name):
    return os.path.join(config.httpd_config_dir, plugin_name)

def httpd_config_file(config, plugin_name, plugin_instance):
    return os.path.join(config.httpd_config_dir, plugin_name, '{}.conf'.format(plugin_instance))

def reload_config():
    logging.info('Restarting httpd...')
    try:
        subprocess.check_call(['/usr/bin/scalr-server-manage', 'restart', 'httpd'])
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            logging.warning('Could not restart httpd: /usr/bin/scalr-server-manage not found')
        else:
            raise

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
