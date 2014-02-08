import os
import sys
from ConfigParser import ConfigParser, NoOptionError


class Config(object):
    def __init__(self):
        root = os.path.dirname(os.path.realpath(__file__))
        config_file = os.path.join(root, 'system', 'pyscrape.cfg')
        if not os.path.exists(config_file):
            from TerminalColor import print_colored, Foreground

            print_colored('Config file not found', Foreground.Red)
            sys.exit(-1)

        cfg = ConfigParser()
        cfg.read(config_file)
        self.pyscrape = PyscrapeConfig(cfg)
        self.tmdb = TmdbConfig(cfg)
        self.fanart = FanartConfig(cfg)
        self.codec = CodecConfig(cfg)
        self.movie = MovieConfig(cfg)
        self.show = ShowConfig(cfg)
        self.xbmc = XbmcConfig(cfg)


class PyscrapeConfig(object):
    def __init__(self, cfg):
        self.language = cfg.get('pyscrape', 'language')
        self.fallback_language = cfg.get('pyscrape', 'fallback_language')
        self.backdrop_limit = int(cfg.get('pyscrape', 'backdrop_limit'))
        self.poster_limit = int(cfg.get('pyscrape', 'poster_limit'))
        self.thumb_limit = int(cfg.get('pyscrape', 'thumb_limit'))
        self.debug_log = cfg.get('pyscrape', 'debug_log').lower().strip() == 'true'
        self.rename = cfg.get('pyscrape', 'rename').lower().strip() == 'true'


class MovieConfig(object):
    def __init__(self, cfg):
        self.paths = cfg.get('movie', 'paths').split('::')


class ShowConfig(object):
    def __init__(self, cfg):
        self.paths = cfg.get('show', 'paths').split('::')


class TmdbConfig(object):
    def __init__(self, cfg):
        self.api_key = cfg.get('tmdb', 'api_key')
        self.image_base = cfg.get('tmdb', 'image_base')
        self.url_base = cfg.get('tmdb', 'url_base')


class FanartConfig(object):
    def __init__(self, cfg):
        self.api_key = cfg.get('fanarttv', 'api_key')
        self.image_base = cfg.get('fanarttv', 'image_base')
        self.url_base = cfg.get('fanarttv', 'url_base')


class CodecConfig(object):
    def __init__(self, cfg):
        self.mediainfo_path = cfg.get('codec', 'mediainfo_path')
        self.mkvmerge = cfg.get('codec', 'mkvmerge')
        self.ffmpeg = cfg.get('codec', 'ffmpeg')
        self.screenshot_time = cfg.get('codec', 'screenshot_time')

        try:
            self.keep_subs = cfg.get('codec', 'keep_subtitles')
        except NoOptionError:
            self.keep_subs = 'all'
        self.keep_tracks = []
        try:
            self.keep_tracks = cfg.get('codec', 'keep_tracks').split('::')
        except NoOptionError:
            pass


class XbmcConfig(object):
    def __init__(self, cfg):
        self.protocol = cfg.get('xbmc', 'protocol')
        self.ip = cfg.get('xbmc', 'ip')
        self.port = cfg.get('xbmc', 'port')
        self.user = cfg.get('xbmc', 'user')
        self.password = cfg.get('xbmc', 'pass')