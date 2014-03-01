import os
import sys
from ConfigParser import ConfigParser, NoOptionError


class Config(object):
    def __init__(self):
        root = os.path.dirname(os.path.realpath(__file__))
        config_file = os.path.join(root, '../configuration', 'pyscrape.cfg')
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
        self.download_banner = cfg.get('movie', 'banner').lower().strip() == 'true'
        self.download_backdrop = cfg.get('movie', 'backdrop').lower().strip() == 'true'
        self.download_poster = cfg.get('movie', 'poster').lower().strip() == 'true'
        self.download_landscape = cfg.get('movie', 'landscape').lower().strip() == 'true'
        self.download_thumbs = cfg.get('movie', 'thumbs').lower().strip() == 'true'
        self.download_extrathumbs = cfg.get('movie', 'extrathumbs').lower().strip() == 'true'
        self.download_logo = cfg.get('movie', 'logo').lower().strip() == 'true'
        self.download_disc = cfg.get('movie', 'disc').lower().strip() == 'true'
        self.download_clearart = cfg.get('movie', 'clearart').lower().strip() == 'true'
        self.download_extrafanart = cfg.get('movie', 'extrafanart').lower().strip() == 'true'


class ShowConfig(object):
    def __init__(self, cfg):
        self.paths = cfg.get('show', 'paths').split('::')
        self.download_banner = cfg.get('show', 'banner').lower().strip() == 'true'
        self.download_seasonbanner = cfg.get('show', 'seasonbanner').lower().strip() == 'true'
        self.download_seasonthumbs = cfg.get('show', 'seasonthumbs').lower().strip() == 'true'
        self.download_seasonposter = cfg.get('show', 'seasonposter').lower().strip() == 'true'
        self.download_logo = cfg.get('show', 'logo').lower().strip() == 'true'
        self.download_landscape = cfg.get('show', 'landscape').lower().strip() == 'true'
        self.download_thumbs = cfg.get('show', 'thumbs').lower().strip() == 'true'
        self.download_extrathumbs = cfg.get('show', 'extrathumbs').lower().strip() == 'true'
        self.download_clearart = cfg.get('show', 'clearart').lower().strip() == 'true'
        self.download_characterart = cfg.get('show', 'characterart').lower().strip() == 'true'
        self.download_poster = cfg.get('show', 'poster').lower().strip() == 'true'
        self.download_backdrop = cfg.get('show', 'backdrop').lower().strip() == 'true'
        self.download_extrafanart = cfg.get('show', 'extrafanart').lower().strip() == 'true'
        self.download_folder = cfg.get('show', 'folder').lower().strip() == 'true'


class TmdbConfig(object):
    def __init__(self, cfg):
        self.api_key = cfg.get('tmdb', 'api_key')
        self.url_base = cfg.get('tmdb', 'url_base')


class FanartConfig(object):
    def __init__(self, cfg):
        self.api_key = cfg.get('fanarttv', 'api_key')
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