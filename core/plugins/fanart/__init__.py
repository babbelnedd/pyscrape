from core.plugins.PluginType import PluginType
from core.plugins.fanart.scanner import FanartScanner

__type__ = PluginType.MovieScanner


def load():
    return FanartScanner()