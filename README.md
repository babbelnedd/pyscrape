1. README
=========
PyScrape collects information and media artwork for movies
 - Create NFO files
 - Download artwork from TheMovieDB.org / Fanart.tv
 - Delete unwanted audio-tracks from matroska files


2. SETUP
=========
 - Install pip  
 - Install mkvtoolnix  
 - Install mediainfo  
 - Run setup.py  
  
  
  
3. REQUIREMENTS
=========
pip                             http://www.pip-installer.org/en/latest/installing.html  
termcolor                       installed by setup.py  
  
mkvtoolnix                      http://www.bunkus.org/videotools/mkvtoolnix/downloads.html  
mediainfo                       http://mediaarea.net/de/MediaInfo/Download  
  
  
  
4. CLI
=========
**-p** Ignore Path from config and scrape a single movie dir  
**-r** Don't delete exisiting files, refresh NFO and download *new* images  
**-u** Clean and update XBMC library
