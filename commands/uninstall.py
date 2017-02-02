import argparse
import logging
import os
import shutil
import scalr_server_config as cfg

def process(args, loglevel):
    parser = argparse.ArgumentParser(
        description="Uninstall a Scalr plugin"
    )
    parser.add_argument("pluginName", metavar="NAME", help="Uninstall plugin NAME")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbosity")
    parser.add_argument("--instanceId", "-i", metavar="INDEX", help="Uninstall plugin instance INDEX")
    parser.add_argument("--all", "-a", action="store_true", help="Uninstall all plugin instances")
    newArgs = parser.parse_args(args=args)
    config = cfg.ScalrServerPluginsConfiguration()
    if not config.checkConfig():
        logging.error("Configuration is incorrect")
        return
    if newArgs.all and not newArgs.instanceId is None:
        logging.error("Invalid arguments, can't have --all and --instanceId at the same time")
        return
    plugin_name = newArgs.pluginName
    plugin_dir = os.path.join(config.plugins_base_dir, plugin_name)
    if not os.path.isdir(plugin_dir):
        logging.error("This plugin is not installed in the first place")
        return
    if newArgs.all:
        try:
            shutil.rmtree(plugin_dir)
        except Exception as e:
            logging.error("Error deleting directory %s: %s",plugin_dir ,e.message)
            return
        logging.info("All instances of plugin %s successfully uninstalled", plugin_name)
        return
    if not newArgs.instanceId:
        available_instances = [s for s in os.listdir(plugin_dir)]
        if len(available_instances) == 0:
            logging.info("No available instance for plugin $s. Deleting the enclosing folder.", plugin_name)
            shutil.rmtree(plugin_dir)
            return
        plugin_instance = available_instances[0]
        print 'Available instances for plugin: %s' % available_instances
        print 'Please choose one to delete [=%s]' % plugin_instance
        s = raw_input('-->')
        if not s == '':
            plugin_instance = s
        if plugin_instance not in available_instances:
            logging.error("Wrong instance chosen.")
            return
        plugin_instance_path = os.path.join(plugin_dir,plugin_instance)
        shutil.rmtree(plugin_instance_path)
        logging.info("Successfully uninstalled instance %s.", plugin_instance)
        if len(available_instances) == 1:
            logging.info("Enclosing folder for plugin %s is empty. Deleting it", plugin_name)
            shutil.rmtree(plugin_dir)




