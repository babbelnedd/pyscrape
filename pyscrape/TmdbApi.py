__author__ = 'LSC'
import urllib2
import operator

try:
    import simplejson as json
except:
    import json


class TmdbApi():
    def __init__(self, config, logger):
        self.config = config
        self.url_base = self.config.tmdb.url_base
        self.api_key = self.config.tmdb.api_key
        self.logger = logger

    def __request(self, request):
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

    def __loadImages(self, images, poster=False):
        result = {}
        for image in images:
            if poster:
                url = 'http://image.tmdb.org/t/p/w1920' + image['file_path']
            else:
                url = 'http://image.tmdb.org/t/p/w' + str(image['width']) + image['file_path']
            result[url] = image['vote_average']
        return result

    def __getResolution(self, images, width, height):
        result = []
        for image in images:
            if image == (): continue
            if image['width'] == width and image['height'] == height:
                result.append(image)
        return result

    def searchByTitle(self, title, lang, year=None):
        title = title.replace(' ', '%20')
        req = 'search/movie?query=' + title
        req = req + '&language=' + lang
        if not year is None and not year == 'unknown':
            req = req + '&year=' + year
        result = self.__request(req)
        return result

    def getTrailer(self, movie):
        if movie.id != '':
            trailers = self.__request('movie/{0}/trailers'.format(movie.id))
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

    def getMovie(self, id, lang='de'):
        return self.__request('movie/' + str(id) + '?language=' + lang)

    def getCertification(self, movie):
        # holt die Altersfreigabe
        r = 'movie/{0}/releases'.format(movie.id)
        result = self.__request(r)
        rating = 'unknown'
        for r in result['countries']:
            if r['iso_3166_1'] == 'DE':
                rating = r['certification']
        return rating

    def getImages(self, id):
        return self.__request('movie/{0}/images'.format(id))

    def getBackdrops(self, id):
        allImages = self.getImages(id)
        backdrops = self.__getResolution(allImages['backdrops'], 1920, 1080)
        if len(backdrops) == 0:
            backdrops = self.__getResolution(allImages['backdrops'], 1280, 720)
        if len(backdrops) == 0:
            backdrops = allImages['backdrops']
        return self.__loadImages(backdrops)

    def getPosters(self, id):
        self.logger.log('Load Posters', 'DEBUG')
        posters = self.__request('movie/{0}/images?language={1}'.format(id, self.config.pyscrape.language))['posters']
        if posters == []:
            posters = \
                self.__request('movie/{0}/images?language={1}'.format(id, self.config.pyscrape.fallback_language))[
                    'posters']
        if posters == []:
            posters = self.getImages(id)['posters']
        return sorted(self.__loadImages(posters, True).iteritems(), key=operator.itemgetter(1), reverse=True)

    def getCredits(self, id):
        self.logger.log('Load Credits', 'DEBUG')
        credits = self.__request('movie/{0}/credits'.format(id))
        cast = credits['cast']
        crew = credits['crew']

        xml = u''
        # write credits
        for c in crew:
            if c['department'] == 'Writing' and c['name'] != '':
                xml += u'    <credits>{0}</credits>\n'.format(c['name'])
            if c['department'] == 'Directing' and c['name'] != '':
                xml += u'    <director>{0}</director>\n'.format(c['name'])

        #write actors
        for actor in cast:
            try:
                image = 'http://image.tmdb.org/t/p/w500' + actor['profile_path']
            except:
                continue # falls es kein Bild gibt
            xml += '    <actor>\n'
            if not actor is None and not actor['name'] is None:
                xml += u'       <name>{0}</name>\n'.format(actor['name'].replace('"', "'"))
            if not actor is None and not actor['character'] is None:
                xml += u'       <role>{0}</role>\n'.format(actor['character'].replace('"', "'"))
            xml += u'       <thumb>{0}</thumb>\n'.format(image)
            xml += '    </actor>\n'

        return xml

    def getThumb(self, id):
        self.logger.log('Load Thumb', 'DEBUG')
        posters = self.getPosters(id)
        for poster in posters:
            return poster[0] # 1. poster ist das best bewerteste poster, deshalb hier rausspringen

    def getChanges(self):
        return self.__request('movies/changes?start_date=2000-01-01')

    def ____pycharm_bugfix(self):
        pass
