from core.plugins.plugintype import PluginType
from core.plugins.rottentomatoes.scanner import RottenTomatoesScanner

__type__ = PluginType.MovieScanner


def load():
    return RottenTomatoesScanner()