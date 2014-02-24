import re
import sys
import os
import shutil
import time
import getopt
import traceback
import operator
from lxml import etree

import utils
import RegEx
import FanartTvApi
from Xbmc import Xbmc
import TmdbApi as Tmdb
from Movie import Movie
from Logger import log, LogLevel, whiteline
from Config import Config
import Codec
from utils import download


delete_existing = False
refresh = False
nfo_only = False
force = False
config = Config()


def get_movie(root, path):
    def get_movie_files(movie_path):
        return [f for f in os.listdir(movie_path) if os.path.isfile(os.path.join(movie_path, f)) and (
            os.path.splitext(f)[1] in utils.get_movie_extensions())]

    movie = Movie()
    movie.path = path

    regex = RegEx.get_movie(movie.path)
    movie.search_year = regex['year']
    movie.imdb = regex['imdbID']
    movie.search_title = regex['title']
    movie.search_alternative_title = utils.replace(regex['title'])
    movie.path = os.path.join(root, movie.path)

    files = get_movie_files(movie.path)
    if len(files) < 1:
        return movie

    # todo: this *should* not longer be needed,
    if 'new.mkv' in files and len(files) > 1:
        os.remove(os.path.join(movie.path, 'new.mkv'))
        files = get_movie_files(movie.path)

    # todo: implement multi cd support
    if len(files) == 1:
        movie.files = [files[0]]

    if len(files) > 1:
        # get only files that are tagged as CD
        for _file in [f for f in files if RegEx.get_cd(f) == '']:
            files.remove(_file)

        movie.files = files

    return movie


def get_movies(path):
    movies = []
    for movie in os.listdir(path.encode('utf8')):
        if not os.path.isdir(os.path.join(path, movie)):
            continue
        m = get_movie(path, movie)
        movies.append(m)
    return movies


def create_nfo(movie):
    log('Create NFO')
    root = etree.Element('movie')

    child = etree.Element('title')
    child.text = movie.title
    root.append(child)

    child = etree.Element('originaltitle')
    child.text = movie.orig_title
    root.append(child)

    child = etree.Element('sorttitle')
    child.text = movie.sorted_title
    root.append(child)

    if movie.collection is not None and movie.collection != '':
        child = etree.Element('set')
        child.text = movie.collection
        root.append(child)

    child = etree.Element('rating')
    child.text = str(movie.rating)
    root.append(child)

    child = etree.Element('votes')
    child.text = str(movie.vote_count)
    root.append(child)

    child = etree.Element('year')
    child.text = movie.year
    root.append(child)

    #xml += '    <top250>{0}</top250>\n'.format(0)      # information is still missing

    if movie.outline is not None and movie.outline != '':
        child = etree.Element('outline')
        child.text = movie.outline
        root.append(child)

    if movie.tagline is not None and movie.tagline != '':
        child = etree.Element('tagline')
        child.text = movie.tagline
        root.append(child)

    child = etree.Element('plot')
    child.text = movie.plot
    root.append(child)

    if movie.mpaa is not None and movie.mpaa != 'unknown':
        child = etree.Element('mpaa')
        child.text = movie.mpaa
        root.append(child)

    if movie.revenue is not None and movie.revenue != '' and movie.revenue != 0:
        child = etree.Element('revenue')
        child.text = utils.intWithCommas(movie.revenue)
        root.append(child)

    if movie.budget is not None and movie.budget != '' and movie.budget != 0:
        child = etree.Element('budget')
        child.text = utils.intWithCommas(movie.budget)
        root.append(child)

    if movie.runtime is not None and movie.runtime != '' and movie.runtime != '0':
        child = etree.Element('runtime')
        child.text = movie.runtime
        root.append(child)

    child = etree.Element('thumb')
    child.text = movie.thumb
    root.append(child)

    child = etree.Element('playcount')
    child.text = '0'
    root.append(child)

    child = etree.Element('id')
    child.text = movie.imdb
    root.append(child)

    if movie.trailer is not None and movie.trailer != '':
        child = etree.Element('trailer')
        child.text = 'plugin://plugin.video.youtube/?action=play_video&amp;videoid={0}'.format(movie.trailer)
        root.append(child)

    for genre in movie.genres.split('/'):
        child = etree.Element('genre')
        child.text = genre
        root.append(child)

    if len(movie.production_companies) > 0:
        child = etree.Element('studio')
        child.text = movie.production_companies.split('/')[0].strip()
        root.append(child)

    movie_credits = Tmdb.get_credits(movie.id)
    for credit in movie_credits['credits']:
        child = etree.Element('director')
        child.text = credit
        root.append(child)

    for director in movie_credits['directors']:
        child = etree.Element('director')
        child.text = director
        root.append(child)

    for actor in movie_credits['actors']:
        _actor = etree.Element('actor')
        name = etree.SubElement(_actor, 'name')
        role = etree.SubElement(_actor, 'role')

        name.text = actor['name']
        role.text = actor['role']
        if actor['thumb'] is not None:
            thumb = etree.SubElement(_actor, 'thumb')
            thumb.text = 'http://image.tmdb.org/t/p/w500' + actor['thumb']

        root.append(_actor)

    if len(movie.files) > 0:
        videos = [os.path.join(movie.path, v) for v in movie.files]
        vinfo = Codec.get_vinfo(videos[0])
        ainfo = Codec.get_ainfo(videos[0])

        fileinfo = etree.Element('fileinfo')
        streamdetails = etree.SubElement(fileinfo, 'streamdetails')

        video = etree.SubElement(streamdetails, 'video')
        aspect = etree.SubElement(video, 'aspect')
        video_codec = etree.SubElement(video, 'codec')
        duration = etree.SubElement(video, 'durationinseconds')
        width = etree.SubElement(video, 'width')
        height = etree.SubElement(video, 'height')
        scantype = etree.SubElement(video, 'scantype')

        aspect.text = str(vinfo['aspect'])
        video_codec.text = vinfo['codec']
        duration.text = str(int(Codec.get_runtime(videos)) * 60)
        width.text = str(vinfo['width'])
        height.text = str(vinfo['height'])
        scantype.text = vinfo['scantype']

        for info in ainfo:
            audio = etree.SubElement(streamdetails, 'audio')
            channels = etree.SubElement(audio, 'channels')
            audio_codec = etree.SubElement(audio, 'codec')
            language = etree.SubElement(audio, 'language')

            channels.text = info['channel_count']
            audio_codec.text = info['format']
            language.text = info['language']

        root.append(fileinfo)

    log('Write NFO to disk', LogLevel.Debug)
    if len(movie.files) > 0:
        filename, extension = os.path.splitext(movie.files[0])
        regex = re.search('\cd[0-9]', filename, re.IGNORECASE)
        if regex:
            filename = filename.replace(regex.group(), '').strip()
    else:
        filename = ''

    if filename == '':
        filename = os.path.basename(movie.path)
    nfo_file = os.path.join(movie.path, filename + '.nfo')
    file(nfo_file, 'w').write(etree.tostring(root, pretty_print=True, encoding='utf8', xml_declaration=True))


