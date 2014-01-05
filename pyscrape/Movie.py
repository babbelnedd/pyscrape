# -*- coding: utf-8 -*-
class Movie(object):
    def __init__(self):
        self.title = ''                                 # Movie title
        self.id = ''                                    # TMDB ID
        self.imdbID = ''                                # IMDB ID
        self.orig_title = ''                            # Original title
        self.year = ''                                  # Year of release
        self.thumb = ''                                 # Url of thumb for .nfo
        self.posters = {}                               # Poster urls, format: url : rating
        self.backdrops = {}                             # Backdrop urls, format: url : rating
        self.rating = ''                                # Average rating from tmdb
        self.vote_count = ''                            # votes given (tmdb)
        self.search_year = ''                           # year from folder name
        self.search_title = 'unknown'                   # title from folder (without imdb id/year)
        self.search_alternative_title = 'unknown'       # title (with replaced characters)
        self.path = ''                                  # full path of file
        self.file = ''                                  # Filename (without path)
        self.trailers = {}                              # Trailer urls
        self.trailer = ''                               # Trailer for .nfo
        self.production_countries = ''                  # Production countries, format: Germany / Italy / ...
        self.production_companies = ''                  # Studios, format: Warner Bros / HBO / ...
        self.genres = ''                                # Genres, format: Comedy / Family / Drama
        self.runtime = '0'                              # Runtime in minutes
        self.plot = ''                                  # Plot
        self.outline = ''                               # Outline (1 sentence)
        self.tagline = ''                               # Summary
        self.collection = ''                            # Belongs to a collection? format: 'Lord of the Rings collection'
        self.spoken_languages = []                      # Spoken languages
        self.budget = ''                                # Budget (int)
        self.revenue = 0                                # Revenue (int)
        self.mpaa = ''                                  # Film Rating, http://bit.ly/1ljeYvJ
        self.top250 = ''                                # IMDB top 250
        self.sorted_title = ''                          # Title in collection view (XBMC)
        self.credits = ''                               # Credits, format: Foo Bar / John Wayne / ...
        self.popularity = 0                             # TMDB popularity
        self.audio_xml = ''                             # used for codec information
        self.video_xml = ''                             # used for codec information
