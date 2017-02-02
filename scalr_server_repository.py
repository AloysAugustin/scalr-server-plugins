import utils
import os
import zipfile
import tarfile
import urllib2
import StringIO
from contextlib import closing
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
        self.plugins = [
            {
                'name':'testplugin',
                'url' : 'file://' + os.path.join(os.path.dirname(__file__), 'samples', 'testplugin.zip'),
                'archive-type' : 'zip'
            },

        ]

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


