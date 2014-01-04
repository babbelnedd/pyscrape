import urllib2

try:
    import simplejson as json
except:
    import json
from Config import Config
from Logger import Logger


class FanartTvApi(object):
    def __init__(self):
        self.config = Config()
        self.logger = Logger()

    def __request(self, id):
        format = 'JSON'
        req = '{0}{1}/{2}/{3}'.format(self.config.fanart.url_base, self.config.fanart.api_key, id, format)

        self.logger.log('Send Fanart Request: ' + req.replace(self.config.fanart.api_key, 'XXX'), 'DEBUG')
        headers = {'Accept': 'application/json'}
        request = urllib2.Request(req, headers=headers)
        response_body = urllib2.urlopen(request).read()
        try:
            result = json.loads(response_body)
        except:
            result = json.loads(response_body.decode('utf-8'))
        return result

    def get_all(self, id):
        import time

        try_again = True
        n = 1
        while try_again:
            try:
                try_again = False
                return self.__request(id)
            except:
                n += 1
                try_again = True
                print 'Ooops.. FanartTV Error - Try again'
                time.sleep(2)
