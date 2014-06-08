# !/usr/bin/python2.7
import os
from time import sleep
from sqlalchemy import create_engine, Column, Integer, String, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.helpers import utils
import core.moviescraper as MovieScraper
from core.helpers.regex import get_episode
from core.moviescraper import get_movies, scrape_movies


Base = declarative_base()


class Video(Base):
    __tablename__ = 'video'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    path = Column(String)
    file = Column(String)
    timestamp = Column(Float)
    filesize = Column(Integer)


Session = sessionmaker()
# todo: fix path to absolute
engine = create_engine('sqlite:///pyscrape.db', echo=False, convert_unicode=True)
Session.configure(bind=engine)
session = Session()
Base.metadata.create_all(engine)


def wait_for_file(video_file):
    fs = os.path.getsize(video_file)

    while True:
        print '.',
        sleep(5)

        nfs = os.path.getsize(video_file)
        if fs != nfs:
            fs = nfs
            continue
        else:
            break


def scrape_new_movies(path):
    # delete all not up-to-date videos
    for instance in session.query(Video).filter(Video.path.like('/media/share/filme/%')).order_by(Video.id):
        video_file = os.path.join(instance.path, instance.file)

        if not os.path.exists(instance.path) \
                or not os.path.exists(video_file) \
                or not os.path.getmtime(video_file) == instance.timestamp \
                or not os.path.getsize(video_file) == instance.filesize:
            print "DELETE", instance.path
            session.delete(instance)
            session.commit()
            continue


    # scan all *movies*
    # todo: "for path in config.movie.paths"
    for movie in get_movies(path):
        if len(movie.files) == 0:
            continue

        video_file = os.path.join(movie.path, movie.files[0])
        timestamp = os.path.getmtime(video_file)
        filesize = os.path.getsize(video_file)
        m = Video(path=movie.path.decode('ascii', 'ignore'), file=movie.files[0], timestamp=timestamp,
                  filesize=filesize)
        exists = session.query(func.count(Video.id)).filter(Video.path == m.path and Video.file == m.file and
                                                            Video.timestamp == m.timestamp and
                                                            Video.filesize == m.filesize).scalar() > 0
        if not exists:
            # try:
            MovieScraper.delete_existing = False
            MovieScraper.nfo_only = False
            MovieScraper.force = False
            MovieScraper.refresh = True

            wait_for_file(video_file)

            scrape_movies(m.path, single=True)
            scraped = True
            # except Exception as exc:
            #     print "Fehlgeschlagen", m.path
            #     print exc
            #     print exc.message
            #     scraped = False

            if scraped:
                m.filesize = os.path.getsize(video_file)
                session.add(m)
                session.commit()


def scrape_new_episodes(path):
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if os.path.splitext(filename)[1] in utils.get_movie_extensions() and get_episode(filename) != []:
                video_file = os.path.join(root, filename)
                fs = os.path.getsize(video_file)
                ts = os.path.getmtime(video_file)
                fn = filename.decode('utf8')
                exists = session.query(func.count(Video.id)).filter(Video.path == root, Video.file == fn,
                                                                    Video.filesize == fs,
                                                                    Video.timestamp == ts).scalar() > 0
                if not exists:
                    #wait_for_file(video_file)

                    try:
                        from core.tvscraper import scrape_episode
                        import core.tvscraper as TvScraper

                        TvScraper.delete_existing = True
                        print video_file
                        scrape_episode(video_file)
                        scraped = True
                    except Exception as exc:
                        print "Fehlgeschlagen"
                        print exc
                        print exc.message
                        scraped = False

                    if scraped:
                        ts = os.path.getmtime(video_file)
                        fs = os.path.getsize(video_file)
                        e = Video(path=root, file=fn, timestamp=ts, filesize=fs)
                        session.add(e)
                        session.commit()


while True:
    print 'Scrape new movies'
    scrape_new_movies('/media/lsc/nas/drive4/movies')
    # print 'Scrape new episodes'
    # try:
    #     scrape_new_episodes('/media/drive4/shows/')
    #     scrape_new_episodes('/media/drive3/shows/')
    #     scrape_new_episodes('/media/drive2/Serien/')
    #     scrape_new_episodes('/media/drive1/Serien/')
    # except Exception as e:
    #     print e
    print 'Sleep 3600seconds'
    sleep(3600)
