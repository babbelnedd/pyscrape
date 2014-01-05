# -*- coding: utf-8 -*-
import sys
import os
import re
import shutil
import time
import operator
import utils
import getopt
import traceback
from Xbmc import Xbmc
from TmdbApi import TmdbApi
from FanartTvApi import FanartTvApi
from Movie import Movie
from Logger import Logger, LogLevel
from Config import Config
from Codec import Codec
from Downloader import Downloader

try:
    import simplejson as json
except:
    import json

config = Config()
logger = Logger()
logger.init()
image_base_url = 'http://image.tmdb.org/t/p/w1920'


class MovieScraper(object):
    def __init__(self, path, single=False, refresh=False, force=False):
        self.refresh = refresh
        self.tmdb = TmdbApi()
        self.fanart = FanartTvApi()
        self.codec = None
        self.config = config
        self.force = force

        def scrape_movies(movies):
            total_elapsed = 0
            progressed = 0
            count_movies = len(movies)
            for m in movies:
                progressed += 1

                logger.whiteline()
                logger.log(m.path)
                logger.log('====================================')
                if not self.force:
                    if not os.path.isfile(os.path.join(m.path, m.file)):
                        logger.log('Skip - No file found', LogLevel.Warning)
                        continue
                start = time.time()
                if not self.refresh:
                    self.cleanup_dir(m)
                self.codec = Codec(logger, config, m)
                self.codec.delete_audio_tracks()
                movie = self.get_metadata(m)
                self.download_images(movie)
                end = time.time()
                elapsed = end - start
                total_elapsed += elapsed
                logger.log('{0} / {1} movies progressed'.format(progressed, count_movies))
                logger.log("%.2f s " % elapsed, 'TIME')
                logger.log("%.2f s total" % total_elapsed, 'TIME')
                logger.whiteline()

        if single:
            movies = []
            root, dir = os.path.split(path)
            m = self.get_movie(root, dir)
            movies.append(m)
        else:
            movies = self.get_movies(path)

        scrape_movies(movies)
        logger.log('Scraping done - have fun')

    def get_movie(self, root, path):
        def get_movie_files(path):
            return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
            and (os.path.splitext(f)[1] in utils.get_extensions())]

        movie = Movie()
        dir = path
        movie.path = path
        rx = re.search('\([0-9]{4}\)', path)
        if rx:
            year = rx.group()
            path = path.replace(year, '')
            movie.search_year = year.replace('(', '').replace(')', '')

        title = path.strip()
        movie.search_title = title
        movie.search_alternative_title = utils.replace(movie.search_title)
        movie.path = os.path.join(root, dir)

        files = get_movie_files(movie.path)
        if len(files) < 1:
            return movie

        if 'new.mkv' in files and len(files) > 1:
            os.remove(os.path.join(movie.path, 'new.mkv'))
            files = get_movie_files(movie.path)

        if len(files) < 2 and len(files) > 0:
            movie.file = files[0]
        return movie

    def get_movies(self, path):
        movies = []
        for movie in os.listdir(path.encode('utf8')):
            if not os.path.isdir(os.path.join(path, movie)):
                continue
            m = self.get_movie(path, movie)
            movies.append(m)
        return movies

    def get_metadata(self, movie):
        def get_basic_metadata(movie):
            logger.log('Get basic informations')
            result = self.tmdb.search_title(title=movie.search_title, year=movie.search_year,
                                            lang=self.config.pyscrape.language)
            results = result['results']
            if results == []:
                logger.log('No Results', LogLevel.Warning)
                return movie

            logger.log(str(len(results)) + ' Result(s) found')
            if len(results) > 1:
                logger.log('MORE THAN ONE RESULT FOUND - PLEASE CHECK THE RETRIEVED DATA!', LogLevel.Warning)

            for r in results:
                if movie.title != '':    # if the title occurs more than once, take the one with the highest popularity
                    if not (movie.search_title == r['title'] or movie.search_title == r['original_title']):
                        if movie.title == r[u'title'] and movie.popularity < float(r['popularity']):
                            logger.log('Found movie with higher popularity')
                        else:
                            continue

                movie.title = r[u'title']
                movie.year = r[u'release_date'][:4]
                movie.orig_title = r[u'original_title']
                movie.id = r['id']
                movie.rating = r['vote_average']
                movie.popularity = float(r['popularity'])

            return movie

        def get_advanced_metadata(movie):
            logger.log('Get advanced informations')
            info = self.tmdb.get_movie(movie.id, lang=self.config.pyscrape.language)
            if info is None:   # If there is no information get information for fallback language
                info = self.tmdb.get_movie(movie.id, lang=self.config.pyscrape.fallback_language)
            if info is None:
                pass           # What to do if there is no info for fallback language?

            movie.imdbID = info['imdb_id']
            movie.plot = info[u'overview']
            movie.tagline = info[u'tagline']
            movie.vote_count = info['vote_count']
            movie.revenue = info['revenue']
            if info['belongs_to_collection']:
                movie.collection = info['belongs_to_collection'][u'name']
            movie.mpaa = self.tmdb.get_certification(movie)
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
            return movie


        movie = get_basic_metadata(movie)
        if movie.id == '':
            logger.log('No match for {0}'.format(movie.search_title), LogLevel.Warning)
            return
        movie.trailer = self.tmdb.get_trailer(movie)
        movie = get_advanced_metadata(movie)
        movie.posters = self.tmdb.get_posters(movie.id)
        movie.thumb = self.tmdb.get_thumb(movie.id)
        movie.credits = self.tmdb.get_credits(movie.id)
        movie.runtime = self.codec.get_runtime()
        movie.audio_xml = self.codec.get_audio_xml()
        movie.video_xml = self.codec.get_video_xml()
        self.create_nfo(movie)
        return movie

    def create_nfo(self, movie):
        logger.log('Prepare NFO')
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<movie>\n'
        xml += u'    <title>{0}</title>\n'.format(movie.title)
        xml += u'    <originaltitle>{0}</originaltitle>\n'.format(movie.orig_title)
        xml += u'    <sorttitle>{0}</sorttitle>\n'.format(movie.sorted_title)
        xml += u'    <set>{0}</set>\n'.format(movie.collection)
        xml += '    <rating>{0}</rating>\n'.format(movie.rating)
        xml += '    <year>{0}</year>\n'.format(movie.year)
        #xml += '    <top250>{0}</top250>\n'.format(0)      # information is still missing
        xml += '    <votes>{0}</votes>\n'.format(movie.vote_count)
        xml += u'    <outline>{0}</outline>\n'.format(movie.outline)
        xml += u'    <tagline>{0}</tagline>\n'.format(movie.tagline)
        xml += u'    <plot>{0}</plot>\n'.format(movie.plot)
        if movie.mpaa != 'unknown':
            xml += u'    <mpaa>{0}</mpaa>\n'.format(movie.mpaa)
        xml += u'    <revenue>{0}</revenue>\n'.format(utils.intWithCommas(movie.revenue))
        xml += u'    <budget>{0}</budget>\n'.format(utils.intWithCommas(movie.budget))
        xml += '    <runtime>{0}</runtime>\n'.format(movie.runtime)
        xml += '    <thumb>{0}</thumb>\n'.format(movie.thumb)
        xml += '    <playcount>{0}</playcount>\n'.format(0)
        xml += '    <id>{0}</id>\n'.format(movie.imdbID)
        xml += u'    <trailer>plugin://plugin.video.youtube/?action=play_video&amp;videoid={0}</trailer>\n'.format(
            movie.trailer)
        for genre in movie.genres.split('/'):
            xml += u'    <genre>{0}</genre>\n'.format(genre)
        try:
            if len(movie.production_companies) > 0:
                xml += u'    <studio>{0}</studio>\n'.format(movie.production_companies.split('/')[0].strip())
        except:
            pass;
        xml += movie.credits
        if movie.video_xml != '' or movie.audio_xml != '':
            xml += '    <fileinfo>\n'
            xml += '        <streamdetails>\n'
            xml += movie.video_xml
            xml += movie.audio_xml
            xml += '        </streamdetails>\n'
            xml += '    </fileinfo>\n'

        xml += '</movie>'

        logger.log('Write NFO')
        fileName, fileExtension = os.path.splitext(movie.file)
        f = os.path.join(movie.path, fileName + '.nfo')
        file(f, 'w').write(xml.encode("utf8"))

    def download_images(self, movie, rights='777'):
        def download_backdrops():
            logger.log('Download Backdrops')
            path = movie.path
            movie.backdrops = self.tmdb.get_backdrops(movie.id)
            backdrops = sorted(movie.backdrops.iteritems(), key=operator.itemgetter(1), reverse=True)
            n = 0
            for backdrop in backdrops:
                if not config.pyscrape.backdrop_limit <= 0 and n > (config.pyscrape.backdrop_limit - 1):
                    return

                if n == 1:
                    path = os.path.join(path, 'extrafanart')
                    if not os.path.exists(path):
                        os.makedirs(path)

                url = backdrop[0]
                if n == 0:
                    dst = os.path.join(path, 'fanart.jpg')
                else:
                    dst = os.path.join(path, os.path.basename(backdrop[0]))

                downloader.download(url, dst)
                n += 1

        def download_posters():
            logger.log('Download posters')
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
                downloader.download(url, dst)
                n += 1

        def download_fanart():
            def get_fanart(category):
                try:
                    return fanart[category]
                except:
                    return []

            def download_logo():
                logger.log('Download Logo', LogLevel.Debug)
                if len(get_fanart('hdmovielogo')) > 0:
                    for fa in get_fanart('hdmovielogo'):
                        if fa['lang'] == self.config.pyscrape.language:
                            dst = os.path.join(movie.path, 'logo.png')
                            downloader.download(fa['url'], dst)
                            return
                    for fa in get_fanart('hdmovielogo'):
                        if fa['lang'] == self.config.pyscrape.fallback_language:
                            dst = os.path.join(movie.path, 'logo.png')
                            downloader.download(fa['url'], dst)
                            return
                elif len(get_fanart('movielogo')) > 0:
                    for fa in get_fanart('movielogo'):
                        if fa['lang'] == self.config.pyscrape.language:
                            dst = os.path.join(movie.path, 'logo.png')
                            downloader.download(fa['url'], dst)
                            return
                    for fa in get_fanart('movielogo'):
                        if fa['lang'] == self.config.pyscrape.fallback_language:
                            dst = os.path.join(movie.path, 'logo.png')
                            downloader.download(fa['url'], dst)
                            return

            def download_banner():
                logger.log('Download Banner', LogLevel.Debug)
                if len(get_fanart('moviebanner')) > 0:
                    banner = {}
                    for b in get_fanart('moviebanner'):
                        if b['lang'] == 'de':
                            banner[b['url']] = b['likes']
                    if len(banner) > 0:
                        banner = sorted(banner.iteritems(), key=operator.itemgetter(1), reverse=True)
                        dst = os.path.join(movie.path, 'banner.jpg')
                        for b in banner:
                            downloader.download(b[0], dst)
                            break                               # nur einen banner laden

            def download_thumbs():
                logger.log('Download Thumbs', LogLevel.Debug)
                _thumbs = get_fanart('moviethumb')
                thumbs = {}

                if len(_thumbs) > 0:
                    for thumb in _thumbs:
                        if thumb['lang'] == self.config.pyscrape.language:
                            thumbs[thumb['url']] = thumb['likes']
                    if len(thumbs) == 0:
                        for thumb in _thumbs:
                            if thumb['lang'] == self.config.pyscrape.fallback_language:
                                thumbs[thumb['url']] = thumb['likes']
                    thumbs = sorted(thumbs.iteritems(), key=operator.itemgetter(1), reverse=True)

                    for n in range(0, len(thumbs)):
                        thumb = thumbs[n]
                        url = thumb[0]

                        if n == 0:
                            path = movie.path
                            name = 'landscape.jpg'
                        elif n > 0 and n < 4:
                            path = movie.path
                            name = 'thumb{0}.jpg'.format(n)
                        else:
                            path = os.path.join(movie.path, 'extrathumbs')
                            if not os.path.exists(path):
                                os.makedirs(path)
                            name = 'thumb{0}.jpg'.format(str(int(n - 3)))

                        dst = os.path.join(path, name)
                        downloader.download(url, dst)

            def download_disc():
                logger.log('Download Disc Art', LogLevel.Debug)
                _discs = get_fanart('moviedisc')
                discs = {}
                if len(_discs) > 0:
                    for disc in _discs:
                        if disc['lang'] == self.config.pyscrape.language:
                            discs[disc['url']] = disc['likes']
                    if len(discs) == 0:
                        for disc in _discs:
                            if disc['lang'] == self.config.pyscrape.fallback_language:
                                discs[disc['url']] = disc['likes']
                    discs = sorted(discs.iteritems(), key=operator.itemgetter(1), reverse=True)

                    for disc in discs:
                        url = disc[0]
                        dst = os.path.join(movie.path, 'disc.png')
                        downloader.download(url, dst)
                        break

            def download_clearart():
                logger.log('Download ClearArt', LogLevel.Debug)
                ca = get_fanart('hdmovieclearart')
                clearart = {}

                if len(ca) == 0:
                    ca = get_fanart('movieclearart')
                if len(ca) == 0:
                    return
                for art in ca:
                    if art['lang'] == self.config.pyscrape.language:
                        clearart[art['url']] = art['likes']
                if len(clearart) == 0:
                    for art in ca:
                        if art['lang'] == self.config.pyscrape.fallback_language:
                            clearart[art['url']] = art['likes']
                if len(clearart) == 0:
                    return

                clearart = sorted(clearart.iteritems(), key=operator.itemgetter(1), reverse=True)
                for art in clearart:
                    dst = os.path.join(movie.path, 'clearart.png')
                    downloader.download(art[0], dst)
                    break

            fanart = self.fanart.get_all(movie.imdbID)
            if fanart is None:
                return
            for f in fanart:     # Fanart gives sometimes more than one result - but there are no double tmdbID's???
                fanart = fanart[f]
                break            # just take the first result, if there are more than 1

            logger.log('Download Fanart')
            download_banner()
            download_logo()
            download_thumbs()
            download_disc()
            download_clearart()

        downloader = Downloader(refresh=self.refresh)
        download_backdrops()
        download_posters()
        download_fanart()

    def cleanup_dir(self, movie):
        logger.log('Delete old files')
        for item in os.listdir(movie.path):
            item = os.path.join(movie.path, item)
            ext = os.path.splitext(item)[1].lower()
            if ext in utils.get_extensions():
                continue
            elif os.path.isfile(item):
                logger.log('Delete ' + item, LogLevel.Debug)
                os.remove(item)
            elif os.path.isdir(item):
                deletable = True
                for d in os.listdir(item):     # Prüfe ob der Ordner keine .mkv datei enthält
                    ext = os.path.splitext(d)[1].lower()
                    if ext in utils.get_extensions():
                        deletable = False
                    else:
                        file = os.path.join(item, d)
                        logger.log('Delete ' + file, LogLevel.Debug)
                        os.remove(file)
                if deletable:
                    logger.log('Delete ' + item, LogLevel.Debug)
                    shutil.rmtree(item)


