from core.plugins.tmdb.scanner import TmdbScanner


def load():
    return TmdbScanner()