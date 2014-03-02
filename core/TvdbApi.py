from xml.dom.minidom import parseString
from zipfile import ZipFile
import urllib
import os
import time
import operator
from lxml import etree

from core.helpers.Decorator import Cached
from core.helpers.Logger import log, LogLevel
from core.helpers import utils
from core.helpers.Config import Config
from core.helpers.utils import download
from TmdbApi import get_show_id, get_show, get_episode_credits, get_season_count, get_season_poster
from core.helpers.Exception import ShowNotFoundException
import FanartTvApi
from core.media import Codec


class TvdbApi(object):
    def __init__(self, show):
        log('Initialise TvdbApi', LogLevel.Debug)
        self.show = {'id': get_id(show['title']), 'path': show['path']}

        if self.show['id'] is None:
            raise ShowNotFoundException()

        primary_language_file = _download_zip(self.show['id'], config.pyscrape.language)
        fallback_language_file = _download_zip(self.show['id'], config.pyscrape.fallback_language)

        self.files = [primary_language_file['dst'], fallback_language_file['dst']]
        self._get_show_info(self.files)
        self.show['zip_url'] = primary_language_file['core']

    def _get_actors(self):
        primary = _read_from_zip(src=self.files[0], language=config.pyscrape.language)
        second = _read_from_zip(src=self.files[1], language=config.pyscrape.fallback_language)
        log('Get TvShow actors', LogLevel.Debug)
        image_base = 'http://thetvdb.com/banners/'
        actors = []
        for node in parseString(primary['actors']).getElementsByTagName('Actor'):
            def get_node_value(key):
                x = node.getElementsByTagName(key)[0]
                if x is not None and x.firstChild is not None:
                    return unicode(x.firstChild.nodeValue).encode('utf8')
                else:
                    return ''

            name = get_node_value('Name')
            thumb = get_node_value('Image')
            role = get_node_value('Role')

            if thumb != '':
                thumb = image_base + thumb

            if '|' in role:
                roles = role.split('|')
                for role in roles:
                    actors.append({'name': name, 'role': role.strip(), 'thumb': thumb})
            else:
                actors.append({'name': name, 'role': role, 'thumb': thumb})
        return actors

    def _get_show_info(self, files):
        def get_value_from_tmdb(key):
            tmdb_id = get_show_id(title=get_show_value('SeriesName'))
            if tmdb_id is None:
                return ''

            result = get_show(tmdb_id)
            if key == 'Network':
                for network in result['networks']:
                    return network['name']

            if key == 'ContentRating':
                pass

            return ''

        def get_show_value(tag):
            def get_value(xml, key):
                dom = parseString(xml)
                for node in dom.getElementsByTagName('Series'):
                    try:
                        result = unicode(node.getElementsByTagName(key)[0].firstChild.nodeValue).encode('utf8')
                    except AttributeError:
                        result = get_value_from_tmdb(key)
                    except IndexError:
                        result = get_value_from_tmdb(key)

                    return result

            result = get_value(primary['lang'], tag)
            if result == '':
                result = get_value(second['lang'], tag)

            return result

        def get_episode_count():
            log('Get TvShow episode count', LogLevel.Debug)
            count = 0
            dom = parseString(primary['lang'])
            for _ in dom.getElementsByTagName('Episode'):
                count += 1

            return count

        primary = _read_from_zip(src=files[0], language=config.pyscrape.language)
        second = _read_from_zip(src=files[1], language=config.pyscrape.fallback_language)
        image_base = 'http://thetvdb.com/banners/'
        self.show['tmdb_id'] = get_show_id(title=get_show_value('SeriesName'))
        self.show['mpaa'] = get_show_value('ContentRating')
        self.show['premiered'] = get_show_value('FirstAired')
        self.show['genres'] = [g for g in get_show_value('Genre').split('|') if g != ""]
        self.show['imdbID'] = get_show_value('IMDB_ID')
        self.show['network'] = get_show_value('Network')
        self.show['networkID'] = get_show_value('NetworkID')
        self.show['plot'] = get_show_value('Overview')
        self.show['rating'] = get_show_value('Rating')
        self.show['votes'] = get_show_value('RatingCount')
        self.show['average_runtime'] = get_show_value('RatingCount')
        self.show['title'] = get_show_value('SeriesName')
        self.show['status'] = get_show_value('Status')
        self.show['banner'] = image_base + get_show_value('banner')
        self.show['fanart'] = image_base + get_show_value('fanart')
        self.show['poster'] = image_base + get_show_value('poster')
        self.show['episode_count'] = get_episode_count()
        self.show['actors'] = self._get_actors()

    def get_episode_nfo(self, path, episodes):
        def get_episode(_episode):
            def get_episode_node(xml):
                dom = parseString(xml)
                for node in dom.getElementsByTagName('Episode'):
                    season_found = False
                    episode_found = False

                    for n in node.getElementsByTagName('SeasonNumber'):
                        if n.firstChild.nodeValue == _episode['season']:
                            season_found = True

                    for n in node.getElementsByTagName('EpisodeNumber'):
                        if n.firstChild.nodeValue == _episode['episode']:
                            episode_found = True

                    if season_found and episode_found:
                        log('Episode Node found', LogLevel.Debug)
                        return node

            def get_value(key):
                result = ''

                try:
                    result = nodes['primary'].getElementsByTagName(key)[0].firstChild.nodeValue
                except IndexError:
                    pass
                except AttributeError:
                    pass

                if result is '':
                    try:
                        result = nodes['secondary'].getElementsByTagName(key)[0].firstChild.nodeValue
                    except IndexError:
                        pass
                    except AttributeError:
                        pass

                return unicode(result).encode('utf8')

            while _episode['episode'].startswith('0'):
                _episode['episode'] = _episode['episode'][1:]
            while _episode['season'].startswith('0'):
                _episode['season'] = _episode['season'][1:]

            primary = _read_from_zip(src=self.files[0], language=config.pyscrape.language)
            secondary = _read_from_zip(src=self.files[1], language=config.pyscrape.fallback_language)
            nodes = {'primary': get_episode_node(primary['lang']), 'secondary': get_episode_node(secondary['lang'])}
            image_base = 'http://thetvdb.com/banners/'
            thumb = get_value('filename')
            if thumb is not '':
                thumb = image_base + thumb

            from Movie import Movie

            item = Movie()
            item.file = _episode['filename']
            item.path = path
            file = os.path.join(item.path, item.file)

            result = {'title': get_value('EpisodeName'), 'tvdb_id': get_value('id'),
                      'show_name': self.show['title'],
                      'episode_number': get_value('EpisodeNumber'), 'season_number': get_value('SeasonNumber'),
                      'aired': get_value('FirstAired'), 'guests': get_value('GuestStars'),
                      'imdb_id': get_value('IMDB_ID'), 'writer': get_value('Writer'),
                      'thumb': thumb, 'overview': get_value('Overview'), 'director': get_value('Director'),
                      'rating': get_value('Rating'), 'votes': get_value('RatingCount'),
                      'video_xml': Codec.get_video_xml([file]), 'audio_xml': Codec.get_audio_xml([file])}

            return result

        def get_nfo():
            xml = '<episodedetails>\n'
            xml += '    <title>{0}</title>\n'.format(episode['title'])
            xml += '    <rating>{0}</rating>\n'.format(episode['rating'])
            xml += '    <season>{0}</season>\n'.format(episode['season_number'])
            xml += '    <episode>{0}</episode>\n'.format(episode['episode_number'])
            xml += '    <plot>{0}</plot>\n'.format(
                episode['overview'].replace('\n', '').replace('\r', '').replace('\r\n', ''))
            xml += '    <thumb>{0}</thumb>\n'.format(episode['thumb'])
            xml += '    <aired>{0}</aired>\n'.format(episode['aired'])
            xml += '    <premiered>{0}</premiered>\n'.format(self.show['premiered'])  # premiered = release date of SHOW
            xml += '    <studio>{0}</studio>\n'.format(self.show['network'].encode('utf-8'))
            xml += '    <mpaa>{0}</mpaa>\n'.format(self.show['mpaa'])

            episode_credits = get_episode_credits(self.show['tmdb_id'], episode['season_number'],
                                                  episode['episode_number'])

            if episode_credits is not None and 'crew' in episode_credits:
                for c in episode_credits['crew']:
                    if c['department'] == 'Writing':
                        xml += '    <credits>{0}</credits>\n'.format(c['name'].encode('utf-8'))
                    if c['department'] == 'Directing':
                        xml += '    <director>{0}</director>\n'.format(c['name'].encode('utf-8'))

            if episode_credits is not None and 'cast' in episode_credits:
                for actor in episode_credits['cast']:
                    xml += '    <actor>\n'
                    xml += '        <name>{0}</name>\n'.format(actor['name'].encode('utf-8'))
                    if actor['character'] != "" and actor['character'] is not None:
                        xml += '        <role>{0}</role>\n'.format(actor['character'])
                    if actor['profile_path'] != '' and actor['profile_path'] is not None:
                        xml += '        <thumb>{0}</thumb>\n'.format(
                            'http://image.tmdb.org/t/p/w500' + actor['profile_path'])
                    xml += '    </actor>\n'

            if episode_credits is not None and 'guest_stars' in episode_credits:
                for actor in episode_credits['guest_stars']:
                    xml += '    <actor>\n'
                    xml += '        <name>{0}</name>\n'.format(actor['name'].encode('utf-8'))
                    if actor['character'] != "" and actor['character'] is not None:
                        xml += '        <role>{0}</role>\n'.format(actor['character'].encode('utf-8'))
                    if actor['profile_path'] != '' and actor['profile_path'] is not None:
                        xml += '        <thumb>{0}</thumb>\n'.format(
                            'http://image.tmdb.org/t/p/w500' + actor['profile_path'])
                    xml += '    </actor>\n'

            xml = unicode(xml, 'utf8')
            if episode['video_xml'] != '' or episode['audio_xml'] != '':
                xml += '    <fileinfo>\n'
                xml += '        <streamdetails>\n'
                xml += episode['video_xml']
                xml += episode['audio_xml']
                xml += '        </streamdetails>\n'
                xml += '    </fileinfo>\n'
            xml += '</episodedetails>'
            return xml

        nfo = ''
        for n in range(0, len(episodes)):
            episode = get_episode(episodes[n])
            if n > 0:
                nfo += '\n'
            nfo += get_nfo()

        return nfo

    def download_images(self):
        def download_fanart():
            def download_backdrops():

                log('Download Backdrops', LogLevel.Debug)
                path = self.show['path']
                backdrops = {}

                for backdrop in get_fanart('showbackground'):
                    backdrops[backdrop['url']] = backdrop['likes']

                backdrops = sorted(backdrops.iteritems(), key=operator.itemgetter(1), reverse=True)
                n = 0
                for backdrop in backdrops:
                    if not config.pyscrape.backdrop_limit <= 0 and n > (config.pyscrape.backdrop_limit - 1):
                        return

                    if n == 1 and config.show.download_extrafanart:
                        path = os.path.join(path, 'extrafanart')
                        if not os.path.exists(path):
                            os.makedirs(path)

                    url = backdrop[0]
                    if n == 0 and config.show.download_backdrop:
                        dst = os.path.join(path, 'fanart.jpg')
                    elif n != 0 and config.show.download_extrafanart:
                        dst = os.path.join(path, os.path.basename(backdrop[0]))

                    download(url, dst)
                    n += 1

            def get_fanart(category):
                try:
                    return fanart[category]
                except KeyError:
                    log('Fanart category ' + category + ' not found', LogLevel.Debug)
                    return []

            def download_logo():
                log('Download Logo', LogLevel.Debug)
                path = self.show['path']
                dst = os.path.join(path, 'logo.png')

                if len(get_fanart('hdtvlogo')) > 0:
                    for fa in get_fanart('hdtvlogo'):
                        if fa['lang'] == config.pyscrape.language:
                            download(fa['url'], dst)
                            return
                    for fa in get_fanart('hdtvlogo'):
                        if fa['lang'] == config.pyscrape.fallback_language:
                            download(fa['url'], dst)
                            return
                elif len(get_fanart('tvlogo')) > 0:
                    for fa in get_fanart('tvlogo'):
                        if fa['lang'] == config.pyscrape.language:
                            download(fa['url'], dst)
                            return
                    for fa in get_fanart('tvlogo'):
                        if fa['lang'] == config.pyscrape.fallback_language:
                            download(fa['url'], dst)
                            return

            def download_banner():
                log('Download Banner', LogLevel.Debug)
                banner = {}

                for b in get_fanart('tvbanner'):
                    if b['lang'] == config.pyscrape.language:
                        banner[b['url']] = b['likes']

                if len(banner) > 0:
                    banner = sorted(banner.iteritems(), key=operator.itemgetter(1), reverse=True)
                    dst = os.path.join(self.show['path'], 'banner.jpg')
                    for b in banner:
                        download(b[0], dst)
                        return
                else:
                    for b in get_fanart('tvbanner'):
                        if b['lang'] == config.pyscrape.fallback_language:
                            banner[b['url']] = b['likes']

                        if len(banner) > 0:
                            banner = sorted(banner.iteritems(), key=operator.itemgetter(1), reverse=True)
                            dst = os.path.join(self.show['path'], 'banner.jpg')
                            for b in banner:
                                download(b[0], dst)
                                return

            def download_thumbs():
                log('Download Thumbs', LogLevel.Debug)
                _thumbs = get_fanart('tvthumb')
                thumbs = {}

                if len(_thumbs) > 0:
                    for thumb in _thumbs:
                        if thumb['lang'] == config.pyscrape.language:
                            thumbs[thumb['url']] = thumb['likes']
                    if len(thumbs) == 0:
                        for thumb in _thumbs:
                            if thumb['lang'] == config.pyscrape.fallback_language:
                                thumbs[thumb['url']] = thumb['likes']
                    thumbs = sorted(thumbs.iteritems(), key=operator.itemgetter(1), reverse=True)

                    for n in range(0, len(thumbs)):
                        thumb = thumbs[n]
                        url = thumb[0]
                        path, name = '', ''

                        if n == 0 and config.show.download_landscape:
                            path = self.show['path']
                            name = 'landscape.jpg'
                        elif 0 < n <= 4 and config.show.download_thumbs:
                            path = self.show['path']
                            name = 'thumb{0}.jpg'.format(n)
                        elif n > 4 and config.show.download_extrathumbs:
                            path = os.path.join(self.show['path'], 'extrathumbs')
                            if not os.path.exists(path):
                                os.makedirs(path)
                            name = 'thumb{0}.jpg'.format(str(int(n - 4)))

                        if path != '' and name != '':
                            dst = os.path.join(path, name)
                            download(url, dst)

            def download_clearart():
                log('Download ClearArt', LogLevel.Debug)
                ca = get_fanart('hdclearart')
                clearart = {}

                if len(ca) == 0:
                    ca = get_fanart('clearart')
                if len(ca) == 0:
                    return

                for art in ca:
                    if art['lang'] == config.pyscrape.language:
                        clearart[art['url']] = art['likes']

                if len(clearart) == 0:
                    for art in ca:
                        if art['lang'] == config.pyscrape.fallback_language:
                            clearart[art['url']] = art['likes']
                if len(clearart) == 0:
                    return

                clearart = sorted(clearart.iteritems(), key=operator.itemgetter(1), reverse=True)
                for art in clearart:
                    dst = os.path.join(self.show['path'], 'clearart.png')
                    download(art[0], dst)
                    break

            def download_character_art():
                log('Download Character Art', LogLevel.Debug)
                ca = get_fanart('characterart')
                characterart = {}
                for art in ca:
                    characterart[art['url']] = art['likes']

                characterart = sorted(characterart.iteritems(), key=operator.itemgetter(1), reverse=True)
                for character in characterart:
                    download(character[0], os.path.join(self.show['path'], 'character.png'))
                    break

            def download_poster():
                log('Download Poster', LogLevel.Debug)
                posters = {}
                for poster in get_fanart('tvposter'):
                    posters[poster['url']] = poster['likes']

                posters = sorted(posters.iteritems(), key=operator.itemgetter(1), reverse=True)
                for poster in posters:
                    download(poster[0], os.path.join(self.show['path'], 'poster.jpg'))
                    return

            def download_season_banner():
                log('Download Season Banner', LogLevel.Debug)
                log('Season Banner aren\'t supported currently - fanart.tv have to update their API',
                    LogLevel.Debug)

            def download_season_thumbs():
                def download_thumb(thumb):
                    season = thumb['season']
                    while season.startswith('0'):
                        season = season[1:]
                    dst = os.path.join(self.show['path'], 'season' + season + '-landscape.jpg')

                    if os.path.isfile(dst):
                        return

                    utils.download(thumb['url'], dst)

                log('Download Season Thumbs', LogLevel.Debug)
                thumbs = []

                for thumb in get_fanart('seasonthumb'):
                    if thumb['lang'] == config.pyscrape.language and thumb['season'] != '':
                        thumbs.append(thumb)

                if len(thumbs) == 0:
                    for thumb in get_fanart('seasonthumb'):
                        if thumb['lang'] == '' and thumb['season'] != '':
                            thumbs.append(thumb)

                if len(thumbs) == 0:
                    for thumb in get_fanart('seasonthumb'):
                        if thumb['lang'] == config.pyscrape.fallback_language and thumb['season'] != '':
                            thumbs.append(thumb)

                for thumb in thumbs:
                    download_thumb(thumb)

            def download_season_poster():
                log('Download Season Poster', LogLevel.Debug)
                if self.show['tmdb_id'] is not None:
                    season_count = get_season_count(self.show['tmdb_id'])
                else:
                    season_count = 0

                for n in range(1, season_count + 1):
                    poster = get_season_poster(self.show['tmdb_id'], n)
                    if poster is not None:
                        src = 'http://image.tmdb.org/t/p/w1920' + poster
                        dst = os.path.join(self.show['path'], 'season{0}.tbn'.format(n))
                        download(src, dst)

            fanart = FanartTvApi.get_show(self.show['id'])
            if fanart is not None:
                for f in fanart:  # Fanart gives sometimes more than one result - but there are no double tmdbID's???
                    fanart = fanart[f]
                    break  # just take the first result, if there are more than 1

                if config.show.download_banner:
                    download_banner()
                if config.show.download_seasonbanner:
                    download_season_banner()
                if config.show.download_seasonthumbs:
                    download_season_thumbs()
                if config.show.download_seasonposter:
                    download_season_poster()
                if config.show.download_logo:
                    download_logo()
                if config.show.download_landscape:
                    download_thumbs()
                if config.show.download_clearart:
                    download_clearart()
                if config.show.download_characterart:
                    download_character_art()
                if config.show.download_poster:
                    download_poster()
                if config.show.download_backdrop:
                    download_backdrops()

        def download_from_tmdb(image_type, file_name=None):
            if file_name is None:
                file_name = image_type

            log('Try to get ' + image_type + ' from TMDB', LogLevel.Debug)
            if self.show[image_type] is not None and self.show[image_type] != '':
                dst = os.path.join(self.show['path'], file_name + '.jpg')
                download(self.show[image_type], dst)
            else:
                log('No image found for ' + image_type, LogLevel.Debug)

        log('Download images from fanart.tv')
        download_fanart()

        log('Start downloading missing Images from TMDB')
        if config.show.download_banner:
            if not os.path.exists(os.path.join(self.show['path'], 'banner.jpg')):
                download_from_tmdb('banner')

        if config.show.download_poster:
            if not os.path.exists(os.path.join(self.show['path'], 'poster.jpg')):
                download_from_tmdb('poster')

        if config.show.download_backdrop:
            if not os.path.exists(os.path.join(self.show['path'], 'fanart.jpg')):
                download_from_tmdb('fanart')

        if config.show.download_folder:
            if not os.path.exists(os.path.join(self.show['path'], 'folder.jpg')):
                download_from_tmdb('poster', 'folder')


