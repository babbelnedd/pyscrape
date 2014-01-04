# -*- coding: utf-8 -*-
__author__ = 'LSC'
from TmdbApi import TmdbApi
from FanartTvApi import FanartTvApi
from Movie import Movie
from Logger import Logger, LogLevel
from Config import Config
from Codec import Codec
import sys, os, re, shutil, time, operator, urllib, utils, getopt, traceback

try:
    import simplejson as json
except:
    import json

config = Config(os.path.join('/home/pyscrape/src/pyscrape/', 'system', 'pyscrape.cfg'))
logger = Logger('pyscrape.log', config)
image_base_url = 'http://image.tmdb.org/t/p/w1920'

class MovieScraper(object):
    def __init__(self, path, single=False,refresh=False):
        self.refresh = refresh
        def getChanges():
            pass
            changedMovies = self.tmdb.getChanges()['results']
            print changedMovies
            for movie in changedMovies:
                logger.log('CHANGES:', LogLevel.Error)
                logger.log(movie, LogLevel.Error)

        self.tmdb = TmdbApi(config, logger)
        self.fanart = FanartTvApi(config, logger)
        self.codec = None
        # getChanges()

        def scrapeMovies(movies):
            total_elapsed = 0
            progressed = 0
            count_movies = len(movies)
            for m in movies:
                progressed += 1

                logger.whiteline()
                logger.log(m.path)
                logger.log('====================================')
                if not os.path.isfile(os.path.join(m.path, m.file)):
                    logger.log('Skip - No file found', LogLevel.Warning)
                    continue
                start = time.time()
                if not self.refresh:
                    self.cleanUp(m)
                self.codec = Codec(logger, config, m)
                self.codec.deleteAudioTracks()
                movie = self.getMetadata(m)
                end = time.time()
                elapsed = end - start
                total_elapsed += elapsed
                logger.log('{0} / {1} movies progressed'.format(progressed, count_movies))
                logger.log("%.2f s " % elapsed, 'TIME')
                logger.log("%.2f s total" % total_elapsed, 'TIME')
                logger.whiteline()

        self.config = config
        if single:
            movies = []
            root, dir = os.path.split(path)
            m = self.getSingleMovie(root, dir)
            movies.append(m)
        else:
            movies = self.getMissingMovies(path)

        scrapeMovies(movies)
        logger.log('Scraping done - have fun')


    def getSingleMovie(self, root, path):
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
        files = [f for f in os.listdir(movie.path) if
                 os.path.isfile(os.path.join(movie.path, f)) and (f.endswith('.mkv') or f.endswith('.avi'))]
        if len(files) > 0:
            if 'new.mkv' in files and len(files) > 1:
                os.remove(os.path.join(movie.path, 'new.mkv'))
            if len(files) < 2 and len(files) > 0:
                files = [f for f in os.listdir(movie.path) if
                         os.path.isfile(os.path.join(movie.path, f)) and (f.endswith('.mkv') or f.endswith('.avi'))]
                movie.file = files[0]
        return movie

    def getMissingMovies(self, path):
        movies = []
        for movie in os.listdir(path.encode('utf8')):
            if not os.path.isdir(os.path.join(path, movie)):
                continue
            m = self.getSingleMovie(path, movie)
            movies.append(m)
        return movies

    def getMetadata(self, movie):
        def getBasicMetadata(movie):
            logger.log('Get basic informations')
            result = self.tmdb.searchByTitle(title=movie.search_title, year=movie.search_year,
                                             lang=self.config.pyscrape.language)
            results = result['results']
            if results == []:
                logger.log('No Results', LogLevel.Warning)
                return movie

            logger.log(str(len(results)) + ' Result(s) found')
            if len(results) > 1:
                logger.log('MORE THAN ONE RESULT FOUND - PLEASE CHECK THE RETRIEVED DATA!', LogLevel.Warning)
                logger.log(movie.path, 'WARNING')

            for r in results:
                if movie.title != '':    # falls der titel mehrmals vorkommt, den mit der höchsten popularity nehmen
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

                #break   # das erste ergebnis muss ab jetzt richtig sein :S

            return movie

        def getAdvancedMetadata(movie):
            logger.log('Get advanced informations')
            info = self.tmdb.getMovie(movie.id, lang=self.config.pyscrape.language)
            if info is None:   # todo: hmm verbessern.. falls plot == "" ist? :/
                info = self.tmdb.getMovie(movie.id, lang=self.config.pyscrape.fallback_language)

            movie.imdbID = info['imdb_id']
            movie.plot = info[u'overview']
            movie.tagline = info[u'tagline']
            movie.vote_count = info['vote_count']
            movie.revenue = info['revenue']
            if info['belongs_to_collection']:
                movie.collection = info['belongs_to_collection'][u'name']
            movie.mpaa = self.tmdb.getCertification(movie)
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


        movie = getBasicMetadata(movie)
        if movie.id == '':
            logger.log('No match for {0}'.format(movie.search_title), LogLevel.Warning)
            return
        movie.trailer = self.tmdb.getTrailer(movie)
        movie = getAdvancedMetadata(movie)
        movie.posters = self.tmdb.getPosters(movie.id)
        movie.thumb = self.tmdb.getThumb(movie.id)
        movie.credits = self.tmdb.getCredits(movie.id)
        movie.runtime = self.codec.getRuntime()
        movie.audio_xml = self.codec.getAudioXml()
        movie.video_xml = self.codec.getVideoXml()
        self.writeNFO(movie)
        self.downloadImages(movie)
        return movie

    def writeNFO(self, movie):
        logger.log('Prepare NFO')
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<movie>\n'
        xml += u'    <title>{0}</title>\n'.format(movie.title)
        xml += u'    <originaltitle>{0}</originaltitle>\n'.format(movie.orig_title)
        xml += u'    <sorttitle>{0}</sorttitle>\n'.format(movie.sorted_title)
        xml += u'    <set>{0}</set>\n'.format(movie.collection)
        xml += '    <rating>{0}</rating>\n'.format(movie.rating)
        xml += '    <year>{0}</year>\n'.format(movie.year)
        #xml += '    <top250>{0}</top250>\n'.format(0)                           # INFORMATION FEHLT NOCH - ANPASSEN!!!
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
        #xml += u'    <filenameandpath>{0}</filenameandpath>\n'.format(movie.file.encode('utf8'))
        xml += u'    <trailer>plugin://plugin.video.youtube/?action=play_video&amp;videoid={0}</trailer>\n'.format(
            movie.trailer)
        for genre in movie.genres.split('/'):
            xml += u'    <genre>{0}</genre>\n'.format(genre)
        try:
            if len(movie.production_companies) > 0:
                xml += u'    <studio>{0}</studio>\n'.format(movie.production_companies.split('/')[0].strip())
        except: pass;
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
        # if 'linux' in sys.platform.lower():
        #     os.system('chmod {0} "{1}"'.format(config.pyscrape.file_permissions, f))

    def downloadImages(self, movie, rights='777'):
        def tryToDownload(src, dst):
	    if os.path.exists(dst):
		return
            tryAgain = True
            count = 0
            while tryAgain:
                try:
                    urllib.urlretrieve(src, dst)
                    tryAgain = False
                except Exception, e:
                    logger.log(dst + " could not be downloaded", LogLevel.Error)
                    logger.log(e.message, 'ERROR')
                    if count < 10:
                        logger.log('Wait 10 Seconds and try it again', LogLevel.Error)
                        time.sleep(10)
                    else:
                        tryAgain = False
                finally:
                    count += 1

        def download(src, dst):
            start = time.time()
            tryToDownload(src, dst)
            elapsed = time.time() - start
            kbps = '[%.2f kbps]' % ((os.path.getsize(dst) / 1024) / elapsed)
            elapsed = '[%.2f s]' % elapsed
            msg = src + ' {0} {1}'.format(kbps, elapsed)
            logger.log('Downloaded: ' + msg, LogLevel.Debug)
            # self.chmod(config.pyscrape.file_permissions, dst)

        def downloadBackdrops():
            logger.log('Download Backdrops')
            path = movie.path
            movie.backdrops = self.tmdb.getBackdrops(movie.id)
            backdrops = sorted(movie.backdrops.iteritems(), key=operator.itemgetter(1), reverse=True)
            n = 0
            for backdrop in backdrops:
                if not config.pyscrape.backdrop_limit <= 0 and n > (config.pyscrape.backdrop_limit - 1):
                    return

                if n == 1:
                    path = os.path.join(path, 'extrafanart')
                    if not os.path.exists(path):
                        os.makedirs(path)
                    # self.chmod(config.pyscrape.folder_permissions, path)

                url = backdrop[0]
                if n == 0:
                    dst = '{0}/fanart.jpg'.format(path)
                else:
                    dst = '{0}/{1}'.format(path, os.path.basename(backdrop[0]))

                download(url, dst)
                n += 1

        def downloadPosters():
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
                dst = '{0}/poster{1}.jpg'.format(path, number)
                download(url, dst)
                n += 1

        def downloadFanart():
            def getFanart(category):
                try:
                    return fanart[category]
                except:
                    return []

            def downloadLogo():
                logger.log('Download Logo', LogLevel.Debug)
                if len(getFanart('hdmovielogo')) > 0:
                    for fa in getFanart('hdmovielogo'):
                        if fa['lang'] == self.config.pyscrape.language:
                            dst = os.path.join(movie.path, 'logo.png')
                            download(fa['url'], dst)
                            return
                    for fa in getFanart('hdmovielogo'):
                        if fa['lang'] == self.config.pyscrape.fallback_language:
                            dst = os.path.join(movie.path, 'logo.png')
                            download(fa['url'], dst)
                            return
                elif len(getFanart('movielogo')) > 0:
                    for fa in getFanart('movielogo'):
                        if fa['lang'] == self.config.pyscrape.language:
                            dst = os.path.join(movie.path, 'logo.png')
                            download(fa['url'], dst)
                            return
                    for fa in getFanart('movielogo'):
                        if fa['lang'] == self.config.pyscrape.fallback_language:
                            dst = os.path.join(movie.path, 'logo.png')
                            download(fa['url'], dst)
                            return

            def downloadBanner():
                logger.log('Download Banner', LogLevel.Debug)
                if len(getFanart('moviebanner')) > 0:
                    banner = {}
                    for b in getFanart('moviebanner'):
                        if b['lang'] == 'de':
                            banner[b['url']] = b['likes']
                    if len(banner) > 0:
                        banner = sorted(banner.iteritems(), key=operator.itemgetter(1), reverse=True)
                        dst = os.path.join(movie.path, 'banner.jpg')
                        for b in banner:
                            download(b[0], dst)
                            break                               # nur einen banner laden

            def downloadThumbs():
                logger.log('Download Thumbs', LogLevel.Debug)
                _thumbs = getFanart('moviethumb')
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
                                # self.chmod(config.pyscrape.folder_permissions, path)
                            name = 'thumb{0}.jpg'.format(str(int(n - 3)))

                        dst = os.path.join(path, name)
                        download(url, dst)

            def downloadDisc():
                logger.log('Download Disc Art', LogLevel.Debug)
                _discs = getFanart('moviedisc')
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
                        download(url, dst)
                        break

            def downloadClearart():
                logger.log('Download ClearArt', LogLevel.Debug)
                ca = getFanart('hdmovieclearart')
                clearart = {}

                if len(ca) == 0:
                    ca = getFanart('movieclearart')
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
                    download(art[0], dst)
                    break

            fanart = self.fanart.getAll(movie.imdbID)
            if fanart is None:
                return
            for f in fanart:     # JSON gibt mehrere einträge zurück, aber es gibt keine tmdb id 'doppelt' ??
                fanart = fanart[f]
                break            # falls es doch mehrere einträge gibt, nimm bitte das erste!

            logger.log('Download Fanart')
            downloadBanner()
            downloadLogo()
            downloadThumbs()
            downloadDisc()
            downloadClearart()

        downloadBackdrops()
        downloadPosters()
        downloadFanart()

    def cleanUp(self, movie):
        # alle Dateien ausser den Film löschen
        logger.log('Delete old files')
        for item in os.listdir(movie.path):
            item = os.path.join(movie.path, item)
            if item.endswith('.mkv') or item.endswith('.avi') or item.endswith('.idx') or item.endswith('.sub'):
                continue
            elif os.path.isfile(item):
                logger.log('Delete ' + item, LogLevel.Debug)
                os.remove(item)
            elif os.path.isdir(item):
                deletable = True
                for d in os.listdir(item):     # Prüfe ob der Ordner keine .mkv datei enthält
                    if d.endswith('.mkv') or d.endswith('.avi'):
                        deletable = False
                if deletable:
                    shutil.rmtree(item)

    def chmod(self, permissions, target):
        if 'linux' in sys.platform.lower():
            os.system('chmod {0} "{1}"'.format(permissions, target))
            #os.fchmod(dst, 777)
        elif 'win' in sys.platform.lower():
            pass

    def pyCharmBugFix(self):
        pass


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "c:l:p:m:r", ["config=", "log=", "path", "movie", "refresh"])
    except getopt.GetoptError:
        logger.log('Wrong arguments', LogLevel.Error)
        print '-c --config           path of config'
        print '-l --log              path of log'
        print '-p --path             paths (seperated by "::")'
        print '-m --movie            Scrape a single folder (e.g. postproc couchpotato)'
        print '-r --refresh          Do not delete existing files'
        sys.exit(2)


    single_path = ''
    refresh= False
    if not len(args) > 0:
        for opt, arg in opts:
            if opt in ("-c", "--config"):
                pass
            elif opt in ("-l", "--log"):
                pass
            elif opt in ("-p", "--path"):
                path = arg
                try:
                    path =unicode(arg).encode('utf-8')
                except:
                    pass
                single_path = path
            elif opt in ("-m", "--movie"):
                pass
            elif opt in ("-r", "--refresh"):
                refresh = True


    # scrape movies
    if os.path.isdir(single_path):
        single_path = utils.renameDirectory(single_path, logger)
        utils.renameFiles(single_path, logger)
        MovieScraper(single_path, single=True, refresh=refresh)
    # else:
    #     for path in config.movie.paths:
    #         if not os.path.exists(path):
    #             logger.log('Path "{0} does not exist - SKIP"'.format(path), LogLevel.Warning)
    #             continue
    #         logger.log('Start renaming subdirectories for root: ' + path)
    #         utils.renameSubfolder(path, logger)
    #         for p in os.listdir(path.decode('utf8')):
    #             utils.renameFiles(os.path.join(path, p), logger)
    #
    #         logger.log('Start scraping for Path: ' + path)
    #         MovieScraper(path)


def updateXbmc():
    return
    import time
    # clean db
    url = 'http://xbmc:xbmc@192.168.178.50:8080/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Clean"}'
    urllib.urlretrieve(url)
    time.sleep(120)

    # update db
    url = 'http://xbmc:xbmc@192.168.178.50:8080/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Scan"}'
    urllib.urlretrieve(url)


try:
    import time
    main(sys.argv[1:])
    updateXbmc()
except Exception, e:
    logger.log('SCHEISSE WAS HIER LOS MAN', LogLevel.Error)
    for a in sys.argv:
        logger.log(a, LogLevel.Error)
    try:
        logger.log(traceback.format_exc(), LogLevel.Error)
    except:
        pass
