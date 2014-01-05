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