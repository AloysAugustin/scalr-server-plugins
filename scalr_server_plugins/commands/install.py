#!/usr/bin/env python

import os
import logging
import json
import types
import subprocess

from common import *

def setup_parser(parser):
    parser.description = 'Install a Scalr plugin'
    parser.add_argument("pluginName", metavar="NAME", help="Install plugin NAME")

def process(args, config):
    repository = config.getRepository()

    plugin_name = args.pluginName
    if not plugin_name in repository.list_available_plugins():
        logging.error("Plugin not found in repository!")
        return 1

    if not exists(config, plugin_name):
        create_plugin_dir(config, plugin_name)

    plugin_instances = installed_instances(config, plugin_name)
    logging.debug("Number of already existing instances: %d", len(plugin_instances))
    available_index = 0
    while str(available_index) in plugin_instances:
        available_index += 1
    plugin_instance = str(available_index)
    logging.debug("Chosen index: %s", plugin_instance)
    create_instance_dir(config, plugin_name, plugin_instance)
    plugin_instance_dir = instance_dir(config, plugin_name, plugin_instance)
    try:
        repository.install_plugin_in_dir(plugin_name,plugin_instance_dir)
        configure(config, plugin_name, plugin_instance)
        venv_dir = install_venv(config, plugin_instance_dir)
        install_httpd_config(config, plugin_name, plugin_instance, venv_dir, plugin_instance_dir)
    except Exception as e:
        logging.exception("Cannot install plugin: %s",e.message)
        remove_instance(config, plugin_name, plugin_instance)
        return 1
    logging.info("Plugin %s installed with index %s.", plugin_name, plugin_instance)
    logging.info("Reachable at location /plugins/%s/%s/", plugin_name, plugin_instance)
    return 0

def install_venv(config, plugin_instance_dir):
    logging.info('Installing virtual environment...')
    venv_dir = os.path.join(plugin_instance_dir, '.venv')
    requirements_path = os.path.join(plugin_instance_dir, 'requirements.txt')
    activate_path = os.path.join(venv_dir, 'bin', 'activate')
    # Create virtualenv
    subprocess.check_call(['virtualenv', venv_dir])
    if os.path.isfile(requirements_path):
        subprocess.check_call('. {} && pip install -r {}'.format(activate_path, requirements_path), shell=True)
    logging.info('Virtual environment installed.')
    return venv_dir

def install_httpd_config(config, plugin_name, plugin_index, venv_dir, plugin_instance_dir):
    config_path = httpd_config_file(config, plugin_name, plugin_index)
    daemon_process_name = '{}_{}'.format(plugin_name, plugin_index)
    wsgi_path = os.path.join(plugin_instance_dir, 'wsgi.py')
    if not os.path.isfile(wsgi_path):
        raise Exception('WSGI module {} not found, plugin will not be functional'.format(wsgi_path))

    logging.info('Installing Apache configuration file...')
    create_dir(os.path.dirname(config_path))

    with open(config_path, 'w') as config_file:
        contents = """
WSGIDaemonProcess {daemon_process_name} python-home={venv_dir} python-path={plugin_instance_dir}
WSGIScriptAlias /{plugin_name}/{plugin_index} {wsgi_path}
<Location /{plugin_name}/{plugin_index}>
WSGIProcessGroup {daemon_process_name}
</Location>
""".format(daemon_process_name=daemon_process_name,
           plugin_name=plugin_name,
           plugin_index=plugin_index,
           venv_dir=venv_dir,
           plugin_instance_dir=plugin_instance_dir,
           wsgi_path=wsgi_path)
        config_file.write(contents)
    reload_config()
    logging.info('Apache configured successfully')

def configure(config, plugin_name, plugin_index):
    plugin_spec_path = os.path.join(instance_dir(config, plugin_name, plugin_index), 'plugin.json')
    plugin_spec = None
    print "Starting configuration for plugin %s, instance %s" % (plugin_name, plugin_index)
    with open(plugin_spec_path) as f:
        plugin_spec = json.loads(f.read())
    plugin_settings = dict()
    plugin_settings_path = instance_config_path(config, plugin_name, plugin_index)
    # Load default settings
    if (not 'parameters' in plugin_spec.keys()) or not (type(plugin_spec['parameters']) is types.ListType):
        logging.debug("No parameters key found in plugin.json")
        plugin_spec['parameters'] = []
    plugin_settings_info = dict()
    for p in plugin_spec['parameters']:
        plugin_settings[ p['key'] ] = p['default']
        plugin_settings_info[ p['key'] ] = p
    # Is there a settings.json file already?
    if os.path.isfile(plugin_settings_path):
        # Then load these parameters as default
        with open(plugin_settings_path) as f:
            plugin_settings = json.loads(f.read())

    # Now prompts the user to reconfigure everything
    print "Description of the plugin: %s" % plugin_spec['description']
    for k in plugin_settings.keys():
        print "Please enter %s. [=%s]" % (plugin_settings_info[k]['description'], plugin_settings[k])
        value = raw_input('-->')
        if not value == '':
            plugin_settings[k] = value

    # Now outputs the json file
    with open(plugin_settings_path, mode='w') as f:
        f.write( json.dumps(plugin_settings, indent=2) )

    logging.info("Plugin configured")
