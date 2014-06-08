import os
from lxml import etree
from threading import Thread

from memory_profiler import profile

from core.helpers import logger
from core.helpers.config import config
from core.helpers import regex
from core.helpers import utils
from core.helpers.logger import log, LogLevel
from core.helpers.utils import get_movie_extensions, get_all_extensions, download
from core.helpers.utils import readable_int
from core.media.codec import get_ainfo, get_vinfo, get_runtime
from core.media.codec import delete_audio_tracks


#region Private Methods


def _clean_dir(path):
    for f in [os.path.join(path, f) for f in os.listdir(path)
              if os.path.isfile(os.path.join(path, f)) and os.path.splitext(f)[1].lower() not in get_all_extensions()]:
        log('Remove ' + f, LogLevel.Debug)
        os.remove(f)

    for sub in [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]:
        _clean_dir(sub)
        if not [f for f in os.listdir(sub) if os.path.isfile(os.path.join(sub, f))]:
            os.rmdir(sub)


def _get_commandline_options():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="print status messages to stdout")
    parser.add_option("-q", "--quiet",
                      action="store_true", dest="quiet", default=False,
                      help="don't print status messages to stdout")
    parser.add_option("-p", "--path",
                      dest="path", default='',
                      help="specify the path to a movie")
    return parser.parse_args()


def _get_movie_info(movie_path):
    log('Load plugins..', LogLevel.Debug)
    import core.plugins.movieapi as api

    r = regex.get_movie(movie_path)
    # todo: skip when regex is not valid
    tmdb_id = api.get_tmdb_id(title=r['title'], year=r['year'], imdb_id=r['imdbID'])
    imdb_id = api.get_imdb_id(title=r['title'], year=r['year'], tmdb_id=tmdb_id)
    info = api.get_all(imdb_id=imdb_id, tmdb_id=tmdb_id)
    if info is None:
        return None

    info['path'] = movie_path
    info['files'] = [p for p in os.listdir(movie_path)
                     if os.path.splitext(p)[1].lower() in get_movie_extensions()]
    return info


def _get_title(movie_info):
    title = ''
    if 'title' in movie_info and movie_info['title'] is not None and movie_info['title'] != '':
        title = movie_info['title']
    elif 'original_title' in movie_info and movie_info['original_title'] is not None \
            and movie_info['original_title'] != '':
        title = movie_info['original_title']

    title = utils.replace(title)
    return title


def _initialize(movie_info):
    _clean_dir(movie_info['path'])
    # todo: merge cd's
    # todo: implement config settings for renaming (shall be renamed? rename template)
    _remove_audio_tracks(movie_info)
    movie_info['path'] = _rename_movie_path(movie_info)
    movie_info['files'] = _rename_movie_file(movie_info)
    return movie_info


def _movie_is_valid(movie_path):
    if not os.path.isdir(movie_path):
        return False
    if not [p for p in os.listdir(movie_path) if os.path.splitext(p)[1].lower() in get_movie_extensions()]:
        # todo: if no movie is found by extension: use ffmpeg/mediainfo to find video files instead extensions?
        return False

    r = regex.get_movie(movie_path)
    if r['title'] == '' and r['imdbID'] == '':
        return False

    return True


def _process_commandline_options(options, args):
    logger.quiet = options.quiet
    config.pyscrape.debug_log = options.verbose


def _remove_audio_tracks(movie_info):
    # todo: check if removing if audio tracks is configured, pass languages as parameter etc.
    # todo: rewrite codec module
    video_files = [os.path.join(movie_info['path'], f) for f in movie_info['files']]
    delete_audio_tracks(video_files)


def _rename_movie_file(movie_info):
    if len(movie_info['files']) == 1:
        title = _get_title(movie_info)
        title = utils.replace(title)

        if title == '':
            return movie_info['files']

        ext = os.path.splitext(movie_info['files'][0])[1]
        new_file = title + ext
        src = os.path.join(movie_info['path'], movie_info['files'][0])
        dst = os.path.join(movie_info['path'], new_file)
        os.rename(src, dst)
        return [new_file]


def _rename_movie_path(movie_info):
    if os.path.isdir(movie_info['path']) and os.path.exists(movie_info['path']):
        title = _get_title(movie_info)
        if movie_info['release'] != '':
            title += ' (' + movie_info['release'][:4] + ')'
        if movie_info['imdb_id'] != '':
            title += ' (' + movie_info['imdb_id'] + ')'
        path = os.path.dirname(movie_info['path'])
        path = os.path.join(path, title)
        os.rename(movie_info['path'], path)
        movie_info['path'] = path
    return movie_info['path']


#endregion


