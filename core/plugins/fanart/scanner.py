import json
import urllib2
import time

from core.helpers.config import config
from core.helpers.logger import log, LogLevel
from core.plugins import pluginbase
from core.plugins.plugintype import PluginType
from core.helpers.decorator import Cached


#region Private Methods


@Cached
def _request(request):
    log('Send Fanart request: ' + request.replace(config.fanart.api_key, 'XXX'), 'DEBUG')
    headers = {'Accept': 'application/json'}

    req = urllib2.Request(request, headers=headers)
    response_body = urllib2.urlopen(req).read()
    result = json.loads(response_body)
    return result


def _get(movie_id):
    req = '{0}movie/{1}/{2}/JSON'.format(config.fanart.url_base, config.fanart.api_key, movie_id)
    try_again = True
    n = 0
    while try_again and n < 10:
        try:
            return _request(req)
        except urllib2.HTTPError:
            n += 1
            try_again = True
            log('Ooops.. FanartTV Error - Try again', LogLevel.Warning)
            time.sleep(2)


def _get_items(image_type, tmdb_id=None, imdb_id=None, language=None):
    movie_id = None
    if tmdb_id is not None and tmdb_id != '':
        movie_id = tmdb_id
    elif imdb_id is not None and imdb_id != '':
        movie_id = imdb_id

    if movie_id is None:
        return None

    result = _get(movie_id=movie_id)
    if not result or len(result) < 1:
        return None

    items = []
    for r in [result[x] for x in result if image_type in result[x]]:
        if language:
            for item in [x for x in r[image_type]
                         if x['lang'].lower() == language.lower() or x['lang'] == '' or x['lang'] == '00']:
                items.append({'url': item['url'], 'rating': item['likes'], 'vote_count': item['likes']})
        else:
            for item in r[image_type]:
                items.append({'url': item['url'], 'rating': item['likes'], 'vote_count': item['likes']})

    if len(items) > 0:
        return items
    else:
        return None


#endregion


class FanartScanner(pluginbase.Movie):
    def __init__(self):
        self.info = {'type': PluginType.MovieScanner,
                     'author': 'Lucas Schad',
                     'name': 'Fanart.tv Movie Scanner',
                     'version': '0.10',
                     'priority': 2}

    def get_posters(self, language, imdb_id=None, tmdb_id=None):
        return _get_items(language=language, tmdb_id=tmdb_id, imdb_id=imdb_id, image_type='movieposter')

    def get_banners(self, language, imdb_id=None, tmdb_id=None):
        return _get_items(language=language, tmdb_id=tmdb_id, imdb_id=imdb_id, image_type='moviebanner')

    def get_disc_art(self, language, imdb_id=None, tmdb_id=None):
        return _get_items(language=language, tmdb_id=tmdb_id, imdb_id=imdb_id, image_type='moviedisc')

    def get_clearart(self, language, imdb_id=None, tmdb_id=None):
        result = _get_items(language=language, tmdb_id=tmdb_id, imdb_id=imdb_id, image_type='hdmovieclearart')
        if not result:
            result = _get_items(language=language, tmdb_id=tmdb_id, imdb_id=imdb_id, image_type='movieclearart')
        return result

    def get_logos(self, language, imdb_id=None, tmdb_id=None):
        result = _get_items(language=language, tmdb_id=tmdb_id, imdb_id=imdb_id, image_type='hdmovielogo')
        if not result:
            result = _get_items(language=language, tmdb_id=tmdb_id, imdb_id=imdb_id, image_type='movielogo')
        return result

    def get_backdrops(self, imdb_id=None, tmdb_id=None):
        return _get_items(tmdb_id=tmdb_id, imdb_id=imdb_id, image_type='moviebackground')

    def get_landscapes(self, imdb_id=None, tmdb_id=None):
        return _get_items(tmdb_id=tmdb_id, imdb_id=imdb_id, image_type='moviethumb')