def main(arguments):
    def scrape_from_config(parameter):
        for path in config.movie.paths:
            if not os.path.isdir(path):
                continue
            if config.pyscrape.rename:
                utils.rename_subfolder(path)
            MovieScraper(path, single=False, refresh=parameter['refresh'], force=parameter['force'])

    def scrape_single_path(path):
        if os.path.isdir(path):
            if config.pyscrape.rename:
                path = utils.rename_dir(path)
                utils.rename_files(path)
            MovieScraper(path, single=True, refresh=parameter['refresh'], force=parameter['force'])
        else:
            logger.log('Path not found!', LogLevel.Error)
            sys.exit()

    def get_parameter(arguments):
        try:
            opts, args = getopt.getopt(arguments, "p:r:u:f",
                                       ["path=", "refresh", "update-xbmc", "force"])
        except getopt.GetoptError:
            logger.log('Wrong arguments', LogLevel.Error)
            print '-p --path             paths (seperated by "::")'
            print '-r --refresh          Do not delete existing files'
            print '-u --update-xbmc      Clean/Update XBMC'
            print '-f --force            Do not skip even if no movie file was found'
            sys.exit(2)

        single_path = ''
        refresh = False
        update = False
        force = False

        for opt, arg in opts:
            if opt in ("-p", "--path"):
                path = arg
                try:
                    path = unicode(arg).encode('utf-8')
                except:
                    pass
                single_path = path
            elif opt in ("-r", "--refresh"):
                refresh = True
            elif opt in ("-u", "--update-xbmc"):
                update = True
            elif opt in ("-f", "--force"):
                force = True

        return {'single_path': single_path, 'refresh': refresh, 'update': update, 'force': force}

    parameter = get_parameter(arguments)

    if parameter['single_path'] != '':
        scrape_single_path(parameter['single_path'])
    else:
        scrape_from_config(parameter)

    if parameter['update']:
        xbmc = Xbmc()
        xbmc.full_scan()


try:
    main(sys.argv[1:])
except Exception, e:
    logger.log('oops something went wrong :/', LogLevel.Error)
    logger.log('sys.argv:', LogLevel.Error)
    for a in sys.argv:
        logger.log(a, LogLevel.Error)
    logger.log(traceback.format_exc(), LogLevel.Error)
