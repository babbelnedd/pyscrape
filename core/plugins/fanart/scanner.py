class FanartScanner(object):
    def __init__(self):
        from core.plugins.PluginType import PluginType

        self.info = {'type': PluginType.MovieScanner,
                     'author': 'Lucas Schad',
                     'name': 'Fanart.tv Movie Scanner',
                     'version': '0.10'}