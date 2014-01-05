import urllib
import time
from Logger import Logger
from Config import Config


class Xbmc(object):
    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        xbmc = self.config.xbmc
        self.url_base = '{0}://{1}:{2}@{3}:{4}'.format(xbmc.protocol, xbmc.user, xbmc.password, xbmc.ip, xbmc.port)


    def update(self):
        self.logger.log('Update XBMC database')
        url = self.url_base + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Scan"}'
        urllib.urlretrieve(url)


    def clean(self):
        self.logger.log('Clean XBMC database')
        url = self.url_base + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Clean"}'
        urllib.urlretrieve(url)


    def full_scan(self, sleep=120):
        self.clean()
        time.sleep(sleep)
        self.update()