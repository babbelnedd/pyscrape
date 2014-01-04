class Config(object):
    def __init__(self, file):
        from ConfigParser import ConfigParser

        cfg = ConfigParser()
        cfg.read(file)
        self.pyscrape = pyscrapeConfig(cfg)
        self.tmdb = tmdbConfig(cfg)
        self.fanart = fanartConfig(cfg)
        self.codec = Codec(cfg)
        self.movie = MovieConfig(cfg)
        self.tv = TvConfig(cfg)


class pyscrapeConfig(object):
    def __init__(self, cfg):
        self.language = cfg.get('pyscrape', 'language')
        self.fallback_language = cfg.get('pyscrape', 'fallback_language')
        self.backdrop_limit = int(cfg.get('pyscrape', 'backdrop_limit'))
        self.poster_limit = int(cfg.get('pyscrape', 'poster_limit'))
        self.thumb_limit = int(cfg.get('pyscrape', 'thumb_limit'))
        self.debug_log = cfg.get('pyscrape', 'debug_log').lower().strip() == 'true'
        self.file_permissions = int(cfg.get('pyscrape', 'file_permissions'))
        self.folder_permissions = int(cfg.get('pyscrape', 'folder_permissions'))
        self.log_path = cfg.get('pyscrape', 'log_path')


class MovieConfig(object):
    def __init__(self, cfg):
        self.paths = cfg.get('movie', 'paths').split('::')


class tmdbConfig(object):
    def __init__(self, cfg):
        self.api_key = cfg.get('tmdb', 'api_key')
        self.image_base = cfg.get('tmdb', 'image_base')
        self.url_base = cfg.get('tmdb', 'url_base')


class fanartConfig(object):
    def __init__(self, cfg):
        self.api_key = cfg.get('fanarttv', 'api_key')
        self.image_base = cfg.get('fanarttv', 'image_base')
        self.url_base = cfg.get('fanarttv', 'url_base')


class TvConfig(object):
    def __init__(self, cfg):
        self.paths = cfg.get('tv', 'paths').split('::')


class Codec(object):
    def __init__(self, cfg):
        self.mediainfo_path = cfg.get('codec', 'mediainfo_path')
        self.mkvmerge = cfg.get('codec', 'mkvmerge')
        try:
            self.keep_subs = cfg.get('codec', 'keep_subtitles')
        except:
            self.keep_subs = 'all'
        self.keep_tracks = []
        try:
            self.keep_tracks = cfg.get('codec', 'keep_tracks').split('::')
        except:
            pass
