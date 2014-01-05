import urllib2
import operator

try:
    import simplejson as json
except:
    import json
from Config import Config
from Logger import Logger


class TmdbApi():
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.url_base = self.config.tmdb.url_base
        self.api_key = self.config.tmdb.api_key

    def _request(self, request):
        if request.startswith('/'):
            request = request[1:]

        req = self.url_base + request
        if '&' in req or '?' in req:
            req = req + '&api_key=' + self.api_key
        else:
            req = req + '?api_key=' + self.api_key

        self.logger.log('Send TMDB Request: ' + req.replace(self.config.tmdb.api_key, 'XXX'), 'DEBUG')
        headers = {'Accept': 'application/json'}
        req = urllib2.Request(req, headers=headers)
        response_body = urllib2.urlopen(req).read()
        try:
            result = json.loads(response_body)
        except:
            result = json.loads(response_body.decode('utf-8'))
        return result

    def _loadImages(self, images, poster=False):
        result = {}
        for image in images:
            if poster:
                url = 'http://image.tmdb.org/t/p/w1920' + image['file_path']
            else:
                url = 'http://image.tmdb.org/t/p/w' + str(image['width']) + image['file_path']
            result[url] = image['vote_average']
        return result

    def _getResolution(self, images, width, height):
        result = []
        for image in images:
            if image == (): continue
            if image['width'] == width and image['height'] == height:
                result.append(image)
        return result

    def search_title(self, title, lang, year=None, imdbID=''):
        if imdbID is None or imdbID == '':
            title = title.replace(' ', '%20')
            req = 'search/movie?query=' + title
            req += '&language=' + lang
            if not year is None and not year == '':
                req = req + '&year=' + year
            result = self._request(req)
            return result['results']
        else:
            req = 'movie/' + imdbID
            req += '?language=' + lang
            result = self._request(req)
            return result

    def get_trailer(self, movie):
        if movie.id != '':
            trailers = self._request('movie/{0}/trailers'.format(movie.id))
            yt_trailers = trailers['youtube']

            hd_trailers = {}
            hq_trailers = {}
            standard_trailers = {}

            for trailer in yt_trailers:
                if trailer['size'] == 'HD':
                    hd_trailers[trailer['source']] = trailer['name']
                if trailer['size'] == 'HQ':
                    hq_trailers[trailer['source']] = trailer['name']
                if trailer['size'] == 'Standard':
                    standard_trailers[trailer['source']] = trailer['name']

            if len(hd_trailers) > 0:
                for trailer in hd_trailers:
                    if 'official' in hd_trailers[trailer].lower():
                        return trailer
                for trailer in hd_trailers:
                    return trailer

            if len(standard_trailers) > 0:
                for trailer in standard_trailers:
                    if 'official' in standard_trailers[trailer].lower():
                        return trailer
                for trailer in standard_trailers:
                    return trailer

            if len(hq_trailers) > 0:
                for trailer in hq_trailers:
                    if 'official' in hq_trailers[trailer].lower():
                        return trailer
                for trailer in hq_trailers:
                    return trailer

        return ''

    def get_movie(self, id, lang='de'):
        return self._request('movie/' + str(id) + '?language=' + lang)

    def get_certification(self, movie):
        r = 'movie/{0}/releases'.format(movie.id)
        result = self._request(r)
        rating = 'unknown'
        for r in result['countries']:
            if r['iso_3166_1'] == 'DE':
                rating = r['certification']
        return rating

    def get_images(self, id):
        return self._request('movie/{0}/images'.format(id))

    def get_backdrops(self, id):
        allImages = self.get_images(id)
        backdrops = self._getResolution(allImages['backdrops'], 1920, 1080)
        if len(backdrops) == 0:
            backdrops = self._getResolution(allImages['backdrops'], 1280, 720)
        if len(backdrops) == 0:
            backdrops = allImages['backdrops']
        return self._loadImages(backdrops)

    def get_posters(self, id):
        self.logger.log('Load Posters', 'DEBUG')
        posters = self._request('movie/{0}/images?language={1}'.format(id, self.config.pyscrape.language))['posters']
        if posters == []:  # get images of fallback language
            req = 'movie/{0}/images?language={1}'.format(id, self.config.pyscrape.fallback_language)
            posters = self._request(req)['posters']
        if posters == []:  # get all images if there aren't images for primary/fallback language
            posters = self.get_images(id)['posters']

        return sorted(self._loadImages(posters, True).iteritems(), key=operator.itemgetter(1), reverse=True)

    def get_credits(self, id):
        def get_crew(crew):
            xml = u''
            for c in crew:
                if c['department'] == 'Writing' and c['name'] != '':
                    xml += u'    <credits>{0}</credits>\n'.format(c['name'])
                if c['department'] == 'Directing' and c['name'] != '':
                    xml += u'    <director>{0}</director>\n'.format(c['name'])

            return xml

        def get_cast(cast):
            xml = u''
            for actor in cast:
                try:
                    image = 'http://image.tmdb.org/t/p/w500' + actor['profile_path']
                except:
                    continue # skip actore if there is no image
                xml += '    <actor>\n'
                if not actor is None and not actor['name'] is None:
                    xml += u'       <name>{0}</name>\n'.format(actor['name'].replace('"', "'"))
                if not actor is None and not actor['character'] is None:
                    xml += u'       <role>{0}</role>\n'.format(actor['character'].replace('"', "'"))
                xml += u'       <thumb>{0}</thumb>\n'.format(image)
                xml += '    </actor>\n'

            return xml

        self.logger.log('Load Credits', 'DEBUG')
        credits = self._request('movie/{0}/credits'.format(id))

        xml = get_crew(credits['crew'])
        xml += get_cast(credits['cast'])

        return xml

    def get_thumb(self, id):
        self.logger.log('Load Thumb', 'DEBUG')
        posters = self.get_posters(id)
        for poster in posters:
            return poster[0] # first poster is the poster with highest popularity

    def get_changes(self):
        return self._request('movies/changes?start_date=2000-01-01')