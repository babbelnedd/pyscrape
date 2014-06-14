import urllib
import time

from core.helpers.config import config
from core.helpers.logger import log, LogLevel
from core.helpers.utils import ping


class Xbmc(object):
    def __init__(self):
        xbmc = config.xbmc
        self.url_base = '{0}://{1}:{2}@{3}:{4}'.format(xbmc.protocol, xbmc.user, xbmc.password, xbmc.ip, xbmc.port)

    def update(self):
        log('Update XBMC database')
        if not ping(config.xbmc.ip, config.xbmc.port):
            log('XBMC host is not available')
            return -1

        url = self.url_base + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Scan"}'
        urllib.urlretrieve(url)
        return 0

    def clean(self):
        log('Clean XBMC database')
        if not ping(config.xbmc.ip, config.xbmc.port):
            log('XBMC host is no available', LogLevel.Warning)
            return -1

        url = self.url_base + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Clean"}'
        urllib.urlretrieve(url)
        return 0

    def full_scan(self, sleep=120):
        if self.clean() == 0:
            time.sleep(sleep)
            self.update()