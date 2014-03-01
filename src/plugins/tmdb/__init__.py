from src.plugins.PluginType import PluginType
from src.plugins.tmdb.scanner import TmdbScanner

__type__ = PluginType.MovieScanner


def load():
    return TmdbScanner()