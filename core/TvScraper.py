import getopt
import os
import sys
import time

from TvdbApi import get_show_nfo
from core.helpers import RegEx
from core.helpers.Config import Config
from core.helpers.Logger import log, LogLevel, whiteline
from TvdbApi import TvdbApi
from core.helpers.Exception import ShowNotFoundException
from core.helpers.utils import get_all_extensions
from core.helpers.utils import get_movie_extensions
from core.media import Codec


delete_existing = False
single_show = False
single_episode = False
single_season = False
config = Config()


def scrape_shows(shows):
    for show in shows:
        log(show['path'])
        log('====================================')

        # delete old files
        if delete_existing:
            _delete_existing_files(show['path'])

        try:
            get_show_info(show)
        except ShowNotFoundException:
            log('Show not found ... SKIP', LogLevel.Warning)
            whiteline()
            continue

        log('Get info for seasons')
        for season in [p for p in os.listdir(show['path']) if os.path.isdir(os.path.join(show['path'], p))]:
            _get_episode_info(show, season)
        whiteline()


def get_show_info(show):
    log('Get show info')
    tvdb = TvdbApi(show)
    show_xml = get_show_nfo(tvdb.show)
    show_nfo = os.path.join(show['path'], 'tvshow.nfo')
    open(show_nfo, 'w+').write(show_xml)
    log('Start downloading Images')
    tvdb.download_images()


def scrape_episode(episode_file):
    episode_path, episode_title = os.path.split(episode_file)
    tvdb = _find_show(episode_path)

    if delete_existing:
        root = os.path.splitext(episode_title)[0]
        for _file in [f for f in os.listdir(episode_path) if
                      root in f and os.path.splitext(f)[1] not in get_movie_extensions() and os.path.isfile(f)]:
            _file = os.path.join(episode_path, _file)
            log('Remove ' + _file, LogLevel.Debug)
            os.remove(_file)

    # remove audio tracks
    if config.codec.keep_tracks:
        log('Delete Audio Tracks')
        from Movie import Movie

        item = Movie()
        item.file = episode_title
        item.path = episode_path
        Codec.delete_audio_tracks([os.path.join(item.path, item.file)])

    # create nfo
    log('Get Info for episode ' + episode_title)
    nfo = tvdb.get_episode_nfo(episodes=RegEx.get_episode(episode_title), path=episode_path)
    root, ext = os.path.splitext(episode_title)
    nfo_filename = os.path.join(episode_path, root + '.nfo')
    log('Save NFO file', LogLevel.Debug)
    open(nfo_filename, 'w').write(nfo.encode("utf8"))

    # extract image from file
    video_source = os.path.join(episode_path, episode_title)
    output = os.path.join(episode_path, root + '.tbn')
    cmd = '"{0}" -ss {1} -i "{2}" -f image2 -vframes 1 "{3}"'.format(config.codec.ffmpeg,
                                                                     config.codec.screenshot_time,
                                                                     video_source, output)
    log('Extract image from file', LogLevel.Debug)
    os.system(cmd)


def scrape_season(season_path):
    for episode in [e for e in os.listdir(season_path) if os.path.splitext(e)[1] in get_movie_extensions()]:
        scrape_episode(episode_file=os.path.join(season_path, episode))


def _find_show(show_path):
    tvdb = []
    while not tvdb:
        try:
            show_path, title = os.path.split(show_path)
            show = {'title': title, 'path': show_path}
            if show_path == '':
                log('No Show found', LogLevel.Error)
                sys.exit()
            tvdb = TvdbApi(show)
        except ShowNotFoundException:
            continue
    return tvdb


