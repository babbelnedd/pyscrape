import shutil
import cStringIO
import subprocess
import os
import ConfigParser

from core.helpers.config import config
from core.helpers.logger import log, LogLevel




# region private methods


def _get_codec_info(video, extra_attribute=''):
    parameter = ' {0} "{1}"'.format(extra_attribute, video)

    cmd = config.codec.mediainfo_path + parameter
    output = os.popen(cmd).read().splitlines()
    codec = ConfigParser.ConfigParser()

    new_output = ''
    for n in range(0, len(output)):
        line = output[n]
        if not ':' in line and line != '\n' and not '[' in line and not ']' in line and line != '':
            new_output += '[' + line.strip() + ']\n'
        else:
            new_output += line.strip() + '\n'

    codec.readfp(cStringIO.StringIO(new_output))
    return codec


def _get(video, section, key, codec=None):
    # todo: use codec.hassection, codec.hasoption instead try/catch
    if codec is None:
        codec = _get_codec_info(video)

    try:
        result = codec.get(section, key)
        log('Key "{0}" found in "{1}", value: {2}'.format(key, section, result), LogLevel.Debug)
        return result
    except ConfigParser.NoOptionError:
        log('Key "{0}" not found in "{1}"'.format(key, section), LogLevel.Debug)
        return ''
    except ConfigParser.NoSectionError:
        log('Section "{0}" not found'.format(section), LogLevel.Debug)
        return ''
    except AttributeError:
        return ''


def _get_audio_formats(video):
    codecs = []

    for section in _get_codec_info(video).sections():
        if not 'Audio' in section:
            continue

        codec = _get(video, section, 'Codec ID/Hint')
        if codec == '':
            codec = _get(video, section, 'Format')

        if 'AC-3' in codec:
            codec = 'AC3'
        elif 'mp3' in codec.lower():
            codec = 'mp3'

        codecs.append(codec)

    return codecs


def _get_audio_channels(video):
    channels = []

    for section in _get_codec_info(video).sections():
        if not 'Audio' in section:
            continue

        channel_count = _get(video, section, 'Channel count').replace('channels', '').replace(' ', '')
        if channel_count == '':
            channel_count = _get(video, section, 'Channel(s)').replace('channels', '').replace(' ', '')

        channels.append(channel_count)

    return channels


def _get_audio_languages(video):
    languages = []

    for section in _get_codec_info(video).sections():
        if not 'Audio' in section:
            continue

        language = _get(video, section, 'Language')
        languages.append(language)

    return languages


#endregion


def get_ainfo(video):
    codecs = []
    formats = _get_audio_formats(video)
    channels = _get_audio_channels(video)
    languages = _get_audio_languages(video)

    for n in range(0, len(formats)):
        codec = {'format': formats[n], 'channel_count': channels[n], 'language': languages[n]}
        codecs.append(codec)

    return codecs


def get_vinfo(video):
    vinfo = {'width': _get(video, 'Video', 'Width').replace('pixels', '').replace(' ', ''),
             'height': _get(video, 'Video', 'Height').replace('pixels', '').replace(' ', ''),
             'fps': _get(video, 'Video', 'Frame rate').lower().replace('fps', '').strip(),
             'bitrate': _get(video, 'Video', 'Bit rate'),
             'scantype': _get(video, 'Video', 'Scan type'),
             'aspect': _get(video, 'Video', 'Display aspect ratio'),
             'codec': _get(video, 'Video', 'Codec ID/Hint')}

    if vinfo['codec'] == '':
        codec = _get_codec_info(video, '--fullscan')
        vinfo['codec'] = _get(video, 'Video', 'Internet media type', codec)

    if 'x264' in vinfo['codec'].lower():
        vinfo['codec'] = 'h264'
    elif 'h264' in vinfo['codec'].lower():
        vinfo['codec'] = 'h264'
    elif 'xvid' in vinfo['codec'].lower():
        vinfo['codec'] = 'xvid'
    elif 'divx' in vinfo['codec'].lower():
        vinfo['codec'] = 'DivX'
    # what other codes are there and how to name it for xbmc?

    if ':' in vinfo['aspect']:
        aspect = vinfo['aspect'].split(':')
        vinfo['aspect'] = round(float(aspect[0]) / float(aspect[1]), 2)
    else:
        vinfo['aspect'] = None

    return vinfo


def get_runtime(videos):
    if isinstance(videos, str):
        videos = [videos]
    if not isinstance(videos, list):
        raise Exception('Videos have to be a list')

    _duration = 0

    for video in videos:
        duration = _get(video, 'Video', 'Duration')
        if not duration:
            # happens, when movie container is corrupt
            return '0'

        import re

        d = {'h': 0, 'm': 0, 's': 0, 'ms': 0}
        hours = re.search('[0-9]{1,2}h(?![^ ])', duration)
        minutes = re.search('[0-9]{1,3}m(?![^ ])', duration)
        seconds = re.search('[0-9]{1,2}s(?![^ ])', duration)
        ms = re.search('[0-9]{1,3}ms(?![^ ])', duration)
        del re

        if hours: d['h'] = int(hours.group().replace('h', '')) * 60 * 60 * 1000
        if minutes: d['m'] = int(minutes.group().replace('m', '')) * 60 * 1000
        if seconds: d['s'] = int(seconds.group().replace('s', '')) * 1000
        if ms: d['ms'] = int(ms.group().replace('ms', ''))

        _duration += float(d['h'] + d['m'] + d['s'] + d['ms']) / 1000

    return str(_duration)


