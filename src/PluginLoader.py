import imp
import os

import src.utils


__root = src.utils.get_root()
_plugin_root = os.path.join(__root, 'plugins')
_main_module = '__init__'


def _get_plugins():
    """
    Get all custom-plugins from the plugin root
    """
    plugins = []
    for plugin_name in os.listdir(_plugin_root):
        location = os.path.join(_plugin_root, plugin_name)
        if not os.path.isdir(location) or not _main_module + '.py' in os.listdir(location):
            continue

        module = imp.find_module(_main_module, [location])
        plugin_info = imp.load_module(_main_module, *module)
        info = imp.find_module(plugin_info.__plugin__, [location])

        plugins.append({'name': plugin_name, 'plugin': info, 'info': plugin_info})
    return plugins


def _load_plugin(plugin):
    """
    Load and returns a plugin.

    @param  plugin      The plugin that shall be loaded.
                        Expects a result of imp.find_module()
    """
    return imp.load_module(_main_module, *plugin)


def get_plugins(plugin_type=None):
    """
    Load all custom-plugins.

    @param  plugin_type     Load only plugins from given type. Optional.
    """
    from Logger import LogLevel, log

    plugins = []

    for p in _get_plugins():
        log('Loading plugin \'' + p['info'].__name__ + '\' v' + p['info'].__version__, LogLevel.Debug)
        try:
            obj = _load_plugin(p['plugin'])
            ptype = p['info'].__type__
            plugin = {'obj': obj, 'type': ptype}

            if plugin_type is None or (plugin_type is not None and plugin_type == ptype):
                plugins.append(plugin)
        except Exception as exception:
            log('Failed to import plugin', LogLevel.Debug)
            log(exception.message, LogLevel.Debug)

    return plugins