def _download_zip(tvdb_id, language):
    def download_if_older(seconds):
        if os.path.exists(dst):
            creation_time = os.path.getctime(dst)
            current_time = time.time()
            time_difference = int(current_time - creation_time)
            if time_difference > seconds:
                os.remove(dst)
                download(zip_url, dst)
        else:
            download(zip_url, dst)

    tvdb_id = unicode(tvdb_id)
    zip_url = url_base + '/api/' + api_key + '/series/' + tvdb_id + '/all/' + language + '.zip'
    root = os.path.abspath(os.path.join(utils.get_root(), os.pardir))
    tmp_path = os.path.join(root, '.tmp')
    file_name = tvdb_id + '_' + language + '.zip'
    dst = os.path.join(tmp_path, file_name)

    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    download_if_older(86400)
    return {'core': zip_url, 'dst': dst}


def _get_mirror():
    mirrors = 'http://thetvdb.com/api/{0}/mirrors.xml'.format(api_key)
    log('Send TVDB Request: ' + mirrors.replace(api_key, 'XXX'), LogLevel.Debug)
    xml = urllib.urlopen(mirrors).read()
    dom = parseString(xml)

    for node in dom.getElementsByTagName('Mirror'):
        for n in node.getElementsByTagName('typemask'):
            if '<typemask>7</typemask>' in n.toxml().strip():
                for n in node.getElementsByTagName('mirrorpath'):
                    return n.firstChild.nodeValue


