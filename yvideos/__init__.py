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
