import urllib2
import json
import time
from Config import Config
from Logger import Logger, LogLevel


config = Config()
logger = Logger()


def __request(request):
    logger.log('Send Fanart Request: ' + request.replace(config.fanart.api_key, 'XXX'), 'DEBUG')
    headers = {'Accept': 'application/json'}
    request = urllib2.Request(request, headers=headers)
    response_body = urllib2.urlopen(request).read()
    try:
        result = json.loads(response_body)
    except:
        result = json.loads(response_body.decode('utf-8'))

    return result


def get_movie(id):
    result_format = 'JSON'
    req = '{0}movie/{1}/{2}/{3}'.format(config.fanart.url_base, config.fanart.api_key, id, result_format)
    try_again = True
    n = 0
    while try_again and n < 10:
        try:
            return __request(req)
        except urllib2.HTTPError:
            n += 1
            try_again = True
            logger.log('Ooops.. FanartTV Error - Try again', LogLevel.Warning)
            time.sleep(2)