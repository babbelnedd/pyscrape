import urllib2
import json
import time

from core.helpers.decorator import Cached
from core.helpers.config import Config
from core.helpers.logger import log, LogLevel


config = Config()
cached = {}


@Cached
def __request(request):
    log('Send Fanart Request: ' + request.replace(config.fanart.api_key, 'XXX'), 'DEBUG')
    headers = {'Accept': 'application/json'}

    _request = urllib2.Request(request, headers=headers)
    response_body = urllib2.urlopen(_request).read()
    try:
        result = json.loads(response_body)
    except:
        result = json.loads(response_body.decode('utf-8'))

    return result


def _get(type, id, format='JSON'):
    req = '{0}{1}/{2}/{3}/{4}'.format(config.fanart.url_base, type, config.fanart.api_key, id, format)
    try_again = True
    n = 0
    while try_again and n < 10:
        try:
            return __request(req)
        except urllib2.HTTPError:
            n += 1
            try_again = True
            log('Ooops.. FanartTV Error - Try again', LogLevel.Warning)
            time.sleep(2)


def get_movie(tmdb_id):
    return _get(type='movie', id=tmdb_id)


def get_show(tvdb_id):
    return _get(type='series', id=tvdb_id)