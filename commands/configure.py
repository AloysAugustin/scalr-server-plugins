import scalr_server_config as cfg
import install
import logging
import argparse
import os

def process(args, loglevel):
    parser = argparse.ArgumentParser(
        description="Reconfigure a Scalr plugin"
    )
    parser.add_argument("pluginName", metavar="NAME", help="Uninstall plugin NAME")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbosity")
    parser.add_argument("--instanceId", "-i", metavar="INDEX", help="Uninstall plugin instance INDEX")
    newArgs = parser.parse_args(args=args)
    config = cfg.ScalrServerPluginsConfiguration()
    if not config.checkConfig():
        logging.error("Configuration is incorrect")
        return

    plugin_name = newArgs.pluginName
    plugin_dir = os.path.join(config.plugins_base_dir, plugin_name)
    if not os.path.isdir(plugin_dir):
        logging.error("This plugin is not installed in the first place")
        return
    available_instances = [s for s in os.listdir(plugin_dir)]
    if not newArgs.instanceId:
        if len(available_instances) == 0:
            logging.info("No available instance for plugin $s. Nothing to do", plugin_name)
            return
        plugin_instance = available_instances[0]
        print 'Available instances for plugin: %s' % available_instances
        print 'Please choose one to reconfigure [=%s]' % plugin_instance
        s = raw_input('-->')
        if not s == '':
            plugin_instance = s
        if plugin_instance not in available_instances:
            logging.error("Wrong instance chosen.")
            return
    else:
        plugin_instance = newArgs.instanceId
    install.configure(plugin_name, int(plugin_instance) )