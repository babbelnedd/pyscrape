# -*- coding: utf-8 -*-
import httplib
import urllib
import datetime
import os

from Config import Config


root = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(root, 'logs')
logfile = os.path.join(path, 'pyscrape.log')
errorfile = os.path.join(path, 'error.log')
__cfg = Config()

if not os.path.exists(path):
    os.makedirs(path)


def log(text, level=''):
    if level == '':
        level = LogLevel.Info

    if not __cfg.pyscrape.debug_log and level.upper() == 'DEBUG':
        return

    if level == LogLevel.Error:
        level = level.upper()

    text = text.strip()
    level = level.strip().upper()
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    output = '[' + timestamp + '][' + level + ']: ' + text

    with open(logfile, 'a') as logFile:
        if isinstance(output, unicode):
            output = output.encode('ascii', 'replace')
        logFile.write(output + '\n')

    if level == LogLevel.Error or level == LogLevel.Warning:
        with open(errorfile, 'a') as logFile:
            logFile.write(output + '\n')

    _print(output, level)


def pushover(notification):
    token = __cfg.pushover.token
    key = __cfg.pushover.key

    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
                 urllib.urlencode({"token": token,
                                   "user": key,
                                   "message": notification,
                 }), {"Content-type": "application/x-www-form-urlencoded"})
    conn.getresponse()


def whiteline():
    with open(logfile, 'a') as logFile:
        print('\n')
        logFile.write('\n')


def _print(msg, level):
    from TerminalColor import print_colored as print_colored, Foreground

    if level == LogLevel.Debug:
        print_colored(msg, Foreground.White)
    elif level == LogLevel.Info:
        print_colored(msg, Foreground.Green)
    elif level == LogLevel.Warning:
        print_colored(msg, Foreground.Yellow)
    elif level == LogLevel.Error:
        print_colored(msg, Foreground.Red)
    else:
        print_colored(msg, Foreground.Cyan)


class LogLevel(object):
    Debug = 'DEBUG'
    Info = 'INFO'
    Warning = 'WARNING'
    Error = 'ERROR'