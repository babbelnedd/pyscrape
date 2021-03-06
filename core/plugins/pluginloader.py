import imp
import os
import traceback

import core.plugins
from core.helpers.logger import log, LogLevel, whiteline


#region Private Attributes

_plugin_root = core.plugins.__path__[0]
_main_module = '__init__'

#endregion

#region Private Methods


def _search_plugins():
    """
    Find all sub-modules from core.plugins

    Return schema:

    [{'name': '/path/to/sub-module/', 'info': result of imp.find_module()}]
    """
    plugins = []

    for location in [os.path.join(_plugin_root, path) for path in os.listdir(_plugin_root)
                     if os.path.isdir(os.path.join(_plugin_root, path))]:
        if not _main_module + '.py' in os.listdir(location):
            continue
        info = imp.find_module(_main_module, [location])
        plugins.append({'name': location, 'info': info})
    return plugins


def _load_plugin(plugin):
    """
    Load and returns the given plugin

    @param  plugin  Expects an plugin from _search_plugins.
    """
    return imp.load_module(_main_module, *plugin['info'])


#endregion


def get_plugins(plugin_type=None):
    """
    Get all plugins of a given type.

    @param  plugin_type     The type of plugins that shall be loaded. Optional.
                            When plugin_type is not passed, all plugins will be returned.
    """
    plugins = []
    for plugin in _search_plugins():
        try:
            log('Try to load plugin ' + os.path.basename(plugin['name']), LogLevel.Debug)
            plugin = _load_plugin(plugin).load()
            if plugin is not None and (plugin_type is None or plugin.info['type'] == plugin_type):
                plugins.append(plugin)
            log('Plugin successfully loaded', LogLevel.Debug)
        except:
            import sys

            log('Failed to load plugin', LogLevel.Error)
            for n in range(0, len(sys.exc_info())):
                log(str(sys.exc_info()[n]), LogLevel.Error)
            log(traceback.format_exc(), LogLevel.Error)
            whiteline()

    return sorted(plugins, key=lambda k: k.info['priority'])