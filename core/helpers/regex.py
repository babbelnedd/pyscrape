from datetime import date
import re
import os

from core.helpers.decorator import Cached


@Cached
def get_cd(string):
    regex = re.search('\cd[0-9]', string, re.IGNORECASE)

    if regex:
        _cd = regex.group().replace('(', '').replace(')', '')
    else:
        _cd = ''

    _cd = _cd.lower().replace('cd', '').strip()

    return _cd


@Cached
def get_movie(title):
    def remove_brackets(string):
        string = re.sub(r"\([^)]*\)", "", string)
        string = re.sub(r"\[[^)]*\]", "", string)
        return string

    def remove_double_spaces(string):
        while '  ' in string:
            string = string.replace('  ', ' ')
        return string

    def remove_dots(string):
        return string.replace('.', ' ')

    def remove_year(string):
        rx = re.search('[0-9+]{4}', string)
        if rx and 1889 < int(rx.group()) < date.today().year + 2:
            string = string.replace(rx.group(), '')

        return string

    def get_year(string):
        expressions = [re.search('\([0-9]{4}\)', string),
                       re.search('\[[0-9]{4}\]', string),
                       re.search(' [0-9]{4} ', string),
                       re.search(' [0-9]{4}', string),
                       re.search('.[0-9]{4}.', string),
                       re.search('.[0-9]{4}', string),
                       re.search('^(?!a-Z0-9|\\.).[0-9]{4}', string)]

        _year = ''
        for rx in expressions:
            if rx is not None:
                rx_result = rx.group().replace('(', '').replace(')', '')
                rx_result = rx_result.replace('[', '').replace(']', '')
                rx_result = rx_result.replace('.', '')
                rx_result = rx_result.replace(' ', '')

                if rx_result.isdigit() and 1889 < int(rx_result) < date.today().year + 1:
                    _year = rx_result
                    break

        return _year

    def get_imdb_id(string):
        rx_parentheses = re.search('\(tt[0-9]{7}\)', string)
        rx_square_brackets = re.search('\[tt[0-9]{7}\]', string)
        rx_square_dots = re.search('.tt[0-9]{7}.', string)

        imdb = ''
        if rx_parentheses:
            imdb = rx_parentheses.group().replace('(', '').replace(')', '')
        elif rx_square_brackets:
            imdb = rx_square_brackets.group().replace('[', '').replace(']', '')
        elif rx_square_dots:
            imdb = rx_square_dots.group().replace('.', '')

        return imdb

    year = get_year(title)
    imdb_id = get_imdb_id(title)

    title = os.path.basename(os.path.normpath(title))
    _title = remove_brackets(title)
    _title = remove_year(_title)
    _title = remove_dots(_title)
    _title = remove_double_spaces(_title)

    if _title == '.':
        _title = ''

    result = {'title': _title.strip(), 'year': year.strip(), 'imdbID': imdb_id.strip()}
    return result


@Cached
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