def get_movie(title):
    import re

    def get_year(title):
        rx = re.search('\([0-9+]{4}\)', title)
        year = ''
        if rx:
            year = rx.group()
        return year

    def get_imdb_id(title):
        rx = re.search('\(tt[0-9]{7}\)', title)
        imdb_id = ''
        if rx:
            imdb_id = rx.group()
        return imdb_id


    year = get_year(title)
    imdb_id = get_imdb_id(title)

    _title = title.replace(year, '').replace(imdb_id, '').strip()
    while '  ' in _title:
        _title = _title.replace('  ', ' ')

    year = year.replace('(', '').replace(')', '')
    imdb_id = imdb_id.replace('(', '').replace(')', '')

    result = {'title': _title, 'year': year, 'imdbID': imdb_id}
    return result