def get_show_nfo(show):
    log('Create tvshow.nfo')
    root = etree.Element('tvshow')

    child = etree.Element('title')
    child.text = show['title']
    root.append(child)

    child = etree.Element('showtitle')
    child.text = show['title']
    root.append(child)

    child = etree.Element('rating')
    child.text = show['rating']
    root.append(child)

    child = etree.Element('votes')
    child.text = show['votes']
    root.append(child)

    child = etree.Element('year')
    child.text = show['premiered'][:4]
    root.append(child)

    child = etree.Element('season')
    child.text = '-1'
    root.append(child)

    #xml += '    <top250>{0}</top250>\n'.format(show.top250)

    child = etree.Element('episode')
    child.text = str(show['episode_count'])
    root.append(child)

    child = etree.Element('plot')
    plot = show['plot'].replace('\n', '').replace('\r', '').replace('\r\n', '')
    child.text = unicode(plot, 'utf8')
    root.append(child)

    child = etree.Element('mpaa')
    child.text = show['mpaa']
    root.append(child)

    child = etree.Element('episodeguide')
    show_url = etree.SubElement(child, 'url')
    show_url.text = show['zip_url']
    root.append(child)

    child = etree.Element('id')
    child.text = show['id']
    root.append(child)

    for genre in show['genres']:
        child = etree.Element('genre')
        child.text = genre
        root.append(child)

    child = etree.Element('premiered')
    child.text = show['premiered']
    root.append(child)

    child = etree.Element('status')
    child.text = show['status']
    root.append(child)

    child = etree.Element('studio')
    child.text = show['network']
    root.append(child)

    for actor in show['actors']:
        child = etree.Element('actor')
        name = etree.SubElement(child, 'name')
        role = etree.SubElement(child, 'role')
        name.text = actor['name']
        role.text = actor['role']
        if actor['thumb'] != '':
            thumb = etree.SubElement(child, 'thumb')
            thumb.text = actor['thumb']
        root.append(child)

    return etree.tostring(root, pretty_print=True, encoding='utf8', xml_declaration=True)


@Cached
def get_id(title):
    title = title.replace(' ', '%20')
    url = 'http://thetvdb.com/api/GetSeries.php?seriesname=' + title + '&language=de'
    log('Send TVDB Request: ' + url, LogLevel.Debug)
    result = urllib.urlopen(url).read()
    dom = parseString(result)
    for node in dom.getElementsByTagName('Series'):
        for node in node.getElementsByTagName('seriesid'):
            return node.firstChild.nodeValue  # first result = best .. need better algorithm


def _read_from_zip(src, language):
    zip_file = ZipFile(src)
    banners = zip_file.read('banners.xml')
    actors = zip_file.read('actors.xml')
    lang = zip_file.read(language + '.xml')
    return {'banners': banners, 'actors': actors, 'lang': lang}


api_key = '6CC251D2F31B60D2'
url_base = _get_mirror()
config = Config()
