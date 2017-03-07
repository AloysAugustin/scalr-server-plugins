#!/usr/bin/env python

import os
import argparse, logging
import scalr_server_config as cfg
import scalr_server_repository as repo
import json
import types
import subprocess

def process(args, loglevel):

    parser = argparse.ArgumentParser(
        description="Install a Scalr plugin"
    )
    parser.add_argument("pluginName", metavar="NAME", help="Install plugin NAME")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbosity")
    newArgs = parser.parse_args(args=args)

    config = cfg.ScalrServerPluginsConfiguration()

    if not config.checkConfig():
        logging.error("Configuration is incorrect")
        return

    repository = repo.repositories()[config.repository_type]()

    plugin_base_dir = config.plugins_base_dir
    plugin_name = newArgs.pluginName
    if not plugin_name in repository.list_available_plugins():
        logging.error("Plugin not found in repository!")
        return
    #Is an instance of the plugin already installed?
    plugin_dir = os.path.join(plugin_base_dir,plugin_name)
    plugin_instances = []
    if plugin_name in os.listdir(plugin_base_dir):
        plugin_instances += [int(x) for x in os.listdir(plugin_dir)]
    else:
        os.mkdir(plugin_dir)
    logging.debug("Number of already existing instances: %d", len(plugin_instances))
    available_index = 0
    while (available_index in plugin_instances):
        available_index += 1
    logging.debug("Chosen index: %d", available_index)
    plugin_instance_dir = os.path.join(plugin_dir,str(available_index))
    os.mkdir(plugin_instance_dir)
    try:
        repository.install_plugin_in_dir(plugin_name,plugin_instance_dir)
    except Exception as e:
        logging.error("Cannot install plugin: %s",e.message)
        os.rmdir(plugin_instance_dir)
        return
    configure(plugin_name, available_index)
    venv_dir = install_venv(config, plugin_instance_dir)
    install_httpd_config(config, plugin_name, plugin_index, venv_dir, plugin_instance_dir)
    logging.info("Plugin %s installed with index %d.", plugin_name, available_index)
    logging.info("Reachable at location /plugins/%s/%d/", plugin_name, available_index)

def install_venv(config, plugin_instance_dir):
    logging.info('Installing virtual environment...')
    venv_dir = os.path.join(plugin_instance_dir, '.venv')
    requirements_path = os.path.join(plugin_instance_dir, 'requirements.txt')
    activate_path = os.path.join(venv_dir, 'bin', 'activate')
    subprocess.check_call(['/opt/scalr-server/embedded/bin/virtualenv', venv_dir])
    if os.path.isfile(requirements_path):
        subprocess.check_call('source {} && pip install -r {}'.format(activate_path, requirements_path), shell=True)
    logging.info('Virtual environment installed.')
    return venv_dir

def install_httpd_config(config, plugin_name, plugin_index, venv_dir, plugin_instance_dir):
    config_path = os.path.join(config.httpd_config_dir, plugin_name, '{}.conf'.format(plugin_index))
    daemon_process_name = '{}_{}'.format(plugin_name, plugin_index)
    wsgi_path = os.path.join(plugin_instance_dir, 'wsgi.py')

    logging.info('Installing Apache configuration file...')
    if not os.path.exists(os.path.dirname(config_path)):
        try:
            os.makedirs(os.path.dirname(config_path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
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
    logging.info('Apache config file created, restarting httpd...')
    subprocess.check_call(['/usr/bin/scalr-server-manage', 'restart', 'httpd'])
    logging.info('Apache restarted successfully')

def configure(plugin_name, plugin_index):
    config = cfg.ScalrServerPluginsConfiguration()
    plugin_spec_path = os.path.join(config.plugins_base_dir, plugin_name, str(plugin_index), 'plugin.json')
    plugin_spec = None
    print "Starting configuration for plugin %s, instance %d" % (plugin_name, plugin_index)
    with open(plugin_spec_path) as f:
        plugin_spec = json.loads(f.read())
    plugin_settings = dict()
    plugin_settings_path = os.path.join(config.plugins_base_dir, plugin_name, str(plugin_index), 'settings.json')
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