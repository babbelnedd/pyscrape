from core.helpers.xmltodict import xml_to_dict
from core.helpers.xmltodict import XmlDictObject

_config_file = '/home/lsc/test.xml'
__config = xml_to_dict(_config_file)


def _generate_movie_path_dict(xml_dict):
    # todo: fallback/default values when 'general' settings do not exist (?)
    path = {}
    for item in xml_dict.iteritems():
        path[item[0]] = item[1]

    # fill dicts
    if 'extensions' not in path:
        path['extensions'] = __config['configuration']['extensions']

    if 'video' not in path['extensions']:
        path['extensions']['video'] = __config['configuration']['extensions']['video']

    if 'subtitle' not in path['extensions']:
        path['extensions']['subtitle'] = __config['configuration']['extensions']['subtitle']

    if 'languages' not in path:
        path['languages'] = __config['configuration']['movie']['general']['languages']

    if 'countries' not in path:
        path['countries'] = __config['configuration']['movie']['general']['countries']

    if 'downloads' not in path:
        path['downloads'] = __config['configuration']['movie']['downloads']

    for download in path['downloads']:
        if isinstance(path['downloads'][download], dict):
            path['downloads'][download] = [path['downloads'][download]]
        for item in path['downloads'][download]:
            if 'languages' not in item:
                item['languages'] = path['languages']

            if not isinstance(item['languages'], list):
                item['languages'] = item['languages'].split(',')

    # fill booleans
    if 'downloadimages' not in path:
        path['downloadimages'] = __config['configuration']['movie']['general']['settings']['downloadimages']

    if 'deleteexisting' not in path:
        path['deleteexisting'] = __config['configuration']['movie']['general']['settings']['deleteexisting']

    if 'active' not in path:
        path['active'] = True

    if isinstance(path['extensions']['video'], str):
        path['extensions']['video'] = path['extensions']['video'].split(',')
    if isinstance(path['extensions']['video'], str):
        path['extensions']['subtitle'] = path['extensions']['subtitle'].split(',')

    return path


def get_movie_paths():
    paths = __config['configuration']['movie']['general']['paths']['path']
    path_items = []
    if isinstance(paths, list):
        for p in paths:
            path_items.append(_generate_movie_path_dict(p))
    elif isinstance(paths, XmlDictObject):
        path_items.append(_generate_movie_path_dict(paths))

    return path_items


def config_is_valid(config_file):
    import xml

    try:
        xml_to_dict(config_file)
    except (IOError, TypeError, xml.etree.ElementTree.ParseError):
        return False

    return True