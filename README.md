#README
PyScrape is a cross platform aaplication that collects information and media artwork for movies  
 - Create NFO files
 - Download artwork from TheMovieDB.org / Fanart.tv
 - Delete unwanted audio-tracks from matroska files


##SETUP / REQUIREMENTS
 - Install [pip](http://www.pip-installer.org/en/latest/installing.html "pip")    
 - Install [mkvtoolnix](http://www.bunkus.org/videotools/mkvtoolnix/downloads.html "mkvtoolnix")    
 - Install [mediainfo](http://mediaarea.net/de/MediaInfo/Download "mediainfo") (CLI)   
 - Run setup.py  
 - Copy pyscrape.cfg.example to pyscrape.cfg and set it up (explanation will follow..)
  
  

##RESTRICTION
A movie have to be in a folder  
Folder layout: Name (Year); example: Ice Age (2001)  



##USAGE
**Scrape a single movie**  
python MovieScraper.py -p "c:\movies\Ice Age (2001)"  
python MovieScraper.py -p "/media/movies/Ice Age (2001)"  
  
**Scrape all movies of a folder**
Set the path(s) of your movies in *pyscrape.cfg*  
python MovieScraper.py  


##CLI
**-p** Ignore Path from config and scrape a single movie dir  
**--r** Don't delete exisiting files, refresh NFO and download *new* images  
**--u** Clean and update XBMC library  
