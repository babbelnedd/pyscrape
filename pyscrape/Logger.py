# -*- coding: utf-8 -*-
import httplib
import urllib
import datetime
import os
import utils
from termcolor import colored


class Logger(object):
    def __init__(self, logfile, cfg):
        path = os.path.join(utils.get_root(), 'logs')
        if not os.path.exists(path):
            os.makedirs(path)
        self.logfile = os.path.join(path, logfile)
        self.errorfile = os.path.join(path, 'error.log')
        self.__cfg = cfg
        if os.path.isfile(self.logfile):
            if os.path.isfile(self.logfile + '.old'):
                os.remove(self.logfile + '.old')
            os.rename(self.logfile, self.logfile + '.old')

    def log(self, text, level=''):
        if level == '': level = LogLevel.Info

        if not self.__cfg.pyscrape.debug_log and level.upper() == 'DEBUG':
            return

        if level == LogLevel.Error:
            level = level.upper()

        text = text.strip()
        level = level.strip().upper()
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        output = '[' + timestamp + '][' + level + ']: ' + text

        with open(self.logfile, 'a') as logFile:
            if isinstance(output, unicode):
                output = output.encode('ascii', 'replace')
            logFile.write(output + '\n')

        if level == LogLevel.Error or level == LogLevel.Warning:
            with open(self.errorfile, 'a') as logFile:
                logFile.write(output + '\n')

        self._print(output, level)

    def pushover(self, notification):
        token = self.__cfg.pushover.token
        key = self.__cfg.pushover.key

        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
                     urllib.urlencode({"token": token,
                                       "user": key,
                                       "message": notification,
                     }), {"Content-type": "application/x-www-form-urlencoded"})
        conn.getresponse()

    def whiteline(self):
        with open(self.logfile, 'a') as logFile:
            print('\n')
            logFile.write('\n')

    def _print(self, msg, level):
        if level == LogLevel.Debug:
            print colored(msg, 'white')
        elif level == LogLevel.Info:
            print colored(msg, 'green')
        elif level == LogLevel.Warning:
            print colored(msg, 'yellow')
        elif level == LogLevel.Error:
            print colored(msg, 'red')
        else:
            print colored(msg, 'cyan')


class LogLevel(object):
    Debug = 'DEBUG'
    Info = 'INFO'
    Warning = 'WARNING'
    Error = 'ERROR'
