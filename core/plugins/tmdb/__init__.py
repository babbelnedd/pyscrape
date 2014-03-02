from core.plugins.plugintype import PluginType
from core.plugins.tmdb.scanner import TmdbScanner

__type__ = PluginType.MovieScanner


def load():
    return TmdbScanner()