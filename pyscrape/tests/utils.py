from pyscrape import utils

utils.ping('127.0.0.1', '80')
assert utils.ping('127.0.0.1', 9728) == False