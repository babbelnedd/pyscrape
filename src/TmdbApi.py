import urllib2
import operator
import json

from Config import Config
from Decorator import Cached
from Logger import log, LogLevel


config = Config()
url_base = config.tmdb.url_base
api_key = config.tmdb.api_key


def _load_images(images, poster=False):
    result = {}
    for image in images:
        if poster:
            url = 'http://image.tmdb.org/t/p/w1920' + image['file_path']
        else:
            url = 'http://image.tmdb.org/t/p/w' + str(image['width']) + image['file_path']
        result[url] = image['vote_average']
    return result


def _get_resolution(images, width, height):
    result = []
    for image in images:
        if image == ():
            continue
        if image['width'] == width and image['height'] == height:
            result.append(image)
    return result


@Cached
def _request(request_string):
    if request_string.startswith('/'):
        request_string = request_string[1:]

    req = url_base + request_string
    if '&' in req or '?' in req:
        req = req + '&api_key=' + api_key
    else:
        req = req + '?api_key=' + api_key

    log('Send TMDB Request: ' + req.replace(config.tmdb.api_key, 'XXX'), 'DEBUG')
    headers = {'Accept': 'application/json'}
    _req = urllib2.Request(req, headers=headers)
    response_body = urllib2.urlopen(_req).read()

    try:
        result = json.loads(response_body)
    except:
        result = json.loads(response_body.decode('utf-8'))

    return result


def search_title(title, lang, year=None, imdb_id=''):
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


def get_trailer(movie):
    if movie.id != '':
        trailers = _request('movie/{0}/trailers'.format(movie.id))
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


def get_movie(tmdb_id, lang='de'):
    return _request('movie/' + str(tmdb_id) + '?language=' + lang)


def get_certification(movie):
    r = 'movie/{0}/releases'.format(movie.id)
    result = _request(r)
    rating = 'unknown'
    for r in result['countries']:
        if r['iso_3166_1'].lower() == config.pyscrape.language:
            rating = r['certification']
    if not rating or rating == '':
        for r in result['countries']:
            if r['iso_3166_1'].lower() == config.pyscrape.fallback_language:
                rating = r['certification']
    return rating


def get_images(tmdb_id):
    return _request('movie/{0}/images'.format(tmdb_id))


def get_backdrops(tmdb_id):
    all_images = get_images(tmdb_id)
    backdrops = _get_resolution(all_images['backdrops'], 1920, 1080)
    if len(backdrops) == 0:
        backdrops = _get_resolution(all_images['backdrops'], 1280, 720)
    if len(backdrops) == 0:
        backdrops = all_images['backdrops']
    return _load_images(backdrops)


def get_posters(tmdb_id):
    log('Load Posters', 'DEBUG')
    posters = _request('movie/{0}/images?language={1}'.format(tmdb_id, config.pyscrape.language))['posters']
    if not posters:  # get images of fallback language
        req = 'movie/{0}/images?language={1}'.format(tmdb_id, config.pyscrape.fallback_language)
        posters = _request(req)['posters']
    if not posters:  # get all images if there aren't images for primary/fallback language
        posters = get_images(tmdb_id)['posters']

    return sorted(_load_images(posters, True).iteritems(), key=operator.itemgetter(1), reverse=True)


def get_credits(tmdb_id):
    def get_crew(crew):
        crew_xml = u''
        for c in crew:
            if c['department'] == 'Writing' and c['name'] != '':
                crew_xml += u'    <credits>{0}</credits>\n'.format(c['name'])
            if c['department'] == 'Directing' and c['name'] != '':
                crew_xml += u'    <director>{0}</director>\n'.format(c['name'])

        return crew_xml

    def get_cast(cast):
        cast_xml = u''
        for actor in cast:
            thumb = ''
            if 'profile_path' in actor and actor['profile_path'] is not None and actor['profile_path'] != '':
                thumb = 'http://image.tmdb.org/t/p/w500' + actor['profile_path']

            if actor is None or 'name' not in actor or actor['name'] is None or actor['name'] is '':
                continue

            cast_xml += '    <actor>\n'
            cast_xml += u'       <name>{0}</name>\n'.format(actor['name'].replace('"', "'"))
            if not actor is None and not actor['character'] is None:
                cast_xml += u'       <role>{0}</role>\n'.format(actor['character'].replace('"', "'"))
            if thumb != '':
                cast_xml += u'       <thumb>{0}</thumb>\n'.format(thumb)
            cast_xml += '    </actor>\n'

        return cast_xml

    log('Load Credits', 'DEBUG')
    movie_credits = _request('movie/{0}/credits'.format(tmdb_id))

    xml = get_crew(movie_credits['crew'])
    xml += get_cast(movie_credits['cast'])

    return xml


def get_thumb(tmdb_id):
    log('Load Thumb', 'DEBUG')
    posters = get_posters(tmdb_id)
    for poster in posters:
        return poster[0]  # first poster is the poster with highest popularity


def get_changes():
    return _request('movies/changes?start_date=2000-01-01')


def get_show_id(title=None, tvdb_id=None):
    if tvdb_id is not None:
        result = _request('find/' + tvdb_id + '?external_source=tvdb_id')

        if len(result['tv_results']) >= 1:
            return result['tv_results'][0]['id']

    if title is not None:
        title = title.replace(' ', '%20')
        for result in _request('search/tv?query=' + title)['results']:
            return result['id']


def get_show(tmdb_id):
    return _request('/tv/' + unicode(tmdb_id))


def get_episode_credits(tmdb_id, season_number, episode_number):
    try:
        return _request('/tv/{0}/season/{1}/episode/{2}/credits'.format(tmdb_id, season_number, episode_number))
    except urllib2.HTTPError:
        log('Ooops, it looks like there is no episode info', LogLevel.Warning)
        return ''


def get_season_poster(tmdb_id, season_number):
    return _request('/tv/{0}/season/{1}'.format(tmdb_id, season_number))['poster_path']


def get_season_count(tmdb_id):
    count = 0
    show = get_show(tmdb_id)
    if show:
        for season in show['seasons']:
            if season['season_number'] != 0:
                count += 1

    return count