def cleanup_dir(movie):
    global delete_existing
    if not delete_existing:
        return

    log('Delete old files')
    for item in os.listdir(movie.path):
        item = os.path.join(movie.path, item)
        ext = os.path.splitext(item)[1].lower()
        if ext in utils.get_all_extensions():
            continue
        elif os.path.isfile(item):
            log('Delete ' + item, LogLevel.Debug)
            os.remove(item)
        elif os.path.isdir(item):
            deletable = True
            for extension in [os.path.splitext(e)[1].lower() for e in os.listdir(item)]:
                if extension in utils.get_all_extensions():
                    deletable = False
            if deletable:
                log('Delete ' + item, LogLevel.Debug)
                shutil.rmtree(item)


def download_images(movie):
    def download_backdrops():
        log('Download Backdrops')
        path = movie.path
        movie.backdrops = Tmdb.get_backdrops(movie.id)
        backdrops = sorted(movie.backdrops.iteritems(), key=operator.itemgetter(1), reverse=True)
        n = 0
        for backdrop in backdrops:
            if not config.pyscrape.backdrop_limit <= 0 and n > (config.pyscrape.backdrop_limit - 1):
                return

            if n == 1:
                if not config.movie.download_extrafanart:
                    return

                path = os.path.join(path, 'extrafanart')
                if not os.path.exists(path):
                    os.makedirs(path)

            url = backdrop[0]
            if n == 0:
                dst = os.path.join(path, 'fanart.jpg')
            else:
                dst = os.path.join(path, os.path.basename(backdrop[0]))

            download(src=url, dst=dst, refresh=_refresh)
            n += 1

    def download_posters():
        log('Download posters')
        path = movie.path
        n = 0
        for poster in movie.posters:
            if not config.pyscrape.poster_limit <= 0 and n > (config.pyscrape.backdrop_limit - 1):
                return

            url = poster[0]
            if n > 0:
                number = n
            else:
                number = ''
            dst = os.path.join(path, 'poster{0}.jpg'.format(number))
            download(src=url, dst=dst, refresh=_refresh)
            n += 1

    def download_fanart():
        def get_fanart(category):
            try:
                return fanart[category]
            except KeyError:
                return []

        def download_logo():
            log('Download Logo', LogLevel.Debug)
            if len(get_fanart('hdmovielogo')) > 0:
                for fa in get_fanart('hdmovielogo'):
                    if fa['lang'] == config.pyscrape.language:
                        dst = os.path.join(movie.path, 'logo.png')
                        download(src=fa['url'], dst=dst, refresh=_refresh)
                        return
                for fa in get_fanart('hdmovielogo'):
                    if fa['lang'] == config.pyscrape.fallback_language:
                        dst = os.path.join(movie.path, 'logo.png')
                        download(src=fa['url'], dst=dst, refresh=_refresh)
                        return
            elif len(get_fanart('movielogo')) > 0:
                for fa in get_fanart('movielogo'):
                    if fa['lang'] == config.pyscrape.language:
                        dst = os.path.join(movie.path, 'logo.png')
                        download(src=fa['url'], dst=dst, refresh=_refresh)
                        return
                for fa in get_fanart('movielogo'):
                    if fa['lang'] == config.pyscrape.fallback_language:
                        dst = os.path.join(movie.path, 'logo.png')
                        download(src=fa['url'], dst=dst, refresh=_refresh)
                        return

        def download_banner():
            log('Download Banner', LogLevel.Debug)
            if len(get_fanart('moviebanner')) > 0:
                banners = {}
                for b in get_fanart('moviebanner'):
                    if b['lang'] == config.pyscrape.language:
                        banners[b['url']] = b['likes']
                if len(banners) > 0:
                    banners = sorted(banners.iteritems(), key=operator.itemgetter(1), reverse=True)
                    dst = os.path.join(movie.path, 'banner.jpg')
                    for b in banners:
                        download(src=b[0], dst=dst, refresh=_refresh)
                        return
                else:
                    for b in get_fanart('moviebanner'):
                        if b['lang'] == config.pyscrape.fallback_language:
                            banners[b['url']] = b['likes']
                        if len(banners) > 0:
                            banners = sorted(banners.iteritems(), key=operator.itemgetter(1), reverse=True)
                            dst = os.path.join(movie.path, 'banner.jpg')
                            for banner in banners:
                                download(src=banner[0], dst=dst, refresh=_refresh)
                                return

        def download_thumbs():
            log('Download Thumbs', LogLevel.Debug)
            _thumbs = get_fanart('moviethumb')
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

                    path = ''
                    name = ''
                    if n == 0 and config.movie.download_landscape:
                        path = movie.path
                        name = 'landscape.jpg'
                    elif 0 < n <= 4 and config.movie.download_thumbs:
                        path = movie.path
                        name = 'thumb{0}.jpg'.format(n)
                    elif n > 4 and config.movie.download_extrathumbs:
                        path = os.path.join(movie.path, 'extrathumbs')
                        if not os.path.exists(path):
                            os.makedirs(path)
                        name = 'thumb{0}.jpg'.format(str(int(n - 4)))

                    if path != '' and name != '':
                        dst = os.path.join(path, name)
                        download(src=url, dst=dst, refresh=_refresh)

        def download_disc():
            log('Download Disc Art', LogLevel.Debug)
            _discs = get_fanart('moviedisc')
            discs = {}
            if len(_discs) > 0:
                for disc in _discs:
                    if disc['lang'] == config.pyscrape.language:
                        discs[disc['url']] = disc['likes']
                if len(discs) == 0:
                    for disc in _discs:
                        if disc['lang'] == config.pyscrape.fallback_language:
                            discs[disc['url']] = disc['likes']
                discs = sorted(discs.iteritems(), key=operator.itemgetter(1), reverse=True)

                for disc in discs:
                    url = disc[0]
                    dst = os.path.join(movie.path, 'disc.png')
                    download(src=url, dst=dst, refresh=_refresh)
                    break

        def download_clearart():
            log('Download ClearArt', LogLevel.Debug)
            ca = get_fanart('hdmovieclearart')
            clearart = {}

            if len(ca) == 0:
                ca = get_fanart('movieclearart')
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
                dst = os.path.join(movie.path, 'clearart.png')
                download(src=art[0], dst=dst, refresh=_refresh)
                break

        fanart = FanartTvApi.get_movie(movie.imdb)
        if fanart is None:
            return
        for f in fanart:  # Fanart gives sometimes more than one result - but there are no double tmdbID's???
            fanart = fanart[f]
            break  # just take the first result, if there are more than 1

        if config.movie.download_banner or config.movie.download_logo or config.movie.download_landscape or \
                config.movie.download_disc or config.movie.download_clearart:
            log('Download Fanart')
            if config.movie.download_banner:
                download_banner()
            if config.movie.download_logo:
                download_logo()
            if config.movie.download_landscape:
                download_thumbs()
            if config.movie.download_disc:
                download_disc()
            if config.movie.download_clearart:
                download_clearart()

    global delete_existing
    _refresh = True
    if refresh or delete_existing:
        _refresh = False

    if config.movie.download_backdrop:
        download_backdrops()
    if config.movie.download_poster:
        download_posters()

    download_fanart()


