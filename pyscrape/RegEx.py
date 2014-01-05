def get_movie(title):
    import re, os

    def remove_brackets(title):
        from pyscrape import utils

        f = os.path.join(utils.get_root(), 'system', 'replace')
        chars = []
        for char in open(f).readlines():
            char = char.split(':')[0].strip()
            if char != '':
                chars.append(char)

        regex = '\([a-z A-Z 0-9 <>\\|\\\._\-/'
        for char in chars:
            regex += char
        regex += ']*\)'

        for match in re.findall(regex, title):
            title = title.replace(match,'')
        return title

    def remove_double_spaces(string):
        while '  ' in string:
            string = string.replace('  ', ' ')
        return string

    def get_year(title):
        rx = re.search('\([0-9+]{4}\)', title)
        year = ''
        if rx:
            year = rx.group()
        return year.replace('(', '').replace(')', '')

    def get_imdb_id(title):
        rx = re.search('\(tt[0-9]{7}\)', title)
        imdb_id = ''
        if rx:
            imdb_id = rx.group()
        return imdb_id.replace('(', '').replace(')', '')


    year = get_year(title)
    imdb_id = get_imdb_id(title)

    _title = remove_brackets(title).strip()
    _title = remove_double_spaces(_title)

    result = {'title': _title, 'year': year, 'imdbID': imdb_id}
    return result