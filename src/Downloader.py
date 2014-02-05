import os
import urllib
import time

from Logger import log, LogLevel


class Downloader(object):
    def __init__(self, refresh=False):
        self.refresh = refresh

    def _try_download(self, src, dst, attempts=10):
        if self.refresh:
            if os.path.exists(dst):
                log('File {0} exists already - skip'.format(dst), LogLevel.Debug)
                return 0

        try_again = True
        count = 0
        while try_again:
            try:
                urllib.urlretrieve(src, dst)
                try_again = False
            except IOError, e:
                log(dst + " could not be downloaded", LogLevel.Error)
                log(unicode(e), 'ERROR')
                if count < attempts:
                    log('Wait 10 Seconds and try it again', LogLevel.Error)
                    time.sleep(10)
                else:
                    try_again = False
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

        f = urllib.urlopen(src)
        size = f.headers["Content-Length"]

        if int(os.path.getsize(dst)) < int(size):
            log('Downloaded file is corrupt - download it again', LogLevel.Warning)
            self.download(src, dst)

        log('Downloaded: ' + msg, LogLevel.Debug)