def get_metadata(movie):
    def get_basic_metadata():
        log('Get basic information')
        result = Tmdb.search_title(title=movie.search_title, year=movie.search_year,
                                   lang=config.pyscrape.language, imdb_id=movie.imdb)

        if not result:
            log('No Results', LogLevel.Warning)
            return movie

        if movie.imdb is None or movie.imdb == '':
            log(str(len(result)) + ' Result(s) found')
            if len(result) > 1:
                log('MORE THAN ONE RESULT FOUND - PLEASE CHECK THE RETRIEVED DATA!', LogLevel.Warning)

            for r in result:
                if movie.title != '':  # if the title occurs more than once take the one with the highest popularity
                    if not (movie.search_title == r['title'] or movie.search_title == r['original_title']):
                        if movie.title == r[u'title'] and movie.popularity < float(r['popularity']):
                            log('Found movie with higher popularity')
                        else:
                            continue

                movie.title = r[u'title']
                movie.year = r[u'release_date'][:4]
                movie.orig_title = r[u'original_title']
                movie.id = r['id']
                movie.rating = r['vote_average']
                movie.popularity = float(r['popularity'])
        else:
            movie.title = result[u'title']
            movie.year = result[u'release_date'][:4]
            movie.orig_title = result[u'original_title']
            movie.id = result['id']
            movie.rating = result['vote_average']
            movie.popularity = float(result['popularity'])

    def get_advanced_metadata():
        log('Get advanced informations')
        info = Tmdb.get_movie(movie.id, lang=config.pyscrape.language)
        if info is None:  # If there is no information get information for fallback language
            info = Tmdb.get_movie(movie.id, lang=config.pyscrape.fallback_language)
        if info is None:
            pass  # What to do if there is no info for fallback language?

        movie.imdb = info['imdb_id']
        movie.plot = info[u'overview']
        movie.tagline = info[u'tagline']
        movie.vote_count = info['vote_count']
        movie.revenue = info['revenue']
        if info['belongs_to_collection']:
            movie.collection = info['belongs_to_collection'][u'name']
        movie.mpaa = Tmdb.get_certification(movie)
        movie.sorted_title = movie.title
        movie.budget = info['budget']
        for country in info['production_countries']:
            movie.production_countries += ' / ' + country[u'name']
        for genre in info['genres']:
            if movie.genres != '':
                movie.genres += '/'
            movie.genres += u'{0}'.format(genre['name'])
        for company in info['production_companies']:
            if movie.production_companies != '':
                movie.production_companies += ' / '
            movie.production_companies += u'{0}'.format(company['name'])
        for language in info['spoken_languages']:
            movie.spoken_languages.append(language[u'name'])

    get_basic_metadata()
    if movie.id == '':
        log('No match for {0}'.format(movie.search_title), LogLevel.Warning)
        return -1

    files = []
    for movie_file in movie.files:
        files.append(os.path.join(movie.path, movie_file))

    movie.trailer = Tmdb.get_trailer(movie)
    get_advanced_metadata()
    movie.posters = Tmdb.get_posters(movie.id)
    movie.thumb = Tmdb.get_thumb(movie.id)
    movie.runtime = Codec.get_runtime(files)
    create_nfo(movie)
    return movie


