import imp
import os

import src.plugins


plugin_root = src.plugins.__path__[0]
main_module = '__init__'


def _search_plugins():
    plugins = []

    for location in [os.path.join(plugin_root, path) for path in os.listdir(plugin_root)
                     if os.path.isdir(os.path.join(plugin_root, path))]:
        if not main_module + '.py' in os.listdir(location):
            continue
        info = imp.find_module(main_module, [location])
        plugins.append({'name': location, 'info': info})
    return plugins


def _load_plugin(plugin):
    return imp.load_module(main_module, *plugin['info'])


def get_plugins(plugin_type=None):
    plugins = []
    for plugin in _search_plugins():
        plugin = _load_plugin(plugin).load()
        if plugin_type is None or plugin.info['type'] == plugin_type:
            plugins.append(plugin)

    return plugins