from core.PluginLoader import get_plugins
from core.plugins.PluginType import PluginType

_plugins = get_plugins(PluginType.MovieScanner)


def get_mpaa(country, imdb_id=None, tmdb_id=None):
    for item in [p.get_mpaa(country=country, imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_tmdb_id(title=None, year=None, imdb_id=None):
    for item in [p.get_tmdb_id(title=title, year=year, imdb_id=imdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_imdb_id(title=None, year=None, tmdb_id=None):
    for item in [p.get_imdb_id(title=title, year=year, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_credits(imdb_id=None, tmdb_id=None):
    for item in [p.get_credits(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_posters(lang=None, imdb_id=None, tmdb_id=None):
    #todo: should I add all posters to one collection?
    #something like: for posters in ...: if posters is not None: all_posters.add(posters)
    for item in [p.get_posters(lang=lang, imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_banners(imdb_id=None, tmdb_id=None):
    for item in [p.get_banners(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_disc_art(language, imdb_id=None, tmdb_id=None):
    for item in [p.get_disc_art(language=language, imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_clearart(language, imdb_id=None, tmdb_id=None):
    for item in [p.get_clearart(language=language, imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_logos(language, imdb_id=None, tmdb_id=None):
    for item in [p.get_logos(language=language, imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_backdrops(imdb_id=None, tmdb_id=None):
    for item in [p.get_backdrops(tmdb_id=tmdb_id, imdb_id=imdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_landscapes(imdb_id=None, tmdb_id=None):
    return None


def get_release(imdb_id=None, tmdb_id=None):
    for item in [p.get_release(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_original_title(imdb_id=None, tmdb_id=None):
    for item in [p.get_original_title(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_vote_count(imdb_id=None, tmdb_id=None):
    for item in [p.get_vote_count(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_average_rating(imdb_id=None, tmdb_id=None):
    for item in [p.get_average_rating(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_popularity(imdb_id=None, tmdb_id=None):
    for item in [p.get_popularity(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_plot(language, imdb_id=None, tmdb_id=None):
    for item in [p.get_plot(language=language, imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_tagline(language, imdb_id=None, tmdb_id=None):
    for item in [p.get_tagline(language=language, imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_outline(language, imdb_id=None, tmdb_id=None):
    for item in [p.get_outline(language=language, imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_revenue(imdb_id=None, tmdb_id=None):
    for item in [p.get_revenue(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_budget(imdb_id=None, tmdb_id=None):
    for item in [p.get_budget(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_collection(imdb_id=None, tmdb_id=None):
    for item in [p.get_collection(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_production_countries(imdb_id=None, tmdb_id=None):
    for item in [p.get_production_countries(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_production_companies(imdb_id=None, tmdb_id=None):
    for item in [p.get_production_companies(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_genres(imdb_id=None, tmdb_id=None):
    for item in [p.get_genres(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item


def get_spoken_languages(imdb_id=None, tmdb_id=None):
    for item in [p.get_spoken_languages(imdb_id=imdb_id, tmdb_id=tmdb_id) for p in _plugins]:
        if item is not None and item != '':
            return item