def _get_episode_info(show, season):
    log('Get info for season ' + season)
    season_path = os.path.join(show['path'], season)
    from core.helpers.utils import get_movie_extensions

    episodes = [e for e in os.listdir(season_path) if
                os.path.isfile(os.path.join(season_path, e)) and RegEx.get_episode(e)
                and os.path.splitext(e)[1] in get_movie_extensions()]

    if len(episodes) == 0:
        log('No episodes found for ' + season, LogLevel.Warning)

    for episode_file in episodes:
        episode_file = os.path.join(show['path'], season, episode_file)
        scrape_episode(episode_file=episode_file)


def _delete_existing_files(root):
    fileset = set()
    for dir_, _, files in os.walk(root):
        for filename in files:
            relative_dir = os.path.relpath(dir_, root)
            relative_file = os.path.join(relative_dir, filename)
            fileset.add(os.path.join(root, relative_file))
    for _file in [f for f in fileset if os.path.splitext(f)[1] not in get_all_extensions()]:
        log('Delete ' + _file, LogLevel.Debug)
        os.remove(_file)


def _get_parameter(arguments):
    try:
        opts, args = getopt.getopt(arguments, "d:p:e:s:", ["delete-existing", "path=", "episode=", "season="])
    except getopt.GetoptError:
        log('Wrong arguments', LogLevel.Error)
        print '--d --delete-existing  Delete all files except for these with a extension from the extension list\n' \
              '--p --path Scrapes a single show\n' \
              '--e --episode Scrapes a single episode\n' \
              '--s --season Scrapes a single season\n'

        sys.exit(2)

    global delete_existing, single_show, single_episode, single_season

    for opt, arg in opts:
        if opt in ("-d", "--delete-existing"):
            delete_existing = True
        elif opt in ("-e", "--episode"):
            try:
                single_episode = unicode(arg).encode('utf-8')
            except UnicodeDecodeError:
                single_episode = arg
        elif opt in ("-s", "--season"):
            try:
                single_season = unicode(arg).encode('utf-8')
            except UnicodeDecodeError:
                single_season = arg
        elif opt in ("-p", "--path"):
            try:
                single_show = unicode(arg).encode('utf-8')
            except UnicodeDecodeError:
                single_show = arg


if __name__ == '__main__':
    def _start():
        try:
            shows = []

            if single_episode != '':
                if not os.path.isfile(single_episode):
                    log(single_episode + ' is not a file', LogLevel.Error)
                    sys.exit()

                episode = RegEx.get_episode(single_episode)
                path, filename = os.path.split(single_episode)
                filename, extension = os.path.splitext(filename)

                if not episode or extension not in get_movie_extensions():
                    log(single_episode + ' is not a valid episode file', LogLevel.Error)
                    sys.exit()

                scrape_episode(single_episode)
            elif single_season != '':
                if not os.path.isdir(single_season):
                    log(single_season + ' is not a directory', LogLevel.Error)
                    sys.exit()
                else:
                    scrape_season(season_path=single_season)
            elif single_show != '':
                if os.path.exists(single_show) and os.path.isdir(single_show):
                    title = os.path.basename(os.path.normpath(single_show))
                    show = {'title': title, 'path': single_show}
                    shows.append(show)
                    scrape_shows(shows)
                else:
                    log('Path do not exists', LogLevel.Warning)
            else:
                for path in config.show.paths:
                    if not os.path.exists(path):
                        log(path + ' do not exists - SKIP', LogLevel.Warning)
                        continue

                    for show in [p for p in os.listdir(path) if os.path.isdir(os.path.join(path, p))]:
                        _show = {'title': show, 'path': os.path.join(path, show)}
                        shows.append(_show)

                    scrape_shows(shows)
        except KeyboardInterrupt:
            log("TvScraper was interrupted by user", LogLevel.Warning)

    def _initialize():
        global delete_existing, single_season, single_episode, single_show
        delete_existing = False
        single_show = ''
        single_episode = ''
        single_season = ''
        _get_parameter(sys.argv[1:])

    start = time.time()

    _initialize()
    _start()

    end = time.time()
    elapsed = end - start
    log("%.2f s total" % elapsed, 'TIME')
    whiteline()