def scrape_movies(path, single=False):
    def _scrape(all_movies):
        total_elapsed = 0
        progressed = 0
        count_movies = len(all_movies)
        for movie in all_movies:
            progressed += 1
            whiteline()
            log(movie.path)
            log('====================================')
            if not force:
                if not os.path.isfile(os.path.join(movie.path, movie.files[0])):
                    log('Skip - No file found', LogLevel.Warning)
                    continue

            start_time = time.time()

            if not refresh:
                cleanup_dir(movie)

            if nfo_only:
                get_metadata(movie)
            else:
                files = []
                for movie_file in movie.files:
                    files.append(os.path.join(movie.path, movie_file))

                if config.codec.keep_tracks:
                    Codec.delete_audio_tracks(files)

                movie = get_metadata(movie)
                if movie == -1:  # no movie found
                    continue

                download_images(movie)
            end = time.time()
            elapsed = end - start_time
            total_elapsed += elapsed
            log('{0} / {1} movies progressed'.format(progressed, count_movies))
            log("%.2f s " % elapsed, 'TIME')
            log("%.2f s total" % total_elapsed, 'TIME')
            whiteline()

    if single:
        movies = []
        root, directory = os.path.split(path)
        m = get_movie(root, directory)
        movies.append(m)
    else:
        movies = get_movies(path)

    _scrape(movies)
    log('Scraping done - have fun')


