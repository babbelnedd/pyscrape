import json
import urllib2

from core.helpers.config import Config
from core.plugins import pluginbase
from core.helpers.decorator import Cached
from core.helpers.logger import log, LogLevel


#region Private Attributes

_config = Config()

#endregion

#region Private Methods


@Cached
def _request(request_string):
    if request_string.startswith('/'):
        request_string = request_string[1:]

    req = _config.tmdb.url_base + request_string
    if '&' in req or '?' in req:
        req = req + '&api_key=' + _config.tmdb.api_key
    else:
        req = req + '?api_key=' + _config.tmdb.api_key

    log('Send TMDB request: ' + req.replace(_config.tmdb.api_key, 'XXX'), LogLevel.Debug)
    headers = {'Accept': 'application/json'}
    _req = urllib2.Request(req, headers=headers)
    response_body = urllib2.urlopen(_req).read()
    result = json.loads(response_body)
    return result


#endregion


class TmdbScanner(pluginbase.Movie):
    def __init__(self):
        from core.plugins.plugintype import PluginType

        self.info = {'type': PluginType.MovieScanner,
                     'author': 'Lucas Schad',
                     'name': 'TheMovieDB Movie Scanner',
                     'version': '0.13'}

    @staticmethod
    def search(title, lang, year=None, imdb_id=None):
        if imdb_id is None or imdb_id == '':
            title = title.replace(' ', '%20')
            req = 'search/movie?query=' + title
            req += '&language=' + lang
            if not year is None and not year == '':
                req = req + '&year=' + year
            result = _request(req)
            return result['results']
        else:
            req = 'movie/' + imdb_id
            req += '?language=' + lang
            result = _request(req)
            return result

    def get_tmdb_id(self, title=None, year=None, imdb_id=None):
        result = self.search(title=title, lang=_config.pyscrape.language, year=year, imdb_id=imdb_id)

        if result is None or len(result) < 1:
            result = self.search(title=title, lang=_config.pyscrape.fallback_language, year=year, imdb_id=imdb_id)

        if not result:
            log('No Results', LogLevel.Warning)
            return

        tmdb_id = None
        if imdb_id is None or imdb_id == '':
            log(str(len(result)) + ' Result(s) found', LogLevel.Debug)

            if len(result) > 1:
                log('MORE THAN ONE RESULT FOUND - PLEASE CHECK THE RETRIEVED DATA!', LogLevel.Warning)

            popularity = 0
            for r in result:
                if tmdb_id is None:
                    tmdb_id = r['id']

                if (title == r[u'title'] or title == r[u'original_title']) and popularity < float(r['popularity']):
                    log('Found movie with higher popularity', LogLevel.Debug)
                    tmdb_id = r['id']
                else:
                    continue

                popularity = float(r['popularity'])
        else:
            tmdb_id = result['id']

        return tmdb_id

    def get_imdb_id(self, title=None, year=None, tmdb_id=None):
        if tmdb_id is None:
            tmdb_id = self.get_tmdb_id(title=title, year=year)

        if tmdb_id is not None:
            request = _request('movie/' + str(tmdb_id))
            if 'imdb_id' in request:
                return request['imdb_id']

    # todo: implement! problem: how to separate?
    def get_trailer(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

        if tmdb_id is not None:
            return _request('movie/{0}/trailers'.format(tmdb_id))

    def get_mpaa(self, country, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id is self.get_tmdb_id(imdb_id=imdb_id)

        r = 'movie/{0}/releases'.format(tmdb_id)
        result = _request(r)
        rating = 'unknown'
        for r in result['countries']:
            if r['iso_3166_1'].lower() == country.lower():
                rating = r['certification']

        return rating

    def get_credits(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

        movie_credits = _request('movie/{0}/credits'.format(tmdb_id))

        _credits = []
        _directors = []
        _actors = []

        for c in movie_credits['crew']:
            if c['department'] == 'Writing' and c['name'] != '':
                if c['name'] not in _credits:
                    _credits.append(c['name'])
            if c['department'] == 'Directing' and c['name'] != '':
                if c['name'] not in _directors:
                    _directors.append(c['name'])

        for actor in movie_credits['cast']:
            actor = {'name': actor['name'], 'role': actor['character'], 'thumb': actor['profile_path']}
            if actor not in _actors:
                _actors.append(actor)

        return dict(directors=_directors, credits=_credits, actors=_actors)

    def get_posters(self, language, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

        results = _request('movie/{0}/images?language={1}'.format(tmdb_id, language))['posters']

        posters = []
        for poster in results:
            if poster['file_path'] != '':
                posters.append({'url': 'http://image.tmdb.org/t/p/w1920' + poster['file_path'],
                                'rating': poster['vote_average'],
                                'vote_count': poster['vote_count'],
                                'language': poster['iso_639_1']})

        if posters:
            return sorted(posters, key=lambda k: k['rating'], reverse=True)
        else:
            return []

    def get_backdrops(self, imdb_id=None, tmdb_id=None):
        def _get_resolution(_images, width, height):
            result = []
            for _image in _images:
                if _image == ():
                    continue
                if _image['width'] == width and _image['height'] == height:
                    result.append(_image)
            return result

        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

        all_images = _request('movie/{0}/images'.format(str(tmdb_id)))
        backdrops = _get_resolution(all_images['backdrops'], 1920, 1080)
        if len(backdrops) == 0:
            backdrops = _get_resolution(all_images['backdrops'], 1280, 720)
        if len(backdrops) == 0:
            backdrops = all_images['backdrops']

        images = []
        for image in backdrops:
            url = 'http://image.tmdb.org/t/p/w' + str(image['width']) + image['file_path']
            images.append({'url': url, 'rating': image['vote_average'], 'vote_count': image['vote_count']})

        return sorted(images, key=lambda d: d['rating'])

    def get_release(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        return _request('movie/' + str(tmdb_id))['release_date']

    def get_original_title(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        return _request('movie/' + str(tmdb_id))['original_title']

    def get_title(self, country, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

        result = _request('movie/{0}/alternative_titles'.format(str(tmdb_id)))

        if 'titles' in result:
            for title in result['titles']:
                if title['iso_3166_1'].lower() == country.lower():
                    return title['title']

    def get_vote_count(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        return _request('movie/' + str(tmdb_id))['vote_count']

    def get_average_rating(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        return _request('movie/' + str(tmdb_id))['vote_average']

    def get_popularity(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        return _request('movie/' + str(tmdb_id))['popularity']

    def get_plot(self, language, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        return _request('movie/{0}?language={1}'.format(str(tmdb_id), language))['overview']

    def get_tagline(self, language, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        result = _request('movie/{0}?language={1}'.format(str(tmdb_id), language))
        if 'tagline' in result:
            return result['tagline']
        else:
            return ''

    def get_outline(self, language, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        result = _request('movie/{0}?language={1}'.format(str(tmdb_id), language))
        if 'outline' in result:
            return result['outline']
        else:
            return ''

    def get_revenue(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        return _request('movie/' + str(tmdb_id))['revenue']

    def get_budget(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        return _request('movie/' + str(tmdb_id))['budget']

    def get_collection(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        result = _request('movie/' + str(tmdb_id))['belongs_to_collection']

        if result is not None and 'name' in result:
            return result['name']

    def get_production_countries(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        countries = []
        for country in _request('movie/' + str(tmdb_id))['production_countries']:
            countries.append(country['name'])

        return countries

    def get_production_companies(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        companies = []
        for company in _request('movie/' + str(tmdb_id))['production_companies']:
            companies.append(company['name'])

        return companies

    def get_genres(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        result = _request('movie/' + str(tmdb_id))['genres']
        genres = []
        for genre in result:
            genres.append(genre['name'])

        return genres

    def get_spoken_languages(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)
        languages = []
        for language in _request('movie/' + str(tmdb_id))['spoken_languages']:
            languages.append(language['name'])

        return languages