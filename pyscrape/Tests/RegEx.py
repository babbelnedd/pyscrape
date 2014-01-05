from pyscrape import RegEx

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
