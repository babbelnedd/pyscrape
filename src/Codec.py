import shutil
import cStringIO
import subprocess
import os
import ConfigParser

from Logger import log, LogLevel
from Config import Config
from Decorator import Cached


config = Config()


@Cached
def _get_codec(video, extra_attribute=''):
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


@Cached
def _get(video, section, key, codec=None):
    # todo: use codec.hassection, codec.hasoption instead try/catch
    if codec is None:
        codec = _get_codec(video)

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


def get_runtime(videos):
    _duration = '0'

    for video in videos:
        duration = _get(video, 'Video', 'Duration')

        if 'h' in duration:
            duration = duration.lower().replace(' ', '').replace('mn', '').split('h')
        elif 'm' in duration and 'h' not in duration:
            duration = duration.replace(' ', '').lower().split('mn')

        if len(duration) == 2 and 's' not in duration[1]:
            h = int(duration[0]) * 60
            m = int(duration[1])
            duration = h + m
        elif len(duration) == 2 and 's' in duration[1]:
            duration = duration[0]
        elif len(duration) == 1:
            duration = duration[0].replace('s', '').strip()

        _duration = str(int(duration) + int(_duration))

    return _duration


def delete_audio_tracks(videos):
    # todo: verify functionality
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
        codec = _get_codec(video)
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
            except:
                shutil.move(dst, video)


def get_audio_xml(videos):
    def audio_xml():
        xml = ''
        for section in _get_codec(videos[0]).sections():
            if 'Audio' in section:
                audio = {'codec': _get(videos[0], section, 'Format')}
                if 'AC-3' in audio['codec']:
                    audio['codec'] = 'AC3'

                audio['channels'] = _get(videos[0], section, 'Channel count').replace('channels', '').replace(' ', '')
                if audio['channels'] == '':
                    audio['channels'] = _get(videos[0], section, 'Channel(s)').replace('channels', '').replace(' ', '')
                audio['language'] = _get(videos[0], section, 'Language')

                xml += '\n'
                xml += '            <audio>\n'
                xml += '                <channels>{0}</channels>\n'.format(audio['channels'])
                xml += '                <codec>{0}</codec>\n'.format(audio['codec'])
                if audio['language'] != '':
                    xml += u'                <language>{0}</language>\n'.format(audio['language'])
                xml += '            </audio>'
        xml += '\n'
        return xml

    log('Load Audio Codec Information')
    return audio_xml()


def get_video_xml(videos):
    def video_xml():
        video = {'width': _get(videos[0], 'Video', 'Width').replace('pixels', '').replace(' ', ''),
                 'height': _get(videos[0], 'Video', 'Height').replace('pixels', '').replace(' ', ''),
                 'bitrate': _get(videos[0], 'Video', 'Bit rate'), 'fps': _get(videos[0], 'Video', 'Frame rate'),
                 'aspect': _get(videos[0], 'Video', 'Display aspect ratio'),
                 'scantype': _get(videos[0], 'Video', 'Scan type'),
                 'codec': _get(videos[0], 'Video', 'Writing library')}

        if video['codec'] == '':
            codec = _get_codec(videos[0], '--fullscan')
            video['codec'] = _get(videos[0], 'Video', 'Internet media type', codec)

        if 'x264' in video['codec'].lower():
            video['codec'] = 'h264'
        elif 'h264' in video['codec'].lower():
            video['codec'] = 'h264'
        elif 'xvid' in video['codec'].lower():
            video['codec'] = 'xvid'
            # what other codes are there and how to name it for xbmc?

        aspect = None
        if ':' in video['aspect']:
            aspect = video['aspect'].split(':')
            aspect = round(float(aspect[0]) / float(aspect[1]), 2)

        xml = '             <video>\n'
        if aspect:
            xml += '                <aspect>{0}</aspect>\n'.format(aspect)

        xml += '                <codec>{0}</codec>\n'.format(video['codec'])
        xml += '                <durationinseconds>{0}</durationinseconds>\n'.format(int(get_runtime(videos)) * 60)
        xml += '                <width>{0}</width>\n'.format(video['width'])
        xml += '                <height>{0}</height>\n'.format(video['height'])
        xml += u'                <scantype>{0}</scantype>\n'.format(video['scantype'])
        xml += '            </video>'
        return xml

    log('Load Video Codec Information')
    return video_xml()


    #print get_video_xml(['/media/lsc/nas/filme/Thor (2011) (tt0800369)/Thor.mkv'])