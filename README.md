# README
  **README IS NOT UP TO DATE**
 PyScrape is a cross platform aplication that collects information and media artwork for movies in XBMC format  
   Create NFO files
   Download artwork from TheMovieDB.org / Fanart.tv
   Delete unwanted audio-tracks from matroska files
 
 
## SETUP / REQUIREMENTS  
   Install [python 2.7.6](http://python.org/download/releases/2.7.6/ "python 2.7.6")
   Install [mkvtoolnix](http://www.bunkus.org/videotools/mkvtoolnix/downloads.html "mkvtoolnix")
   Install [mediainfo](http://mediaarea.net/de/MediaInfo/Download "mediainfo") (CLI)   
   Copy pyscrape.cfg.example to pyscrape.cfg and set it up (explanation will follow..)
   
   
 
## RESTRICTION / FOLDER NAME  
 A movie file **have to be** in a folder  
 The name of the folder has some conditions that must be met  
 Name (Year) (imdbID); example: Ice Age (2001) (tt0268380)  
 
 The order of year and imdb id do not matter
 Neither year nor imdb id are necessary
 Values can be in parentheses `(` `)` or in square brackets `[` `]`  
 **But it is highly recommend to use one of both** (id is better than year)  
   
 The name of the movie file do not matter  
 
 
 
## USAGE  
 **Scrape a single movie**  
 python MovieScraper.py -p "c:\movies\Ice Age (2002)"  
 python MovieScraper.py -p "/media/movies/Ice Age (2002)"  
   
 **Scrape all movies of a folder**
 Set the path(s) of your movies in *pyscrape.cfg*  
 python MovieScraper.py  [--r, -u, -f, -nfo-only]
 
 
## CLI
 **-p path** Ignore 'paths' from config and scrape a single movie dir  
 **--r**     Don't delete existing files, refresh NFO and download *new* images  
 **--u**     Clean and update XBMC library  
 **--f**     Forces to scrape a folder  even is there no movie file  
 **--r**     Refresh  only download new images  
 **--nfo-only** Only create a .nfo file (can be combined with -f and -r)  
 **--d --delete-existing** Will delete all files that aren't a movie / subtitle file. You can add file extensions to [this](https://github.com/SchadLucas/pyscrape/blob/master/pyscrape/system/extensions "extensions") file to keep specific files