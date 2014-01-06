def get_movie(title):
    import re

    def remove_brackets(title):
        title = re.sub(r"\([^)]*\)", "", title)
        title = re.sub(r"\[[^)]*\]", "", title)
        return title

    def remove_double_spaces(string):
        while '  ' in string:
            string = string.replace('  ', ' ')
        return string

    def get_year(title):
        rx_parentheses = re.search('\([0-9+]{4}\)', title)
        rx_square_brackets = re.search('\[[0-9+]{4}\]', title)

        year = ''
        if rx_parentheses:
            year = rx_parentheses.group().replace('(', '').replace(')', '')
        elif rx_square_brackets:
            year = rx_square_brackets.group().replace('[', '').replace(']', '')

        return year

    def get_imdb_id(title):
        rx_parentheses = re.search('\(tt[0-9]{7}\)', title)
        rx_square_brackets = re.search('\[tt[0-9]{7}\]', title)

        imdb_id = ''
        if rx_parentheses:
            imdb_id = rx_parentheses.group().replace('(', '').replace(')', '')
        elif rx_square_brackets:
            imdb_id = rx_square_brackets.group().replace('[', '').replace(']', '')

        return imdb_id


    year = get_year(title)
    imdb_id = get_imdb_id(title)

    _title = remove_brackets(title).strip()
    _title = remove_double_spaces(_title)

    result = {'title': _title, 'year': year, 'imdbID': imdb_id}
    return result