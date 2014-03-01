import json
import urllib2

from core.Config import Config
import core.Decorator as Decorator
from core.Logger import log, LogLevel


config = Config()


#region Private Methods


@Decorator.Cached
def _request(request_string):
    if request_string.startswith('/'):
        request_string = request_string[1:]

    req = config.tmdb.url_base + request_string
    if '&' in req or '?' in req:
        req = req + '&api_key=' + config.tmdb.api_key
    else:
        req = req + '?api_key=' + config.tmdb.api_key

    log('Send TMDB Request: ' + req.replace(config.tmdb.api_key, 'XXX'), LogLevel.Debug)
    headers = {'Accept': 'application/json'}
    _req = urllib2.Request(req, headers=headers)
    response_body = urllib2.urlopen(_req).read()

    result = json.loads(response_body)

    return result


#endregion


class TmdbScanner(object):
    def __init__(self):
        from core.plugins.PluginType import PluginType

        self.info = {'type': PluginType.MovieScanner,
                     'author': 'Lucas Schad',
                     'name': 'TheMovieDB Movie Scanner',
                     'version': '0.13'}

    @staticmethod
    def search(title, lang, year=None, imdb_id=None):
        if imdb_id is None:
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
        """
        Tries to find the correct TMDB ID.

        @param  title       Title of the searched movie. Optional.
        @param  year        Release year of the searched movie. Optional.
        @param  imdb_id     IMDB ID of the searched movie. Optional.
        """
        result = self.search(title=title, lang=config.pyscrape.language, year=year, imdb_id=imdb_id)

        if result is None or len(result) < 1:
            result = self.search(title=title, lang=config.pyscrape.fallback_language, year=year, imdb_id=imdb_id)

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
        """
        Tries to find the correct IMDB ID.

        @param      title       The title of the searched movie. Optional.
        @param      year        The release year of the searched movie. Optional.
        @param      tmdb_id     The TMDB ID of the searched movie. Optional.
        """
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
        """
        Gets the MPAA for a specific country. Country code is ISO639-2 standard.
        Both ID parameter are optional - but you need to pass one.

        @param      country     ISO639-2 country code
        @param      imdb_id     IMDB ID of a movie. Optional.
        @param      tmdb_id     TMDB ID of a movie. Optional.

        Example:
        get_mpaa('US', imdb_id='tt1234567')
        """
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
        """
        Return the credits of a movie.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return schema:
            {
             'credits': [u'Bob Kane', u'Jonathan Nolan', ...],
             'directors': [u'Christopher Nolan', ...],
             'actors':[{'role': u'Bruce Wayne', 'name': u'Christian Bale', 'thumb': u'/vecCvACI2QhSE5fOoANeWDjxGKM.jpg'}, {...}]
             }
        """
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

        movie_credits = _request('movie/{0}/credits'.format(tmdb_id))

        credits = []
        directors = []
        actors = []

        for c in movie_credits['crew']:
            if c['department'] == 'Writing' and c['name'] != '':
                if c['name'] not in credits:
                    credits.append(c['name'])
            if c['department'] == 'Directing' and c['name'] != '':
                if c['name'] not in directors:
                    directors.append(c['name'])

        for actor in movie_credits['cast']:
            actor = {'name': actor['name'], 'role': actor['character'], 'thumb': actor['profile_path']}
            if actor not in actors:
                actors.append(actor)

        return dict(directors=directors, credits=credits, actors=actors)

    def get_posters(self, lang=None, imdb_id=None, tmdb_id=None):
        """
        Load all posters for a movie.

        @param  lang        The preferred Language of movie posters. Optional.
        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return schema:
            [{'url': u'http://image.tmdb.org/t/p/w1920/tdzD09XZzfSSgNTsYtmcgS4uSNE.jpg',
            'rating': 5.30505952380952),
            'vote_count': 11,
            'language': 'en'},
            {...},]

            Ordered descending by popularity. Highest first.
        """
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

        if lang:
            results = _request('movie/{0}/images?language={1}'.format(tmdb_id, lang))['posters']
        else:
            results = _request('movie/{0}/images'.format(tmdb_id))['posters']

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

    def get_banners(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_disc_art(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_clearart(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_logos(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_backdrops(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_landscapes(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_release(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_original_title(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_vote_count(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_average_rating(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_popularity(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_plot(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_tagline(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_outline(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_revenue(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_collection(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_budget(self, imdb_id=None, tmdb_id=None):
        print "TMDB"
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_production_countries(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_genres(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_production_companies(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)

    def get_spoken_languages(self, imdb_id=None, tmdb_id=None):
        if tmdb_id is None and imdb_id is not None:
            tmdb_id = self.get_tmdb_id(imdb_id=imdb_id)