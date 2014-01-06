import urllib
import time
from Logger import Logger, LogLevel
from Config import Config
from utils import ping


class Xbmc(object):
    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        xbmc = self.config.xbmc
        self.url_base = '{0}://{1}:{2}@{3}:{4}'.format(xbmc.protocol, xbmc.user, xbmc.password, xbmc.ip, xbmc.port)


    def update(self):
        self.logger.log('Update XBMC database')
        if not ping(self.config.xbmc.ip, self.config.xbmc.port):
            self.logger.log('XBMC host is no available')
            return -1

        url = self.url_base + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Scan"}'
        urllib.urlretrieve(url)
        return 0


    def clean(self):
        self.logger.log('Clean XBMC database')
        if not ping(self.config.xbmc.ip, self.config.xbmc.port):
            self.logger.log('XBMC host is no available', LogLevel.Warning)
            return -1

        url = self.url_base + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Clean"}'
        urllib.urlretrieve(url)
        return 0


    def full_scan(self, sleep=120):
        if self.clean() == 0:
            time.sleep(sleep)
            self.update()