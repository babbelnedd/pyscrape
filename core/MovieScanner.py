from core.PluginLoader import get_plugins
from core.plugins.PluginType import PluginType
from core.plugins.PluginBase import Movie

_plugins = get_plugins(PluginType.MovieScanner)

#region Private Methods


def __call(func, **kwargs):
    for plugin in _plugins:
        function = getattr(plugin, func.__name__, None)
        item = function(**kwargs)
        if item is not None and item != '':
            return item


#endregion


def get_mpaa(country, imdb_id=None, tmdb_id=None):
    return __call(Movie.get_mpaa, country=country, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_tmdb_id(title=None, year=None, imdb_id=None):
    return __call(Movie.get_tmdb_id, title=title, year=year, imdb_id=imdb_id)


def get_imdb_id(title=None, year=None, tmdb_id=None):
    return __call(Movie.get_imdb_id, title=title, year=year, tmdb_id=tmdb_id)


def get_credits(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_credits, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_posters(lang=None, imdb_id=None, tmdb_id=None):
    #todo: should I add all posters to one collection?
    #something like: for posters in ...: if posters is not None: all_posters.add(posters)
    return __call(Movie.get_posters, lang=lang, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_banners(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_banners, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_disc_art(language, imdb_id=None, tmdb_id=None):
    return __call(Movie.get_disc_art, language=language, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_clearart(language, imdb_id=None, tmdb_id=None):
    return __call(Movie.get_clearart, language=language, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_logos(language, imdb_id=None, tmdb_id=None):
    return __call(Movie.get_logos, language=language, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_backdrops(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_backdrops, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_landscapes(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_landscapes, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_release(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_release, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_original_title(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_original_title, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_vote_count(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_vote_count, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_average_rating(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_average_rating, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_popularity(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_popularity, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_plot(language, imdb_id=None, tmdb_id=None):
    return __call(Movie.get_plot, language=language, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_tagline(language, imdb_id=None, tmdb_id=None):
    return __call(Movie.get_tagline, language=language, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_outline(language, imdb_id=None, tmdb_id=None):
    return __call(Movie.get_outline, language=language, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_revenue(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_revenue, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_budget(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_budget, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_collection(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_collection, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_production_countries(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_production_countries, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_production_companies(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_production_companies, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_genres(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_genres, imdb_id=imdb_id, tmdb_id=tmdb_id)


def get_spoken_languages(imdb_id=None, tmdb_id=None):
    return __call(Movie.get_spoken_languages, imdb_id=imdb_id, tmdb_id=tmdb_id)