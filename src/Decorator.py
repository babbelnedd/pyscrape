class Cached(object):
    def __init__(self, function):
        self.func = function
        self.cache = {}

    def __call__(self, *args):
        from Logger import log, LogLevel
        args = args[0]

        if args in self.cache:
            log('Found Cached Result', LogLevel.Debug)
        else:
            self.cache[args] = self.func(args)

        return self.cache[args]