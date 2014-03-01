# from http://stackoverflow.com/a/1823101/1922357
def intWithCommas(x):
    if type(x) not in [type(0), type(0L)]:
        raise TypeError("Parameter must be an integer.")
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)


def _get_chars(file):
    chars = {}
    with open(file) as f:
        content = f.readlines()
    for c in content:
        c = c.split(':')
        x = c[0].strip()

        try:
            y = c[1].strip()
        except:
            y = ''
        chars[x] = y
    return chars


def replace(string):
    import os

    root = os.path.dirname(os.path.realpath(__file__))
    chars = _get_chars(os.path.join(root, '../configuration', 'replace'))
    try:
        string = string.encode('utf8')
    except:
        pass
    for key in chars.keys():
        value = chars[key]
        string = string.replace(key, value)
    return string


def rename_subfolder(root):
    for path in os.listdir(root.decode('utf8')):
        src = os.path.join(root, path)
        if os.path.isdir(src):
            new = replace(path)
            dst = os.path.join(root, new)
            if src != dst:
                log(u'Move {0} to {1}'.format(src, dst), 'MOVE')
                os.rename(src, dst)


def rename_dir(folder):
    folder = unicode(folder, encoding='utf8')
    while folder.endswith('/'):
        folder = folder[0:(len(folder) - 1)]

    dst = folder
    if os.path.isdir(folder):
        while folder.endswith('/'):
            folder = folder[:1]
        root, dir = os.path.split(folder)
        src = folder
        new = replace(dir)
        dst = os.path.join(root, new)
        if src != dst:
            log(u'Move {0} to {1}'.format(src, dst), 'MOVE')
            os.rename(src, dst)
    try:
        dst = unicode(dst, encoding='utf8')
    except:
        pass

    return dst


def rename_files(root):
    for file in os.listdir(root.decode('utf8')):
        if os.path.isfile(os.path.join(root, file)):
            replaced_file = replace(file)
            if file != replaced_file:
                src = os.path.join(root, file)
                dst = os.path.join(root, replaced_file)
                log(u'Move {0} to {1}'.format(src, dst), 'MOVE')
                os.rename(src, dst)


def get_root():
    import core

    return core.__path__[0]


def get_movie_extensions():
    import os

    result = []
    root = os.path.abspath(os.path.join(get_root(), os.pardir))
    for extension in [f for f in open(os.path.join(root, 'configuration', 'extensions')).readlines() if
                      f.startswith('.') and not f.startswith('..')]:
        result.append(extension.lower().replace('\n', ''))
    return result


def get_all_extensions():
    return get_movie_extensions() + get_other_extensions()


def get_other_extensions():
    import os

    result = []
    root = os.path.abspath(os.path.join(get_root(), os.pardir))
    for extension in [f for f in open(os.path.join(root, 'configuration', 'extensions')).readlines() if
                      f.startswith('..')]:
        result.append(extension[1:].lower().replace('\n', ''))
    return result


def ping(ip, port):
    import socket

    port = int(port)
    try:
        sock = socket.socket()
        sock.connect((ip, port))
        sock.close()
        return True
    except socket.error:
        return False


def _try_download(src, dst, attempts=10, refresh=False):
    if refresh:
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


def download(src, dst, refresh=False):
    start = time.time()
    if _try_download(src=src, dst=dst, refresh=refresh) == 0:
        return
    elapsed = time.time() - start
    kbps = '[%.2f kbps]' % ((os.path.getsize(dst) / 1024) / elapsed)
    elapsed = '[%.2f s]' % elapsed
    msg = src + ' {0} {1}'.format(kbps, elapsed)

    try:
        f = urllib.urlopen(src)
        size = f.headers['Content-Length']

        if int(os.path.getsize(dst)) < int(size):
            log('Downloaded file is corrupt - download it again', LogLevel.Warning)
            download(src, dst)
    except KeyError:
        log('Server do not provide "Content-Length" in header, can\'t verify downloaded item', LogLevel.Debug)

    log('Downloaded: ' + msg, LogLevel.Debug)


if __name__ != 'main':
    from Logger import log, LogLevel
    import os
    import urllib
    import time