def delete_audio_tracks(videos):
    if not config.codec.keep_tracks:
        return

    if config.codec.mkvmerge == '':
        log('mkvmerge is not set / installed', LogLevel.Warning)
        return

    for video in videos:
        if not os.path.exists(video) or not os.path.isfile(video):
            continue

        log('Look for removable Audio-Tracks')
        keep_tracks = config.codec.keep_tracks
        audio_tracks = {}

        # get all audio codecs
        codec = _get_codec_info(video)
        for section in codec.sections():
            if not 'Audio' in section:
                continue

            try:
                language = codec.get(section, 'Language').lower()
                track_id = int(codec.get(section, 'ID')) - 1
            except ConfigParser.NoOptionError:
                continue
            audio_tracks[track_id] = language

        deletable_tracks = []
        keep_tracks_count = 0
        if len(audio_tracks) < 2:  # If there is only one audio-track do not try do delete any tracks
            return

        for track in audio_tracks:
            _language = audio_tracks[track]
            if _language == '':
                continue
            if _language in keep_tracks:
                keep_tracks_count += 1
            else:
                deletable_tracks.append(track)

        # check if we have to delete audio tracks
        if len(deletable_tracks) > 0 and keep_tracks_count > 0:
            delete_audiotracks = ' --audio-tracks !'

            for n in range(0, len(deletable_tracks)):
                if n > 0:
                    delete_audiotracks += ','
                delete_audiotracks += str(deletable_tracks[n])

            dst = os.path.join(os.path.dirname(video), 'new.mkv')

            cmd = '{0} -o "{1}"{2} "{3}"'.format(config.codec.mkvmerge, dst, delete_audiotracks, video)

            log("Remove {0} audio-tracks".format(keep_tracks_count))
            log('\a === DO NOT STOP THE PROCESS ===', LogLevel.Warning)
            log('Execute mkvmerge: ' + cmd, LogLevel.Debug)
            open(dst, 'a').close()
            try:
                subprocess.check_call(cmd, shell=True)
            except subprocess.CalledProcessError:
                log('Not able to merge MKV: ' + video, LogLevel.Error)
                return

            # check if new file is valid
            cmd = 'mediainfo "--Inform=General;%FileName%,%Duration/String3%,%FileSize%" "' + video + '"'
            output = os.popen(cmd).read()
            path, filename = os.path.split(video)
            name, ext = os.path.splitext(filename)
            output = output.replace(name, '')
            old_runtime = output.replace(',', '', 1).split(':')
            old_runtime = old_runtime[0] + ':' + old_runtime[1]

            cmd = 'mediainfo "--Inform=General;%FileName%,%Duration/String3%,%FileSize%" "' + dst + '"'
            output = os.popen(cmd).read()
            path, filename = os.path.split(dst)
            name, ext = os.path.splitext(filename)
            output = output.replace(name, '')
            new_runtime = output.replace(',', '', 1).split(':')
            new_runtime = new_runtime[0] + ':' + new_runtime[1]

            if old_runtime != new_runtime:
                log('File merging goes wrong', LogLevel.Error)
                os.remove(dst)
                return

            old_filesize = os.path.getsize(video)
            new_filesize = os.path.getsize(dst)
            percent = 100 - (new_filesize / (old_filesize / 100))
            mb = (old_filesize - new_filesize) / 1024 / 1024
            log('{0}% ({1} mb)saved'.format(percent, mb))
            log('REPLACE {0}'.format(video), LogLevel.Debug)
            os.remove(video)
            try:
                os.rename(dst, video)
            except OSError:
                shutil.move(dst, video)


def get_audio_xml(videos):
    def audio_xml():
        if len(videos) < 1:
            return ''

        xml = '\n'
        for codec in get_ainfo(videos[0]):
            xml += '            <audio>\n'
            xml += '                <channels>{0}</channels>\n'.format(codec['channel_count'])
            xml += '                <codec>{0}</codec>\n'.format(codec['format'])
            if codec['language'] != '':
                xml += u'                <language>{0}</language>\n'.format(codec['language'])
            xml += '            </audio>\n'
        return xml

    log('Load Audio Codec Information')
    return audio_xml()


def get_video_xml(videos):
    def video_xml():
        if len(videos) < 1:
            return ''

        vinfo = get_vinfo(videos[0])

        xml = '             <video>\n'
        if vinfo['aspect']:
            xml += '                <aspect>{0}</aspect>\n'.format(vinfo['aspect'])

        xml += '                <codec>{0}</codec>\n'.format(vinfo['codec'])
        dur = str(int(float(get_runtime(videos)) * 60))
        xml += '                <durationinseconds>{0}</durationinseconds>\n'.format(dur)
        xml += '                <width>{0}</width>\n'.format(vinfo['width'])
        xml += '                <height>{0}</height>\n'.format(vinfo['height'])
        xml += u'                <scantype>{0}</scantype>\n'.format(vinfo['scantype'])
        xml += '            </video>'
        return xml

    log('Load Video Codec Information')
    return video_xml()