def __start():
    def requirements_satisfied():

        result = True
        if config.fanart.api_key == '':
            log('FanartTV Api Key is missing', LogLevel.Error)
            result = False
        if config.tmdb.api_key == '':
            log('TMDB Api Key is missing', LogLevel.Error)
            result = False
        if config.codec.mediainfo_path == '':
            log('Mediainfo is not set', LogLevel.Warning)
        if config.codec.mkvmerge == '':
            log('MkvMerge is not set', LogLevel.Warning)

        return result

    def main(arguments):
        def scrape_from_config():
            for path in config.movie.paths:
                if not os.path.isdir(path):
                    continue
                if config.pyscrape.rename:
                    utils.rename_subfolder(path)
                scrape_movies(path, single=False)

        def scrape_single_path(path):
            if os.path.isdir(path):
                if config.pyscrape.rename:
                    path = utils.rename_dir(path)
                    utils.rename_files(path)
                scrape_movies(path, single=True)
            else:
                log('Path not found!', LogLevel.Error)
                sys.exit()

        def get_parameter(system_arguments):
            try:
                opts, args = getopt.getopt(system_arguments, "p:r:u:f:d",
                                           ["path=", "refresh", "update-xbmc", "force", "nfo-only",
                                            "delete-existing"])
            except getopt.GetoptError:
                log('Wrong arguments', LogLevel.Error)
                print '-p --path             paths (seperated by "::")'
                print '-r --refresh          Do not delete existing files'
                print '-u --update-xbmc      Clean/Update XBMC'
                print '-f --force            Do not skip even if no movie file was found'
                print '   --nfo-only         Only creates a .nfo file'
                print '-d --delete-existing  Delete all files from a movie except ' \
                      'for these with a extenstion from the extension list'

                sys.exit(2)
            global delete_existing
            single_path = ''
            refresh = False
            update = False
            force = False
            nfo_only = False

            for opt, arg in opts:
                if opt in ("-p", "--path"):
                    path = arg
                    try:
                        path = unicode(arg).encode('utf-8')
                    except UnicodeDecodeError:
                        pass
                    single_path = path
                elif opt in ("-r", "--refresh"):
                    refresh = True
                elif opt in ("-u", "--update-xbmc"):
                    update = True
                elif opt in ("-f", "--force"):
                    force = True
                elif opt in "--nfo-only":
                    nfo_only = True
                elif opt in ("-d", "--delete-existing"):
                    delete_existing = True

            return {'single_path': single_path, 'refresh': refresh, 'update': update, 'force': force,
                    'nfo_only': nfo_only}

        global refresh, nfo_only, force
        parameter = get_parameter(arguments)
        refresh = parameter['refresh']
        nfo_only = parameter['nfo_only']
        force = parameter['force']

        if parameter['single_path'] != '':
            scrape_single_path(parameter['single_path'])
        else:
            scrape_from_config()

        if parameter['update']:
            xbmc = Xbmc()
            xbmc.full_scan()

    try:
        if requirements_satisfied():
            main(sys.argv[1:])
    except Exception, e:
        log('oops something went wrong : /', LogLevel.Error)
        log(unicode(e), LogLevel.Error)
        log('sys.argv:', LogLevel.Error)
        for a in sys.argv:
            log(a, LogLevel.Error)
        log(traceback.format_exc(), LogLevel.Error)


if __name__ == '__main__':
    try:
        __start()
    except KeyboardInterrupt:
        log("MovieScraper was interrupted by user", LogLevel.Warning)