def create_nfo(movie):
    log('Create NFO')
    root = etree.Element('movie')

    child = etree.Element('title')
    child.text = movie['title']
    root.append(child)

    child = etree.Element('originaltitle')
    child.text = movie['original_title']
    root.append(child)

    child = etree.Element('sorttitle')
    child.text = movie['title']
    root.append(child)

    if movie['collection'] is not None and movie['collection'] != '':
        child = etree.Element('set')
        child.text = movie['collection']
        root.append(child)

    child = etree.Element('rating')
    child.text = str(movie['rating'])
    root.append(child)

    child = etree.Element('votes')
    child.text = str(movie['vote_count'])
    root.append(child)

    child = etree.Element('year')
    child.text = movie['release'][:4]
    root.append(child)

    # todo: Implement IMDB Top250

    if movie['outline'] is not None and movie['outline'] != '':
        child = etree.Element('outline')
        child.text = movie['outline']
        root.append(child)

    if movie['tagline'] is not None and movie['tagline'] != '':
        child = etree.Element('tagline')
        child.text = movie['tagline']
        root.append(child)

    child = etree.Element('plot')
    child.text = movie['plot']
    root.append(child)

    if movie['mpaa'] is not None and movie['mpaa'] != 'unknown':
        child = etree.Element('mpaa')
        child.text = movie['mpaa']
        root.append(child)

    if movie['revenue'] is not None and movie['revenue'] != '' and movie['revenue'] != 0:
        child = etree.Element('revenue')
        child.text = readable_int(movie['revenue'])
        root.append(child)

    if movie['budget'] is not None and movie['budget'] != '' and movie['budget'] != 0:
        child = etree.Element('budget')
        child.text = readable_int(movie['budget'])
        root.append(child)

    if len(movie['posters']) > 0:
        if 'url' in movie['posters'][0]:
            child = etree.Element('thumb')
            child.text = movie['posters'][0]['url']
            root.append(child)

    child = etree.Element('id')
    child.text = movie['imdb_id']
    root.append(child)

    # todo: implement movie trailers!
    # if movie.trailer is not None and movie.trailer != '':
    #     child = etree.Element('trailer')
    #     child.text = 'plugin://plugin.video.youtube/?action=play_video&amp;videoid={0}'.format(movie.trailer)
    #     root.append(child)

    for genre in movie['genres']:
        child = etree.Element('genre')
        child.text = genre
        root.append(child)

    if len(movie['production_companies']) > 0:
        child = etree.Element('studio')
        child.text = movie['production_companies'][0].strip()
        root.append(child)

    movie_credits = movie['credits']
    for credit in movie_credits['credits']:
        child = etree.Element('credits')
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

    if len(movie['files']) > 0:
        videos = [os.path.join(movie['path'], v) for v in movie['files']]
        vinfo = get_vinfo(videos[0])
        ainfo = get_ainfo(videos[0])

        fileinfo = etree.Element('fileinfo')
        streamdetails = etree.SubElement(fileinfo, 'streamdetails')

        video = etree.SubElement(streamdetails, 'video')
        aspect = etree.SubElement(video, 'aspect')
        video_codec = etree.SubElement(video, 'codec')
        duration = etree.SubElement(video, 'durationinseconds')
        width = etree.SubElement(video, 'width')
        height = etree.SubElement(video, 'height')

        aspect.text = str(vinfo['aspect'])
        video_codec.text = vinfo['codec']
        duration.text = str(int(get_runtime(videos)) * 60)
        width.text = str(vinfo['width'])
        height.text = str(vinfo['height'])

        child = etree.Element('runtime')
        child.text = duration.text
        root.append(child)

        if vinfo['scantype'] != '':
            scantype = etree.SubElement(video, 'scantype')
            scantype.text = vinfo['scantype']

        for info in ainfo:
            audio = etree.SubElement(streamdetails, 'audio')
            channels = etree.SubElement(audio, 'channels')
            audio_codec = etree.SubElement(audio, 'codec')

            channels.text = info['channel_count']
            audio_codec.text = info['format']

            if info['language'] != '':
                language = etree.SubElement(audio, 'language')
                language.text = info['language']

        root.append(fileinfo)

    log('Write NFO to disk', LogLevel.Debug)
    filename = movie['title']
    if filename is None or filename == '':
        filename = os.path.basename(movie['path'])
    nfo_file = os.path.join(movie['path'], filename + '.nfo')
    file(nfo_file, 'w').write(etree.tostring(root, pretty_print=True, encoding='utf8', xml_declaration=True))


