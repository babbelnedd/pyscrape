try:
    #region Imports

    import sys
    from core.TerminalColor import print_colored, Foreground

    #endregion

    #region Private Methods

    def ask(question, answer=True):
        r"""
        Asks the user a question to answer by console input
        Output:     [question] yes/no

        Keyword arguments:
        @param question:   The question which will be asked
        @param answer:     True means 'YES' is the default answer
                    False means 'NO' is the default answer
                    default value: True

        Examples:
        >>> q = ask('Do you want to read the docstring?')
        Do you want to read the docstring? YES/no
        yes
        >>> q
        True

        >>> q = ask('Do you want to read the docstring?', default:False)
        Do you want to read the docstring? yes/NO
        yes
        >>> q
        True
        ...
        """
        if answer:
            result = raw_input(question + 'YES/no\n')
        else:
            result = raw_input(question + 'yes/NO\n')

        if answer:
            return 'y' in result.lower() or result == ''
        else:
            return 'y' in result.lower() and result != ''

    #endregion

    #region Intro

    print 'Welcome to PyScrape 1.0'
    print '======================='
    print 'This installation will guide you ......\n'

    #endregion

    #region Dependencies

    print 'Checking the dependencies...'

    try:
        import lxml
    except ImportError:
        print_colored('You need following packages:', Foreground.Red)
        print 'lxml v3.3.1 >'
        sys.exit()

    print 'Congratulations.. all dependencies are available\n\n'

    #endregion

    #region Initial Configuration

    configuration = {'primary_language': raw_input('primary language? (ISO639-1):\nCode: '),
                     'fallback_language': raw_input('fallback language? (ISO639-1):\nCode: '),
                     'country_code': raw_input('country for certifications (MPAA)? (ISO639-2):\nCode: '), }

    #endregion

    #region Movie Configuration

    print '\n\nMovie configuration...'
    print '======================='

    # set paths

    movie_image_types = {}
    movie_input = raw_input('Do you want to download all available images?\n').lower()
    if 'y' in movie_input or movie_input == '':
        download_all_images = True
        movie_image_types = {'banner': True, 'extrafanart': True, 'poster': True,
                             'landscape': True, 'thumbs': True, 'extrathumbs': True,
                             'logo': True, 'disc': True, 'clearart': True}

    if movie_image_types == {}:
        print 'Do you want to download .. '
        movie_image_types['banner'] = ask('.. banner?:')
        movie_image_types['backdrop'] = ask('.. backdrops?:')

        if movie_image_types['backdrop']:
            movie_image_types['extrafanart'] = ask('.. extra fanart?')
        else:
            movie_image_types['extrafanart'] = False

        movie_image_types['poster'] = ask('.. poster?')
        movie_image_types['landscape'] = ask('.. landscapes?')

        if movie_image_types['landscape']:
            movie_image_types['thumbs'] = ask('.. thumbs?')
        else:
            movie_image_types['thumbs'] = False

        if movie_image_types['thumbs']:
            movie_image_types['extrathumbs'] = '.. extra thumbs?'
        else:
            movie_image_types['extrathumbs'] = False

        movie_image_types['logo'] = ask('.. logos?')
        movie_image_types['disc'] = ask('.. discs?')
        movie_image_types['clearart'] = ask('.. clearart?')

    configuration['movie_image_types'] = movie_image_types

    #endregion

    #region Show Configuration

    # set paths
    # set screenshot time

    #endregion

    #region Music Configuration

    #endregion

    #region 3rd Party Tools

    # set mediainfo path
    # set ffmpeg path
    # set mkvmerge path

    # test paths

    #endregion

    #region XBMC Configuration
    if ask('Do you want to set up XBMC synchronisation?', answer=False):
        pass
        # set protocol
        # set ip
        # set port
        # set user
        # set password

        # test configuration
    #endregion

    #region Extra Configuration

    if ask('Do you want to set up professional settings?', False):
        ask('Set up TMDB API Key?', answer=False)
        ask('Set up TMDB url base?', answer=False)
        ask('Set up Fanart.tv API Key?', answer=False)
        ask('Set up TVDB API Key?', answer=False)

    #endregion

    #region End

    print '\n\n', configuration
    print 'Configuration file saved in ...'  # in ~/.pyscrape ?

    #endregion

except KeyboardInterrupt:
    print_colored('\n\nInstallation canceled', Foreground.Red)
    sys.exit()