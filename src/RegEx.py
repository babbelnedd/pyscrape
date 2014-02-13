import re


def get_cd(string):
    regex = re.search('\cd[0-9]', string, re.IGNORECASE)

    if regex:
        _cd = regex.group().replace('(', '').replace(')', '')
    else:
        _cd = ''

    _cd = _cd.lower().replace('cd', '').strip()

    return _cd


def get_movie(title):
    def remove_brackets(string):
        string = re.sub(r"\([^)]*\)", "", string)
        string = re.sub(r"\[[^)]*\]", "", string)
        return string

    def remove_double_spaces(string):
        while '  ' in string:
            string = string.replace('  ', ' ')
        return string

    def get_year(string):
        rx_parentheses = re.search('\([0-9+]{4}\)', string)
        rx_square_brackets = re.search('\[[0-9+]{4}\]', string)

        year = ''
        if rx_parentheses:
            year = rx_parentheses.group().replace('(', '').replace(')', '')
        elif rx_square_brackets:
            year = rx_square_brackets.group().replace('[', '').replace(']', '')

        return year

    def get_imdb_id(string):
        rx_parentheses = re.search('\(tt[0-9]{7}\)', string)
        rx_square_brackets = re.search('\[tt[0-9]{7}\]', string)

        imdb = ''
        if rx_parentheses:
            imdb = rx_parentheses.group().replace('(', '').replace(')', '')
        elif rx_square_brackets:
            imdb = rx_square_brackets.group().replace('[', '').replace(']', '')

        return imdb

    year = get_year(title)
    imdb_id = get_imdb_id(title)

    _title = remove_brackets(title).strip()
    _title = remove_double_spaces(_title)

    result = {'title': _title, 'year': year, 'imdbID': imdb_id}
    return result


def get_episode(title):
    orig_title = title
    title = title.upper()  # makes it easier to split matches
    regex_schema1 = re.findall('S[0-9]{1,3}E[0-9]{1,3}', title, re.IGNORECASE)
    regex_schema2 = re.findall('S[0-9]{1,3} E[0-9]{1,3}', title, re.IGNORECASE)
    regex_schema3 = re.findall('[0-9]{1,3}X[0-9]{1,3}', title, re.IGNORECASE)
    regex_schema4 = re.findall('EP[0-9]{1,3}', title, re.IGNORECASE)
    regex_schema5 = re.findall('EP_[0-9]{1,3}', title, re.IGNORECASE)

    regex_schema6 = re.findall('S[0-9+]{1,3}[._\-]E[0-9+]{1,3}', title, re.IGNORECASE)
    results = []

    if regex_schema1:
        for match in regex_schema1:
            match = match.split('E')
            season = match[0].replace('S', '')
            episode = match[1]
            results.append({'season': season, 'episode': episode, 'filename': orig_title})
    elif regex_schema2:
        for match in regex_schema2:
            match = match.split('E')
            season = match[0].replace('S', '').strip()
            episode = match[1].strip()
            results.append({'season': season, 'episode': episode, 'filename': orig_title})
    elif regex_schema3:
        for match in regex_schema3:
            match = match.split('X')
            season = match[0]
            episode = match[1]
            results.append({'season': season, 'episode': episode, 'filename': orig_title})
    elif regex_schema4:
        for match in regex_schema4:
            season = ''
            episode = match.replace('EP', '')
            results.append({'season': season, 'episode': episode, 'filename': orig_title})
    elif regex_schema5:
        for match in regex_schema5:
            season = ''
            episode = match.replace('EP_', '')
            results.append({'season': season, 'episode': episode, 'filename': orig_title})
    elif regex_schema6:
        for match in regex_schema6:
            match = match.split('E')
            season = match[0].replace('S', '').replace('S', '').replace('.', '').replace('-', '').replace('_', '')
            episode = match[1].strip()
            results.append({'season': season, 'episode': episode, 'filename': orig_title})

    return results