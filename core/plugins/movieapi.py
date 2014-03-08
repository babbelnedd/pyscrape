"""
This is a plugin-wrapper for plugins from type PluginType.Movie
"""
from core.helpers.config import config

from core.plugins.pluginloader import get_plugins
from core.plugins.plugintype import PluginType
from core.plugins.pluginbase import Movie

#region Private Attributes


_plugins = get_plugins(PluginType.MovieScanner)


#endregion

#region Private Methods


def __get(func, **kwargs):
    for plugin in _plugins:
        function = getattr(plugin, func.__name__, None)
        item = function(**kwargs)
        if item is not None and item != '':
            return item


def __get_all(func, **kwargs):
    result = None
    for plugin in _plugins:
        function = getattr(plugin, func.__name__, None)
        item = function(**kwargs)
        if item is not None and item != '':
            if result is None and isinstance(item, list):
                result = item
            elif result is None and isinstance(item, dict):
                result = [item]
            else:
                for x in [x for x in item if x not in result]:
                    result.append(x)
    return result


#endregion


def get_mpaa(country, imdb_id=None, tmdb_id=None):
    return __get(Movie.get_mpaa, country=country, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_tmdb_id(title=None, year=None, imdb_id=None):
    return __get(Movie.get_tmdb_id, title=title, year=year, imdb_id=imdb_id)


def get_imdb_id(title=None, year=None, tmdb_id=None):
    return __get(Movie.get_imdb_id, title=title, year=year, tmdb_id=tmdb_id)


def get_credits(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_credits, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_posters(imdb_id=None, tmdb_id=None):
    result = __get_all(Movie.get_posters, language=config.pyscrape.language, imdb_id=imdb_id, tmdb_id=tmdb_id)
    if result is None or result == '':
        result = __get_all(Movie.get_posters, language=config.pyscrape.fallback_language, imdb_id=imdb_id,
                           tmdb_id=tmdb_id)
    return result


def get_banners(imdb_id=None, tmdb_id=None):
    result = __get_all(Movie.get_banners, language=config.pyscrape.language, imdb_id=imdb_id, tmdb_id=tmdb_id)
    if result is None or result == '':
        result = __get_all(Movie.get_banners, language=config.pyscrape.fallback_language, imdb_id=imdb_id,
                           tmdb_id=tmdb_id)
    return result


def get_disc_art(imdb_id=None, tmdb_id=None):
    result = __get_all(Movie.get_disc_art, language=config.pyscrape.language, imdb_id=imdb_id, tmdb_id=tmdb_id)
    if result is None or result == '':
        result = __get_all(Movie.get_disc_art, language=config.pyscrape.fallback_language, imdb_id=imdb_id,
                           tmdb_id=tmdb_id)
    return result


def get_clearart(imdb_id=None, tmdb_id=None):
    result = __get_all(Movie.get_clearart, language=config.pyscrape.language, imdb_id=imdb_id, tmdb_id=tmdb_id)
    if result is None or result == '':
        result = __get_all(Movie.get_clearart, language=config.pyscrape.fallback_language, imdb_id=imdb_id,
                           tmdb_id=tmdb_id)
    return result


def get_logos(imdb_id=None, tmdb_id=None):
    result = __get_all(Movie.get_logos, language=config.pyscrape.language, imdb_id=imdb_id, tmdb_id=tmdb_id)
    if result is None or result == '':
        result = __get_all(Movie.get_logos, language=config.pyscrape.fallback_language, imdb_id=imdb_id,
                           tmdb_id=tmdb_id)
    return result


def get_backdrops(imdb_id=None, tmdb_id=None):
    return __get_all(Movie.get_backdrops, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_landscapes(imdb_id=None, tmdb_id=None):
    return __get_all(Movie.get_landscapes, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_release(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_release, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_original_title(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_original_title, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_title(imdb_id=None, tmdb_id=None):
    #todo: add country to config!!
    result = __get(Movie.get_title, country='DE', imdb_id=imdb_id, tmdb_id=tmdb_id)
    if result is None or result == '':
        result = __get(Movie.get_title, country='US', imdb_id=imdb_id,
                       tmdb_id=tmdb_id)
    return result


def get_vote_count(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_vote_count, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_average_rating(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_average_rating, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_popularity(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_popularity, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_plot(imdb_id=None, tmdb_id=None):
    result = __get(Movie.get_plot, language=config.pyscrape.language, imdb_id=imdb_id, tmdb_id=tmdb_id)
    if result is None or result == '':
        result = __get(Movie.get_plot, language=config.pyscrape.fallback_language, imdb_id=imdb_id,
                       tmdb_id=tmdb_id)
    return result


def get_tagline(imdb_id=None, tmdb_id=None):
    result = __get(Movie.get_tagline, language=config.pyscrape.language, imdb_id=imdb_id, tmdb_id=tmdb_id)
    if result is None or result == '':
        result = __get(Movie.get_tagline, language=config.pyscrape.fallback_language, imdb_id=imdb_id,
                       tmdb_id=tmdb_id)
    return result


def get_outline(imdb_id=None, tmdb_id=None):
    result = __get(Movie.get_outline, language=config.pyscrape.language, imdb_id=imdb_id, tmdb_id=tmdb_id)
    if result is None or result == '':
        result = __get(Movie.get_outline, language=config.pyscrape.fallback_language, imdb_id=imdb_id,
                       tmdb_id=tmdb_id)
    return result


def get_revenue(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_revenue, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_budget(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_budget, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_collection(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_collection, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_production_countries(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_production_countries, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_production_companies(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_production_companies, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_genres(imdb_id=None, tmdb_id=None):
    return __get_all(Movie.get_genres, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_spoken_languages(imdb_id=None, tmdb_id=None):
    return __get(Movie.get_spoken_languages, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_all(imdb_id=None, tmdb_id=None):
    if imdb_id is None and tmdb_id is None:
        return
    title = get_title(tmdb_id=tmdb_id, imdb_id=imdb_id)
    original_title = get_original_title(tmdb_id=tmdb_id, imdb_id=imdb_id)
    plot = get_plot(tmdb_id=tmdb_id, imdb_id=imdb_id)
    genres = get_genres(tmdb_id=tmdb_id, imdb_id=imdb_id)
    tagline = get_tagline(tmdb_id=tmdb_id, imdb_id=imdb_id)
    outline = get_outline(tmdb_id=tmdb_id, imdb_id=imdb_id)
    mpaa = get_mpaa(tmdb_id=tmdb_id, imdb_id=imdb_id, country='DE')  # todo: add country to config
    credits = get_credits(tmdb_id=tmdb_id, imdb_id=imdb_id)
    posters = get_posters(tmdb_id=tmdb_id, imdb_id=imdb_id)
    banners = get_banners(tmdb_id=tmdb_id, imdb_id=imdb_id)
    disc_art = get_disc_art(tmdb_id=tmdb_id, imdb_id=imdb_id)
    clearart = get_clearart(tmdb_id=tmdb_id, imdb_id=imdb_id)
    backdrops = get_backdrops(tmdb_id=tmdb_id, imdb_id=imdb_id)
    logos = get_logos(tmdb_id=tmdb_id, imdb_id=imdb_id)
    landscapes = get_landscapes(tmdb_id=tmdb_id, imdb_id=imdb_id)
    rating = get_average_rating(tmdb_id=tmdb_id, imdb_id=imdb_id)
    vote_count = get_vote_count(tmdb_id=tmdb_id, imdb_id=imdb_id)
    popularity = get_popularity(tmdb_id=tmdb_id, imdb_id=imdb_id)
    revenue = get_revenue(tmdb_id=tmdb_id, imdb_id=imdb_id)
    budget = get_budget(tmdb_id=tmdb_id, imdb_id=imdb_id)
    collection = get_collection(tmdb_id=tmdb_id, imdb_id=imdb_id)
    production_countries = get_production_countries(tmdb_id=tmdb_id, imdb_id=imdb_id)
    production_companies = get_production_companies(tmdb_id=tmdb_id, imdb_id=imdb_id)
    spoken_languages = get_spoken_languages(tmdb_id=tmdb_id, imdb_id=imdb_id)
    release = get_release(tmdb_id=tmdb_id, imdb_id=imdb_id)

    m = {'title': title, 'tmdb_id': tmdb_id, 'imdb_id': imdb_id, 'plot': plot, 'tagline': tagline,
         'outline': outline, 'mpaa': mpaa, 'credits': credits, 'posters': posters,
         'banners': banners, 'disc_art': disc_art, 'clearart': clearart, 'backdrops': backdrops,
         'logos': logos, 'landscapes': landscapes, 'original_title': original_title,
         'genres': genres, 'rating': rating, 'vote_count': vote_count, 'popularity': popularity,
         'release': release, 'revenue': revenue, 'budget': budget, 'collection': collection,
         'production_countries': production_countries, 'production_companies': production_companies,
         'spoken_languages': spoken_languages}
    return m