# -*- coding: utf-8 -*-
import shutil
import subprocess

__author__ = 'LSC'
from Logger import LogLevel
import os, ConfigParser


class Codec(object):
    def __init__(self, logger, config, movie):
        self.logger = logger
        self.config = config
        self.movie = movie

        fileName, fileExtension = os.path.splitext(movie.file)
        self.file = os.path.join(movie.path, fileName + '.nfo.tmp')
        path = os.path.join(movie.path, movie.file)
        try:
            path = unicode(path).encode('utf8')
        except:
            pass
        
        self.path = path
        if movie.file == '' or not os.path.isfile(os.path.join(movie.path, movie.file)):
            self.logger.log('No movie file found - skip Codec inforamtion', LogLevel.Warning)
            return

        self.codec_config = ConfigParser.ConfigParser()
        open(self.file, 'a').close()
        self.__runMediainfo()
        self.codec_config.read(self.file)

    def __runMediainfo(self):
        self.logger.log('Start mediainfo', 'DEBUG')
        
        parameter = ' --logfile="{0}" "{1}"'.format(self.file, self.path)

        import sys
        if 'linux' in sys.platform.lower():
            parameter += '  >/dev/null'
        # elif 'win32' in sys.platform.lower():
        #     parameter += ' > nul'
        cmd = self.config.codec.mediainfo_path + parameter
        os.system(cmd)
        # create section headers
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

    def __get(self, sec, attr):
        try:
            return self.codec_config.get(sec, attr)
        except:
            return ''

    def getRuntime(self):
        duration = self.__get('Video', 'Duration').replace(' ', '').replace('mn', '').lower().split('h')
        if duration != '' and duration != ['']:
            h = int(duration[0]) * 60
            m = int(duration[1])
            return h + m
        return 0

    def getAudioXml(self):
        def audioXml():
            xml = ''
            for section in self.codec_config.sections():
                if 'Audio' in section:
                    audio = {}
                    audio['codec'] = self.__get(section, 'Format')
                    if 'AC-3' in audio['codec']:
                        audio['codec'] = 'AC3'
                    audio['channels'] = self.__get(section, 'Channel count').replace('channels', '').replace(' ', '')
                    audio['language'] = self.__get(section, 'Language')
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
        return audioXml()

    def getVideoXml(self):
        def videoXml():
            video = {}
            duration = self.__get('Video', 'Duration').replace(' ', '').replace('mn', '').lower().split('h')
            if duration != '' and duration != ['']:
                h = int(duration[0]) * 60
                m = int(duration[1])
                video['duration'] = (h + m) * 60
            else:
                video['duration'] = 0
            video['width'] = self.__get('Video', 'Width').replace('pixels', '').replace(' ', '')
            video['height'] = self.__get('Video', 'Height').replace('pixels', '').replace(' ', '')
            video['bitrate'] = self.__get('Video', 'Bit rate')
            video['fps'] = self.__get('Video', 'Frame rate')
            video['aspect'] = self.__get('Video', 'Display aspect ratio')
            video['scantype'] = self.__get('Video', 'Scan type')
            video['codec'] = self.__get('Video', 'Writing library')
            if 'x264' in video['codec'].lower():
                video['codec'] = 'h264'
            elif 'h264' in video['codec'].lower():
                video['codec'] = 'h264'
            elif 'xvid' in video['codec'].lower():
              video['codec'] = 'xvid'
            # welche codecs gibt es noch...?

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
        return videoXml()

    def deleteAudioTracks(self):
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
        for track in audio_tracks:
            _language = audio_tracks[track]
            if _language == '':
                continue
            if _language in keep_tracks:
                keep_tracks_count += 1
            else:
                deletable_tracks.append(track)
                #delete_tracks_count += 1

        # check if we have to delete audio tracks
        if len(deletable_tracks) > 0 and keep_tracks_count > 0:
            # build cmd-string
            delete_subtitles = ''
            # if self.config.codec.keep_subs == 'none':
            #     delete_subtitles = ' --no-subtitles'
            delete_audiotracks = ' --audio-tracks !'

            for n in range(0,len(deletable_tracks)):
                if n > 0:
                    delete_audiotracks += ','
                delete_audiotracks += str(deletable_tracks[n])

            # for track in deletable_tracks:
            #     delete_audiotracks += '{0}'.format(track)

            dst = os.path.join(self.movie.path, 'new.mkv')

            cmd = '{0} -o "{1}"{2}{3} "{4}"'.format(self.config.codec.mkvmerge, dst, delete_subtitles,
                                                    delete_audiotracks,
                                                    src)

            # warn / exec cmd
            self.logger.log("Remove {0} audio-tracks".format(keep_tracks_count))
            self.logger.log('\a === DO NOT STOP THE PROCCESS - IT WILL DELETE YOUR MOVIE ===', LogLevel.Warning)
            self.logger.log('Execute mkvmerge: ' + cmd, LogLevel.Debug)
            open(dst, 'a').close()
            #os.system(cmd)
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
            self.__runMediainfo()
            self.codec_config.read(self.file)


    def __del__(self):
        if os.path.exists(self.file):
            os.remove(self.file)
