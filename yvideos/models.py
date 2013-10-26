# -*- coding: utf-8 -*-

import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Table,
    Unicode
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    backref,
    relationship,
    scoped_session,
    sessionmaker
)
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class S3Bucket(Base):
    __tablename__ = u's3_buckets'

    id = Column(Unicode(36), primary_key=True)
    region = Column(Unicode(36), nullable=False)
    name = Column(Unicode(255), nullable=False)

    def __init__(self, region, name):
        assert isinstance(region, unicode)
        assert isinstance(name, unicode)

        self.id = unicode(uuid.uuid4())
        self.region = region
        self.name = name


class Video(Base):
    __tablename__ = u'videos'

    id = Column(Unicode(36), primary_key=True)
    title = Column(Unicode(255), nullable=False)

    def __init__(self, title):
        assert isinstance(title, unicode)

        self.id = unicode(uuid.uuid4())
        self.title = title


class Object(Base):
    __tablename__ = u'objects'

    id = Column(Unicode(36), primary_key=True)
    video_id = Column(Unicode(36), ForeignKey(Video.id), nullable=False)
    video = relationship(Video, backref=backref(u'objects'))
    s3_bucket_id = Column(Unicode(36), ForeignKey(S3Bucket.id), nullable=False)
    s3_bucket = relationship(S3Bucket, backref=backref(u'videos'))
    s3_key = Column(Unicode(255), nullable=False, unique=True)
    size_no = Column(Integer(), nullable=False)

    def __init__(self, video, s3_bucket, s3_key, size_no):
        assert isinstance(video, Video)
        assert isinstance(s3_bucket, S3Bucket)
        assert isinstance(s3_key, unicode)
        assert isinstance(size_no, int)

        self.id = unicode(uuid.uuid4())
        self.video = video
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.size_no = size_no


collection_video_assoc = Table(
    'collection_video_assoc', Base.metadata,
    Column('collection_id', Unicode(36), ForeignKey('collections.id')),
    Column('video_id', Unicode(36), ForeignKey('videos.id'))
)


class Collection(Base):
    __tablename__ = u'collections'

    id = Column(Unicode(36), primary_key=True)
    title = Column(Unicode(36), primary_key=True)
    videos = relationship(Video, secondary=collection_video_assoc)

    def __init__(self, title):
        assert isinstance(title, unicode)

        self.id = unicode(uuid.uuid4())
        self.title = title


tag_video_assoc = Table(
    'tag_video_assoc', Base.metadata,
    Column('tag_id', Unicode(36), ForeignKey('tags.id')),
    Column('video_id', Unicode(36), ForeignKey('videos.id'))
)


tag_collection_assoc = Table(
    'tag_collection_assoc', Base.metadata,
    Column('tag_id', Unicode(36), ForeignKey('tags.id')),
    Column('collection_id', Unicode(36), ForeignKey('collections.id'))
)


class Tag(Base):
    __tablename__ = u'tags'

    id = Column(Unicode(36), primary_key=True)
    tag = Column(Unicode(20), nullable=False, unique=True)
    collections = relationship(Collection, secondary=tag_collection_assoc)
    videos = relationship(Video, secondary=tag_video_assoc)

    def __init__(self, tag):
        assert isinstance(tag, unicode)

        self.id = unicode(uuid.uuid4())
        self.tag = tag
