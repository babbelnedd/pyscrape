from Logger import Logger, LogLevel
import os
import urllib
import time


class Downloader(object):
    def __init__(self, refresh=False):
        self.logger = Logger()
        self.refresh = refresh

    def _try_download(self, src, dst, attempts=10):
        if self.refresh:
            if os.path.exists(dst):
                self.logger.log('File {0} exists already - skip'.format(dst), LogLevel.Debug)
                return 0

        tryAgain = True
        count = 0
        while tryAgain:
            try:
                urllib.urlretrieve(src, dst)
                tryAgain = False
            except IOError, e:
                self.logger.log(dst + " could not be downloaded", LogLevel.Error)
                self.logger.log(unicode(e), 'ERROR')
                if count < attempts:
                    self.logger.log('Wait 10 Seconds and try it again', LogLevel.Error)
                    time.sleep(10)
                else:
                    tryAgain = False
            finally:
                count += 1
        return 1

    def download(self, src, dst):
        start = time.time()
        if self._try_download(src, dst) == 0:
            return
        elapsed = time.time() - start
        kbps = '[%.2f kbps]' % ((os.path.getsize(dst) / 1024) / elapsed)
        elapsed = '[%.2f s]' % elapsed
        msg = src + ' {0} {1}'.format(kbps, elapsed)
        self.logger.log('Downloaded: ' + msg, LogLevel.Debug)