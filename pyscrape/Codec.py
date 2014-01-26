# -*- coding: utf-8 -*-
import shutil
import subprocess
import os
import ConfigParser
import sys
from Logger import Logger, LogLevel
from Config import Config


class Codec(object):
    def __init__(self, movie):
        self.logger = Logger()
        self.config = Config()
        self.movie = movie

        filename, file_extension = os.path.splitext(movie.file)
        self.file = os.path.join(movie.path, filename + '.nfo.tmp')
        path = os.path.join(movie.path, movie.file)
        try:
            path = unicode(path).encode('utf8')
        except:
            pass

        self.path = path
        if movie.file == '' or not os.path.isfile(os.path.join(movie.path, movie.file)):
            self.logger.log('No movie file found - skip Codec information', LogLevel.Warning)
            return

        self.codec_config = ConfigParser.ConfigParser()
        open(self.file, 'a').close()
        self._run_mediainfo()

    def _run_mediainfo(self, extra_attribute=''):
        self.logger.log('Start mediainfo', 'DEBUG')
        parameter = ' {0} --logfile="{1}" "{2}"'.format(extra_attribute, self.file, self.path)

        if 'linux' in sys.platform.lower():
            parameter += '  >/dev/null'  # do not work - why? :/
        elif 'win32' in sys.platform.lower():
            parameter += ' > nul'
        cmd = self.config.codec.mediainfo_path + parameter
        os.system(cmd)

        # create section headers for ConfigParser
        newcontent = []
        with open(self.file) as f:
            content = f.readlines()
        for line in content:
            if not ':' in line and line != '\n' and not '[' in line and not ']' in line:
                line = '[' + line.strip() + ']\n'
            newcontent.append(line)

        os.remove(self.file)
        with open(self.file, 'a') as f:
            f.writelines(newcontent)
        self.codec_config.read(self.file)

    def _get(self, sec, attr):
        try:
            result = self.codec_config.get(sec, attr)
            self.logger.log('Key "{0}" found in "{1}", value: {2}'.format(attr, sec, result), LogLevel.Debug)
            return result
        except ConfigParser.NoOptionError:
            self.logger.log('Key "{0}" not found in "{1}"'.format(attr, sec), LogLevel.Debug)
            return ''

    def get_runtime(self):
        duration = self._get('Video', 'Duration').replace(' ', '').replace('mn', '').lower().split('h')
        if len(duration) == 2:
            h = int(duration[0]) * 60
            m = int(duration[1])
            return h + m
        elif len(duration) == 1:
            return duration[0].replace('s', '').strip()
        return 0

    def get_audio_xml(self):
        def audio_xml():
            xml = ''
            for section in self.codec_config.sections():
                if 'Audio' in section:
                    audio = {'codec': self._get(section, 'Format')}
                    if 'AC-3' in audio['codec']:
                        audio['codec'] = 'AC3'

                    audio['channels'] = self._get(section, 'Channel count').replace('channels', '').replace(' ', '')
                    if audio['channels'] == '':
                        audio['channels'] = self._get(section, 'Channel(s)').replace('channels', '').replace(' ', '')
                    audio['language'] = self._get(section, 'Language')

                    xml += '\n'
                    xml += '            <audio>\n'
                    xml += '                <channels>{0}</channels>\n'.format(audio['channels'])
                    xml += '                <codec>{0}</codec>\n'.format(audio['codec'])
                    xml += u'                <language>{0}</language>\n'.format(audio['language'])
                    xml += '            </audio>'
            xml += '\n'
            return xml

        self.logger.log('Load Audio Codec Information')
        if not os.path.exists(self.file):
            return ''
        return audio_xml()

    def get_video_xml(self):
        def video_xml():
            video = {}
            duration = self._get('Video', 'Duration').replace(' ', '').replace('mn', '').lower().split('h')
            if len(duration) == 2:
                h = int(duration[0]) * 60
                m = int(duration[1])
                video['duration'] = (h + m) * 60
            elif len(duration) == 1:
                video['duration'] = duration[0].replace('s', '').strip()
            else:
                video['duration'] = 0
            video['width'] = self._get('Video', 'Width').replace('pixels', '').replace(' ', '')
            video['height'] = self._get('Video', 'Height').replace('pixels', '').replace(' ', '')
            video['bitrate'] = self._get('Video', 'Bit rate')
            video['fps'] = self._get('Video', 'Frame rate')
            video['aspect'] = self._get('Video', 'Display aspect ratio')
            video['scantype'] = self._get('Video', 'Scan type')
            video['codec'] = self._get('Video', 'Writing library')

            if video['codec'] == '':
                self._run_mediainfo(extra_attribute='--fullscan')
                video['codec'] = self._get('Video', 'Internet media type')

            if 'x264' in video['codec'].lower():
                video['codec'] = 'h264'
            elif 'h264' in video['codec'].lower():
                video['codec'] = 'h264'
            elif 'xvid' in video['codec'].lower():
                video['codec'] = 'xvid'
                # what codes are there and how to name it for xbmc?

            xml = '             <video>\n'
            xml += '                <aspect>{0}</aspect>\n'.format(video['aspect'])
            xml += '                <codec>{0}</codec>\n'.format(video['codec'])
            xml += '                <durationinseconds>{0}</durationinseconds>\n'.format(video['duration'])
            xml += '                <width>{0}</width>\n'.format(video['width'])
            xml += '                <height>{0}</height>\n'.format(video['height'])
            xml += u'                <scantype>{0}</scantype>\n'.format(video['scantype'])
            xml += '            </video>'
            return xml

        self.logger.log('Load Video Codec Information')
        if not os.path.exists(self.file):
            return ''
        return video_xml()

    def delete_audio_tracks(self):
        if self.config.codec.mkvmerge == '':
            self.logger.log('mkvmerge is not set / installed', LogLevel.Warning)
            return
        if not self.movie.file.endswith('.mkv'):
            self.logger.log('Movie is not a matroska file - skip', LogLevel.Warning)
            return
        src = os.path.join(self.movie.path, self.movie.file)
        if not os.path.exists(src) or not os.path.isfile(src):
            return

        self.logger.log('Look for removable Audio-Tracks')
        keep_tracks = self.config.codec.keep_tracks
        audio_tracks = {}

        # get all audio codecs
        for section in self.codec_config.sections():
            if not 'Audio' in section:
                continue

            try:
                language = self.codec_config.get(section, 'Language').lower()
                id = int(self.codec_config.get(section, 'ID')) - 1
            except:
                continue
            audio_tracks[id] = language

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

            dst = os.path.join(self.movie.path, 'new.mkv')

            cmd = '{0} -o "{1}"{2} "{3}"'.format(self.config.codec.mkvmerge, dst,
                                                 delete_audiotracks,
                                                 src)

            self.logger.log("Remove {0} audio-tracks".format(keep_tracks_count))
            self.logger.log('\a === DO NOT STOP THE PROCCESS - IT WILL DELETE YOUR MOVIE ===', LogLevel.Warning)
            self.logger.log('Execute mkvmerge: ' + cmd, LogLevel.Debug)
            open(dst, 'a').close()
            try:
                subprocess.check_call(cmd, shell=True)
            except:
                self.logger.log('Not able to merge MKV: ' + self.movie.file, LogLevel.Error)
                return

            old_filesize = os.path.getsize(src)
            new_filesize = os.path.getsize(dst)
            percent = 100 - (new_filesize / (old_filesize / 100))
            mb = (old_filesize - new_filesize) / 1024 / 1024
            self.logger.log('{0}% ({1} mb)saved'.format(percent, mb))
            self.logger.log('REPLACE {0}'.format(src), LogLevel.Debug)
            os.remove(src)
            try:
                os.rename(dst, src)
            except:
                shutil.move(dst, src)

            os.remove(self.file)
            self.codec_config = ConfigParser.ConfigParser()
            open(self.file, 'a').close()
            self._run_mediainfo()
            self.codec_config.read(self.file)

    def __del__(self):
        if os.path.exists(self.file):
            os.remove(self.file)
