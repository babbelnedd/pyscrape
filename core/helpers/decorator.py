class Cached(object):
    def __init__(self, function):
        self.func = function
        self.cache = {}

    def __call__(self, *args):
        from core.helpers.logger import log, LogLevel

        if args in self.cache:
            _args = str(args).replace('(', '').replace(')', '')
            if _args.endswith(','):
                _args = _args[:len(_args) - 1]
            msg = 'Found Cached Result: {0}({1})'.format(self.func.__name__, _args)
            log(msg, LogLevel.Debug)
        else:
            self.cache[args] = self.func(*args)

        return self.cache[args]


class Logger(object):
    def __init__(self, function):
        self.log = function
        self.already_logged = False

    def __call__(self, *args):
        if not self.already_logged:
            split_log()

        self.already_logged = True
        if len(args) == 1:
            self.log(args[0])
        if len(args) == 2:
            self.log(args[0], args[1])


def split_log():
    import os
    import shutil
    import core

    root = os.path.abspath(os.path.join(core.__path__[0], os.pardir))
    path = os.path.join(root, '.logs')
    logfile = os.path.join(path, 'pyscrape.log')
    errorfile = os.path.join(path, 'error.log')
    kilobyte = 1024

    if os.path.getsize(logfile) > 1024 * kilobyte:
        old_logfile = logfile + '.old'
        if os.path.exists(old_logfile):
            os.remove(old_logfile)
        shutil.move(logfile, old_logfile)
        open(logfile, 'w+')

    if os.path.getsize(errorfile) > 1024 * kilobyte:
        old_errorfile = errorfile + '.old'
        if os.path.exists(old_errorfile):
            os.remove(old_errorfile)
        shutil.move(errorfile, old_errorfile)
        open(errorfile, 'w+')
