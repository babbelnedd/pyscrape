class Movie(object):
    def get_tmdb_id(self, title=None, year=None, imdb_id=None):
        """
        Tries to find the correct TMDB ID.

        @param  title       Title of the searched movie. Optional.
        @param  year        Release year of the searched movie. Optional.
        @param  imdb_id     IMDB ID of the searched movie. Optional.
        """
        return None

    def get_imdb_id(self, title=None, year=None, tmdb_id=None):
        """
        Tries to find the correct IMDB ID.

        @param      title       The title of the searched movie. Optional.
        @param      year        The release year of the searched movie. Optional.
        @param      tmdb_id     The TMDB ID of the searched movie. Optional.
        """
        return None

    def get_credits(self, imdb_id=None, tmdb_id=None):
        """
        Return the credits of a movie.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return schema:
            {
             'credits': [u'Bob Kane', u'Jonathan Nolan', ...],
             'directors': [u'Christopher Nolan', ...],
             'actors':[{'role': u'Bruce Wayne', 'name': u'Christian Bale', 'thumb': u'/vecCvACI2QhSE5fOoANeWDjxGKM.jpg'}, {...}]
             }
        """
        return None

    def get_mpaa(self, country, imdb_id=None, tmdb_id=None):
        """
        Gets the MPAA for a specific country. Country code is ISO639-2 standard.
        Both ID parameter are optional - but you need to pass one.

        @param      country     ISO639-2 country code
        @param      imdb_id     IMDB ID of a movie. Optional.
        @param      tmdb_id     TMDB ID of a movie. Optional.

        Example:
        get_mpaa('US', imdb_id='tt1234567')
        """
        return None

    def get_posters(self, language=None, imdb_id=None, tmdb_id=None):
        """
        Loads all available posters.

        @param  lang        The preferred Language of movie posters. Optional.
        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return schema:
            [{'url': u'http://image.tmdb.org/t/p/w1920/tdzD09XZzfSSgNTsYtmcgS4uSNE.jpg',
            'rating': 5.30505952380952),
            'vote_count': 11,
            'language': 'en'},
            {...},]

            Ordered descending by popularity. Highest first.
        """
        return None

    def get_banners(self, imdb_id=None, tmdb_id=None):
        """
        Loads all available banners.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type list
            [{'url': u'http://image.tmdb.org/t/p/w1920/tdzD09XZzfSSgNTsYtmcgS4uSNE.jpg',
            'rating': 5.30505952380952),
            'vote_count': 11},
            {...},]

            Ordered descending by popularity. Highest first.
        """
        return None

    def get_disc_art(self, language, imdb_id=None, tmdb_id=None):
        """
        Gets all images of discs (DVD, BluRay).

        @param  language    The preferred Language of movie posters. Optional.
        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return schema:
        [{'url': url, 'rating': float(rating), 'vote_count': int(vote_count)}, {..}, ..]

        Ordered descending by rating. Highest first.
        """
        return None

    def get_clearart(self, language, imdb_id=None, tmdb_id=None):
        """
        Gets all clearart images.

        @param  language    The preferred Language of movie posters. Optional.
        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return schema:
        [{'url': url, 'rating': float(rating), 'vote_count': int(vote_count)}, {..}, ..]

        Ordered descending by rating. Highest first.
        """
        return None

    def get_logos(self, language, imdb_id=None, tmdb_id=None):
        """
        Gets all logos.

        @param  language    The preferred Language of movie posters. Optional.
        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return schema:
        [{'url': url, 'rating': float(rating), 'vote_count': int(vote_count)}, {..}, ..]

        Ordered descending by rating. Highest first.
        """
        return None

    def get_backdrops(self, imdb_id=None, tmdb_id=None):
        """
        Gets all backdrops.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return schema:
        [{'url': url, 'rating': float(rating), 'vote_count': int(vote_count)}, {..}, ..]

        Ordered descending by rating. Highest first.
        """
        #images.append({'url': url, 'rating': image['vote_average'], 'vote_count': image['vote_count']})
        return None

    def get_landscapes(self, imdb_id=None, tmdb_id=None):
        return None

    def get_release(self, imdb_id=None, tmdb_id=None):
        """
        Gets the release date.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type str
        Format yyyy-mm-ddd
        """
        return None

    def get_original_title(self, imdb_id=None, tmdb_id=None):
        """
        Gets the original title.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type unicode
        """
        return None

    def get_vote_count(self, imdb_id=None, tmdb_id=None):
        """
        Gets the count of votes.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type int
        """
        return None

    def get_average_rating(self, imdb_id=None, tmdb_id=None):
        """
        Gets the average rating.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type float
        """
        return None

    def get_popularity(self, imdb_id=None, tmdb_id=None):
        """
        Gets the average rating.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type float
        """
        return None

    def get_plot(self, language, imdb_id=None, tmdb_id=None):
        """
        Gets the plot.

        @param  language    The language of the plot.
        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type unicode
        """
        return None

    def get_tagline(self, language, imdb_id=None, tmdb_id=None):
        """
        Gets the tagline.

        @param  language    The language of the plot.
        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type unicode
        """
        return None

    def get_outline(self, language, imdb_id=None, tmdb_id=None):
        """
        Gets the outline.

        @param  language    The language of the plot.
        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type unicode
        """
        return None

    def get_revenue(self, imdb_id=None, tmdb_id=None):
        """
        Gets the revenue of production.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type int
        """
        return None

    def get_budget(self, imdb_id=None, tmdb_id=None):
        """
        Gets the budget of production.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type int
        """
        return None

    def get_collection(self, imdb_id=None, tmdb_id=None):
        """
        Get the name of the collection, if the movie is part of a collection.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type unicode
        """
        return None

    def get_production_countries(self, imdb_id=None, tmdb_id=None):
        """
        Gets all the countries in which the movie takes place.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type list
        [u'Germany', u'America', ...]
        """
        return None

    def get_production_companies(self, imdb_id=None, tmdb_id=None):
        """
        Gets all companies (studios), which were involved in the production.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type list
        [u'Lionsgate', u'Warner Bros', ...]
        """
        return None

    def get_genres(self, imdb_id=None, tmdb_id=None):
        """
        Fetch all genres.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type list
        [u'Action', u'Drama', ..]
        """
        return None

    def get_spoken_languages(self, imdb_id=None, tmdb_id=None):
        """
        Fetch all the languages spoken in the movie.

        @param  imdb_id     The IMDB ID of a movie. Optional.
        @param  tmdb_id     The TMDB ID of a movie. Optional.

        Return type list
        [u'English', u'French', ..]
        """
        return None


class Show(object):
    pass


class Music(object):
    pass