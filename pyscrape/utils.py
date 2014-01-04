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


def _getChars(file):
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
    chars = _getChars(os.path.join(root, 'system', 'replace'))
    try:
        string = string.encode('utf8')
    except:
        pass
    for key in chars.keys():
        value = chars[key]
        string = string.replace(key, value)
    return string


def rename_subfolder(root, logger):
    logger = logger
    import os

    for path in os.listdir(root.decode('utf8')):
        src = os.path.join(root, path)
        if os.path.isdir(src):
            new = replace(path)
            dst = os.path.join(root, new)
            if src != dst:
                logger.log(u'Move {0} to {1}'.format(src, dst), 'MOVE')
                os.rename(src, dst)


def rename_dir(folder, logger):
    import os

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
            logger.log(u'Move {0} to {1}'.format(src, dst), 'MOVE')
            os.rename(src, dst)
    try:
        dst = unicode(dst, encoding='utf8')
    except:
        pass

    return dst


def rename_files(root, logger):
    import os

    for file in os.listdir(root.decode('utf8')):
        if os.path.isfile(os.path.join(root, file)):
            replacedFile = replace(file)
            if file != replacedFile:
                src = os.path.join(root, file)
                dst = os.path.join(root, replacedFile)
                os.rename(src, dst)

def get_root():
    import os
    return os.path.dirname(os.path.realpath(__file__))