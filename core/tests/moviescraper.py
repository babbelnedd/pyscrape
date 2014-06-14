# coding=utf-8
import os
import sys
import unittest
import shutil
from lxml import etree

from core.Movie import Movie


path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if not path in sys.path:
    sys.path.insert(1, path)
del path

from core import moviescraper


class MovieScraperTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MovieScraperTests, self).__init__(*args, **kwargs)
        self.tmp = os.path.join(os.path.dirname(__file__), 'tmp')
        self.bruno = os.path.join(self.tmp, 'Brüno (tt0889583) (2009)')
        self.iceage = os.path.join(self.tmp, 'Ice Age (tt0268380) (2002)')

    def setUp(self):
        if not os.path.exists(self.tmp): os.mkdir(self.tmp)
        if not os.path.exists(self.bruno): os.mkdir(self.bruno)
        if not os.path.exists(self.iceage): os.mkdir(self.iceage)

    def tearDown(self):
        if os.path.exists(self.tmp): shutil.rmtree(self.tmp)
        if os.path.exists(self.bruno): shutil.rmtree(self.bruno)
        if os.path.exists(self.iceage): shutil.rmtree(self.iceage)

    def test_get_movie_raises_exception_on_wrong_path(self):
        self.assertRaises(OSError, moviescraper.get_movie, self.tmp, self.bruno + 'nope')

    def test_get_movie_correct_attributes(self):
        movie = moviescraper.get_movie(self.tmp, self.bruno)
        self.assertEqual(os.path.join(self.tmp, self.bruno), movie.path)
        self.assertEqual('Brüno', movie.search_title)
        self.assertEqual('Brueno', movie.search_alternative_title)
        self.assertEqual('tt0889583', movie.imdb)
        self.assertEqual('2009', movie.search_year)
        self.assertEqual([], movie.files)

    def test_get_movies(self):
        movies = moviescraper.get_movies(self.tmp)
        self.assertEqual(2, len(movies))
        [self.assertIsInstance(m, Movie) for m in movies]

    def test_get_metadata(self):
        movie = moviescraper.get_movie(self.tmp, self.iceage)
        movie = moviescraper.get_metadata(movie)
        self.assertEqual('2002', movie.year)
        self.assertIn('animation', [g.lower() for g in movie.genres.split('/')])

    def test_create_nfo(self):
        movie = moviescraper.get_movie(self.tmp, self.iceage)
        movie = moviescraper.get_metadata(movie)
        moviescraper.create_nfo(movie)
        nfo_file = os.path.join(self.tmp, self.iceage, 'Ice Age (tt0268380) (2002).nfo')
        self.assertTrue(os.path.exists(nfo_file))
        root = etree.parse(nfo_file).getroot()
        # todo: verify XML values