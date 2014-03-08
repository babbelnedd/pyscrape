import datetime
import os

from core.helpers.config import config
import core.helpers.decorator
import core


__root = os.path.abspath(os.path.join(core.__path__[0], os.pardir))
_path = os.path.join(__root, '.logs')
_logfile = os.path.join(_path, 'pyscrape.log')
_errorfile = os.path.join(_path, 'error.log')
quiet = False

if not os.path.exists(_path):
    os.makedirs(_path)
if not os.path.exists(_logfile):
    open(_logfile, 'w+')
if not os.path.exists(_errorfile):
    open(_errorfile, 'w+')


@core.helpers.decorator.Logger
def log(text, level=''):
    if level == '':
        level = LogLevel.Info

    if level == LogLevel.Debug and not config.pyscrape.debug_log:
        return

    if level == LogLevel.Error:
        level = level.upper()

    text = text.strip()
    level = level.strip().upper()
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    output = '[' + timestamp + '][' + level + ']: ' + text

    with open(_logfile, 'a') as logFile:
        if isinstance(output, unicode):
            output = output.encode('ascii', 'replace')
        logFile.write(output + '\n')

    if level == LogLevel.Error or level == LogLevel.Warning:
        with open(_errorfile, 'a') as logFile:
            logFile.write(output + '\n')

    if not quiet:
        _print(output, level)


def whiteline():
    with open(_logfile, 'a') as logFile:
        if not quiet:
            print('\n')
        logFile.write('\n')


def _print(msg, level):
    from core.helpers.terminal import print_colored as print_colored, Foreground

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