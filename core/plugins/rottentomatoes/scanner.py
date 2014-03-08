import json
import urllib2

from core.plugins import pluginbase
from core.helpers.logger import log, LogLevel
from core.helpers.decorator import Cached


#region Private Methods

@Cached
def _request(request_string):
    api_key = 'czhmm6bhb77vcgdz2h5c4363'
    url_base = 'http://api.rottentomatoes.com/api/public/v1.0/'
    if '?' in request_string:
        req = url_base + request_string + '&apikey=' + api_key
    else:
        req = url_base + request_string + '?apikey=' + api_key

    log('Send RottenTomatoes request: ' + req.replace(api_key, 'XXX'), LogLevel.Debug)
    headers = {'Accept': 'application/json'}
    _req = urllib2.Request(req, headers=headers)
    response_body = urllib2.urlopen(_req).read()
    result = json.loads(response_body)
    return result


def _get_id(imdb_id):
    if imdb_id.startswith('tt'):
        imdb_id = imdb_id[2:]
    result = _request('movie_alias.json?id=' + imdb_id + '&type=imdb')
    if 'id' in result:
        return str(result['id'])


#endregion


class RottenTomatoesScanner(pluginbase.Movie):
    def __init__(self):
        from core.plugins.plugintype import PluginType

        self.info = {'type': PluginType.MovieScanner,
                     'author': 'Lucas Schad',
                     'name': 'RottenTomatoes Movie Scanner',
                     'version': '0.10',
                     'priority': 3}

    def get_credits(self, imdb_id=None, tmdb_id=None):
        if imdb_id is None:
            return None

        rt_id = _get_id(imdb_id)
        result = _request('movies/' + rt_id + '/cast.json')['cast']
        c = {'directors': [], 'credits': []}
        actors = []
        for actor in result:
            for character in actor['characters']:
                actors.append({'role': character, 'name': actor['name'], 'thumb': ''})
        c['actors'] = actors
        return c

    def get_posters(self, language, imdb_id=None, tmdb_id=None):
        if imdb_id is None:
            return None

        rt_id = _get_id(imdb_id)
        result = _request('movies/' + rt_id + '.json')
        if result is not None and 'posters' in result:
            if 'original' in result['posters'] and result['posters']['original'] != '':
                return [{'url': result['posters']['original'], 'rating': '', 'vote_count': ''}]

    def get_release(self, imdb_id=None, tmdb_id=None):
        if imdb_id is None:
            return None

        rt_id = _get_id(imdb_id)
        result = _request('movies/' + rt_id + '.json')
        if 'release_dates' in result and 'theater' in result['release_dates']:
            return result['release_dates']['theater']

    def get_original_title(self, imdb_id=None, tmdb_id=None):
        if imdb_id is None:
            return None

        rt_id = _get_id(imdb_id)
        result = _request('movies/' + rt_id + '.json')
        if 'title' in result:
            return result['title']

    def get_average_rating(self, imdb_id=None, tmdb_id=None):
        if imdb_id is None:
            return None

        rt_id = _get_id(imdb_id)
        result = _request('movies/' + rt_id + '.json')
        if 'ratings' in result and 'audience_score' in result['ratings']:
            return result['ratings']['audience_score']

    def get_plot(self, language, imdb_id=None, tmdb_id=None):
        if imdb_id is None or language.lower() != 'en':
            return None

        rt_id = _get_id(imdb_id)
        result = _request('movies/' + rt_id + '.json')
        if 'synopsis' in result and result['synopsis'] != 'n/a' and result['synopsis'].strip() != '':
            return result['synopsis']

    def get_genres(self, imdb_id=None, tmdb_id=None):
        if imdb_id is None:
            return None

        rt_id = _get_id(imdb_id)
        request_result = _request('movies/' + rt_id + '.json')
        result = []
        if 'genres' in request_result:
            for genre in request_result['genres']:
                for g in genre.split('&'):
                    result.append(g.strip())
            if len(result) > 0:
                return result