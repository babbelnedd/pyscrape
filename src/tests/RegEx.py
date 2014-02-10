import unittest
from src import RegEx


class RegExTests(unittest.TestCase):
    def test_get_movie(self):
        result = RegEx.get_movie('Ice Age (2001) (tt0268380)')
        assert result['title'] == 'Ice Age'
        assert result['year'] == '2001'
        assert result['imdbID'] == 'tt0268380'

        result = RegEx.get_movie('Ice Age (tt0268380)')
        assert result['title'] == 'Ice Age'
        assert result['year'] == ''
        assert result['imdbID'] == 'tt0268380'

        result = RegEx.get_movie('Ice Age (2001)')
        assert result['title'] == 'Ice Age'
        assert result['year'] == '2001'
        assert result['imdbID'] == ''

        result = RegEx.get_movie('Ice Age')
        assert result['title'] == 'Ice Age'
        assert result['year'] == ''
        assert result['imdbID'] == ''

        result = RegEx.get_movie('Ice   Age  ')
        assert result['title'] == 'Ice Age'
        assert result['year'] == ''
        assert result['imdbID'] == ''

        result = RegEx.get_movie('(I) Ice Age (CD1) (Bluray) (2001) (1080p) (HD) (DTS) (x264) (town.ag) (mkv) (7.1) (tt0268380)')
        assert result['title'] == 'Ice Age'
        assert result['year'] == '2001'
        assert result['imdbID'] == 'tt0268380'

        result = RegEx.get_movie('Hobbit, The')
        assert result['title'] == 'Hobbit, The'
        assert result['year'] == ''
        assert result['imdbID'] == ''

        result = RegEx.get_movie('(I) Hobbit, The (CD1) (Bluray) (2001) (1080p) (HD) (DTS) (x264) (town.ag) (mkv) (7.1) (tt0268380)')
        assert result['title'] == 'Hobbit, The'
        assert result['year'] == '2001'
        assert result['imdbID'] == 'tt0268380'

        result = RegEx.get_movie('Paranormal Investigations 3 - Toedliche Geister (2009)')
        assert result['title'] == 'Paranormal Investigations 3 - Toedliche Geister'
        assert result['year'] == '2009'
        assert result['imdbID'] == ''

        result = RegEx.get_movie('Ice Age (2001) [tt0268380]')
        assert result['title'] == 'Ice Age'
        assert result['year'] == '2001'
        assert result['imdbID'] == 'tt0268380'

        result = RegEx.get_movie('Ice Age [2001] [tt0268380]')
        assert result['title'] == 'Ice Age'
        assert result['year'] == '2001'
        assert result['imdbID'] == 'tt0268380'

        result = RegEx.get_movie('Ice Age [2001] (tt0268380)')
        assert result['title'] == 'Ice Age'
        assert result['year'] == '2001'
        assert result['imdbID'] == 'tt0268380'

    def test_get_episode(self):
        result = RegEx.get_episode('s01E5 S01e6 - some episode title')
        assert result[0]['season'] == '01'
        assert result[0]['episode'] == '5'
        assert result[1]['season'] == '01'
        assert result[1]['episode'] == '6'
        assert len(result) == 2

        result = RegEx.get_episode('episode.title.s01E5')
        assert result[0]['season'] == '01'
        assert result[0]['episode'] == '5'
        assert len(result) == 1

        result = RegEx.get_episode('S01E5.episode.title')
        assert result[0]['season'] == '01'
        assert result[0]['episode'] == '5'
        assert len(result) == 1

        result = RegEx.get_episode('S03.E05 S03_E06 S03-E07 - some episode title')
        assert result[0]['season'] == '03'
        assert result[0]['episode'] == '05'
        assert result[1]['season'] == '03'
        assert result[1]['episode'] == '06'
        assert result[2]['season'] == '03'
        assert result[2]['episode'] == '07'
        assert len(result) == 3

        result = RegEx.get_episode('S03E05 - some episode title')
        assert result[0]['season'] == '03'
        assert result[0]['episode'] == '05'
        assert len(result) == 1

        result = RegEx.get_episode('S03 E05 - some episode title')
        assert result[0]['season'] == '03'
        assert result[0]['episode'] == '05'
        assert len(result) == 1

        result = RegEx.get_episode('S03 E05 S03 E06 some episode title')
        assert result[0]['season'] == '03'
        assert result[0]['episode'] == '05'
        assert result[1]['season'] == '03'
        assert result[1]['episode'] == '06'
        assert len(result) == 2

        result = RegEx.get_episode('S04E02 some episode title')
        assert result[0]['season'] == '04'
        assert result[0]['episode'] == '02'
        assert len(result) == 1

        result = RegEx.get_episode('S00E00 some episode title')
        assert result[0]['season'] == '00'
        assert result[0]['episode'] == '00'
        assert len(result) == 1

        result = RegEx.get_episode('S1E2 some episode title')
        assert result[0]['season'] == '1'
        assert result[0]['episode'] == '2'
        assert len(result) == 1
        result = RegEx.get_episode('The Simpsons - S13E22 - some episode title')
        assert result[0]['season'] == '13'
        assert result[0]['episode'] == '22'
        assert len(result) == 1

        result = RegEx.get_episode('s03e05 - some episode title')
        assert result[0]['season'] == '03'
        assert result[0]['episode'] == '05'
        assert len(result) == 1

        result = RegEx.get_episode('S12345E67890 some episode title')
        assert len(result) == 0

        result = RegEx.get_episode('01x02 - some episode title')
        assert result[0]['season'] == '01'
        assert result[0]['episode'] == '02'
        assert len(result) == 1

        result = RegEx.get_episode('1x02 - some episode title')
        assert result[0]['season'] == '1'
        assert result[0]['episode'] == '02'
        assert len(result) == 1

        result = RegEx.get_episode('1x02 1x03- some episode title')
        assert result[0]['season'] == '1'
        assert result[0]['episode'] == '02'
        assert result[1]['season'] == '1'
        assert result[1]['episode'] == '03'
        assert len(result) == 2

        result = RegEx.get_episode('1x02 1X03 1x04 - some episode title')
        assert result[0]['season'] == '1'
        assert result[0]['episode'] == '02'
        assert result[1]['season'] == '1'
        assert result[1]['episode'] == '03'
        assert result[1]['season'] == '1'
        assert result[1]['episode'] == '03'
        assert len(result) == 3

        result = RegEx.get_episode('ep05ep06 - some episode title')
        assert result[0]['season'] == ''
        assert result[0]['episode'] == '05'
        assert result[1]['season'] == ''
        assert result[1]['episode'] == '06'
        assert len(result) == 2

        result = RegEx.get_episode('EP05 ep06 - some episode title')
        assert result[0]['season'] == ''
        assert result[0]['episode'] == '05'
        assert result[1]['season'] == ''
        assert result[1]['episode'] == '06'
        assert len(result) == 2

        result = RegEx.get_episode('eP_05 - some episode title')
        assert result[0]['season'] == ''
        assert result[0]['episode'] == '05'
        assert len(result) == 1