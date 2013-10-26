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

from .exceptions import (
    CollectionNotFound,
    VideoNotFound
)

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
    name = Column(Unicode(20), nullable=False, unique=True)
    collections = relationship(Collection, secondary=tag_collection_assoc)
    videos = relationship(Video, secondary=tag_video_assoc)

    def __init__(self, name):
        assert isinstance(name, unicode)

        self.id = unicode(uuid.uuid4())
        self.name = name


class S3Rogics(object):

    def add_bucket(self, region, name):
        b = S3Bucket(region, name)
        DBSession.add(b)

        return b


class VideoRogics(object):

    def create(self, title):
        v = Video(title)
        DBSession.add(v)

        return v

    def add_object(self, video, s3_bucket, s3_key, size_no):
        assert isinstance(video, Video)
        assert isinstance(s3_bucket, S3Bucket)
        assert isinstance(s3_key, unicode)
        assert isinstance(size_no, int)

        _object = Object(video, s3_bucket, s3_key, size_no)
        DBSession.add(_object)
        return True

    def get_by_id(self, video_id):
        video = DBSession.query(
            Video
        ).filter(
            Video.id == video_id
        ).first()

        if video is None:
            raise VideoNotFound
        return video


class CollectionRogics(object):

    def create(self, title):
        assert isinstance(title, unicode)

        c = Collection(title)
        DBSession.add(c)
        return c

    def get_by_id(self, collection_id):
        collection = DBSession.query(
            Collection
        ).filter(
            Collection.id == collection_id
        ).first()

        if collection is None:
            raise CollectionNotFound()
        return collection

    def add_video(self, collection, video, sequence):
        assert isinstance(collection, Collection)
        assert isinstance(video, Video)
        assert isinstance(sequence, int)
        assert len(collection.videos) + 1 >= sequence > -1

        if 0 < sequence <= len(collection.videos):
            collection.videos.insert(sequence - 1, video)
        else:
            collection.videos.append(video)
        return True


class TagRogics(object):

    def get_or_create(self, name):
        assert isinstance(name, unicode)

        tag = DBSession.query(
            Tag
        ).filter(
            Tag.name == name
        ).first()

        if tag is None:
            tag = Tag(name)
            DBSession.add(tag)

        return tag

    def add_video(self, tag, video):
        assert isinstance(tag, Tag)
        assert isinstance(video, Video)

        if video in tag.videos:
            return False

        tag.videos.append(video)
        return True

    def add_collection(self, tag, collection):
        assert isinstance(tag, Tag)
        assert isinstance(collection, Collection)

        if collection in tag.collections:
            return False

        tag.collections.append(collection)
        return True