def download_images(movie_info):
    def download_image(src, dst):
        log('Add ' + src + ' to queue', LogLevel.Debug)
        Thread(target=download, args=(src, dst)).start()

    def download_backdrops():
        if not movie_info['backdrops']:
            return
        log('Download Backdrops', LogLevel.Debug)
        n = 0
        for backdrop in movie_info['backdrops']:
            if not config.pyscrape.backdrop_limit <= 0 and n > (config.pyscrape.backdrop_limit - 1):
                return
            if n == 1:
                if not config.movie.download_extrafanart:
                    return

                path = os.path.join(movie_info['path'], 'extrafanart')
                if not os.path.exists(os.path.join(movie_info['path'], 'extrafanart')):
                    os.makedirs(path)

            if n == 0:
                dst = os.path.join(movie_info['path'], 'fanart.jpg')
            else:
                dst = os.path.join(movie_info['path'], 'extrafanart', os.path.basename(backdrop['url']))

            #todo: implement: , refresh=_refresh)
            download_image(src=backdrop['url'], dst=dst)
            n += 1

    def download_posters():
        if not movie_info['posters']:
            return
        log('Download posters', LogLevel.Debug)
        n = 0
        for poster in movie_info['posters']:
            if not config.pyscrape.poster_limit <= 0 and n > (config.pyscrape.poster_limit - 1):
                return

            if n > 0:
                number = n
            else:
                number = ''
            dst = os.path.join(movie_info['path'], 'poster{0}.jpg'.format(number))
            #todo: implement: , refresh=_refresh)
            download_image(src=poster['url'], dst=dst)
            n += 1

    def download_logo():
        if not movie_info['logos']:
            return
        log('Download Logo', LogLevel.Debug)
        for logo in [l for l in movie_info['logos'] if 'url' in l and l['url'] != '']:
            #todo: implement: , refresh=_refresh)
            download_image(src=logo['url'], dst=os.path.join(movie_info['path'], 'logo.png'))
            break

    def download_banner():
        if not movie_info['banners']:
            return
        log('Download Banner', LogLevel.Debug)
        for banner in [b for b in movie_info['banners'] if 'url' in b and b['url'] != '']:
            #todo: implement: , refresh=_refresh)
            download_image(src=banner['url'], dst=os.path.join(movie_info['path'], 'banner.jpg'))
            break

    def download_thumbs():
        if not movie_info['landscapes']:
            return
        log('Download Thumbs', LogLevel.Debug)
        thumbs = movie_info['landscapes']
        for n in range(0, len(thumbs)):
            url = thumbs[n]['url']
            if n == 0 and config.movie.download_landscape:
                download_image(src=url, dst=os.path.join(movie_info['path'], 'landscape.jpg'))
            elif 0 < n <= 4 and config.movie.download_thumbs:
                download_image(src=url, dst=os.path.join(movie_info['path'], 'thumb{0}.jpg'.format(n)))
            elif n > 4 and config.movie.download_extrathumbs:
                path = os.path.join(movie_info['path'], 'extrathumbs')
                if not os.path.exists(path):
                    os.makedirs(path)
                download_image(src=url, dst=os.path.join(path, 'thumb{0}.jpg'.format(str(int(n - 4)))))
                del url, path

    def download_disc():
        if not movie_info['disc_art']:
            return
        log('Download DiscArt', LogLevel.Debug)
        for disc in movie_info['disc_art']:
            # todo: implement refresh
            download_image(src=disc['url'], dst=os.path.join(movie_info['path'], 'disc.png'))
            break

    def download_clearart():
        if not movie_info['clearart']:
            return
        log('Download ClearArt', LogLevel.Debug)
        for clearart in movie_info['clearart']:
            download_image(src=clearart['url'], dst=os.path.join(movie_info['path'], 'clearart.png'))
            break

    log('Download images')
    if config.movie.download_backdrop:
        download_backdrops()
    if config.movie.download_poster:
        download_posters()
    if config.movie.download_logo:
        download_logo()
    if config.movie.download_banner:
        download_banner()
    if config.movie.download_thumbs:
        download_thumbs()
    if config.movie.download_disc:
        download_disc()
    if config.movie.download_clearart:
        download_clearart()


def scan(path):
    log('Scan ' + path)
    log('====================================')
    # ================ Initialization =================
    if not _movie_is_valid(path):
        log('Can not find a valid video or folder structure', LogLevel.Warning)
        return

    log('Get all available information')
    info = _get_movie_info(path)

    if info is None:
        log('Can not find a movie for: ' + path, LogLevel.Warning)
        return

    log('Initialize environment')
    info = _initialize(info)
    # =================================================

    # todo: create nfowriter (nfowriter uses a template to create a NFO structure)
    create_nfo(info)
    download_images(info)


if __name__ == '__main__':
    _options, _args = _get_commandline_options()
    _process_commandline_options(_options, _args)
    # todo: scan paths by config when options.path is not specified
    scan(_options.path)
