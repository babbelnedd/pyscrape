# -*- coding: utf-8 -*-
class Movie(object):
    def __init__(self):
        self.title = ''                                 # Deutscher Titel
        self.id = ''                                    # TMDB ID
        self.imdbID = ''                                # IMDB ID
        self.orig_title = ''                            # Original Titel
        self.year = ''                                  # Erscheinungsjahr
        self.posters = {}                               # URLs zu Postern
        self.thumb = ''
        self.backdrops = {}                             # URLs zu Hintergründen
        self.fanart = ()                                # URLs zu Fanart
        self.rating = ''                                # Durchschnittliche Bewertung   (TMDB)
        self.vote_count = ''                            # Anzahl der agegebenen Stimmen (TMDB)
        self.search_year = 'unknown'                    # Jahresangabe aus dem Ordnernamen
        self.search_title = 'unknown'                   # Ordner Name ohne Jahresangabe
        self.search_alternative_title = 'unknown'       # Titel mit Umlauten
        self.path = ''                                  # Pfad des Films
        self.file = ''                                  # Dateiname
        self.trailers = {}                              # Trailer
        self.trailer = ''
        self.production_countries = ''                  # Produktionsland
        self.production_companies = ''                  # Produzierendes Unternehmen Bsp.: Warner Bros
        self.genres = ''                                # Genres
        self.runtime = '0'                              # Dauer des Films
        self.plot = ''                                  # Handlung
        self.outline = ''                               # Handlungs Übersicht
        self.tagline = ''                               # Zusammenfassung
        self.budget = ''                                # Budget
        self.collection = ''
        self.spoken_languages = []                      # Im Film gesprochene Sprachen
        self.revenue = 0                                # Einkommen vom Film
        self.mpaa = ''
        self.top250 = ''
        self.sorted_title = ''
        self.thumb = ''
        self.credits = ''
        self.audio_xml = ''
        self.video_xml =''
        self.popularity = 0