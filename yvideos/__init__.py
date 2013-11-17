# -*- coding: utf-8 -*-

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from .models import (
    Base,
    DBSession
)


def add_routes(config):
    config.add_route('home', '/')
    config.add_route(u'api_series_list', u'/api/series')
    config.add_route(u'api_series',
                     u'/api/series/{series_id}')

    config.add_route(u'api_objects', u'/api/objects')
    config.add_route(u'api_object', u'/api/objects/{object_id}')

    config.add_route(u'api_videos', u'/api/videos')
    config.add_route(u'api_video', u'/api/videos/{video_id}')

    config.add_route(u'api_tags', u'/api/tags')
    config.add_route(u'api_tag', u'/api/tags/{tag_id}')

    config.add_route(u'api_s3_buckets', u'/api/s3/buckets')
    config.add_route(u'api_s3_bucket', u'/api/s3/buckets/{bucket_id}')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    # SQLAlchemy
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # Session Factory
    session_factory = UnencryptedCookieSessionFactoryConfig(u'session_secret')

    config = Configurator(settings=settings, session_factory=session_factory)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    add_routes(config)
    config.scan()
    return config.make_wsgi_app()
