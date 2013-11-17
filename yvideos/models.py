# -*- coding: utf-8 -*-

import random
import time
import uuid

import boto
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Table,
    Unicode,
    UnicodeText
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import (
    backref,
    relationship,
    scoped_session,
    sessionmaker
)
from zope.sqlalchemy import ZopeTransactionExtension

from .exceptions import (
    BucketNotFound,
    SeriesNotFound,
    KeyPairNotFound,
    ObjectNotFound,
    SignerNotFound,
    TagNotFound,
    VideoNotFound
)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class S3Bucket(Base):
    __tablename__ = u's3_buckets'

    id = Column(Unicode(36), primary_key=True)
    region = Column(Unicode(36), nullable=False)
    name = Column(Unicode(255), nullable=False)
    distribution_id = Column(Unicode(255), nullable=False)
    origin = Column(Unicode(255), nullable=False)

    def __init__(self, region, name):
        assert isinstance(region, unicode)
        assert isinstance(name, unicode)

        self.id = unicode(uuid.uuid4())
        self.region = region
        self.name = name

    def set_distribution_id(self, distribution_id):
        assert isinstance(distribution_id, unicode)

        self.distribution_id = distribution_id
        return True

    def set_origin(self, origin):
        assert isinstance(origin, unicode)

        self.origin = origin
        return True

    def __json__(self, request):
        return {
            u'id': self.id,
            u'region': self.region,
            u'name': self.name,
        }


class KeyPair(Base):
    __tablename__ = u'cloudfront_keypairs'

    id = Column(Unicode(20), primary_key=True)
    private = Column(UnicodeText(), nullable=False)

    def __init__(self, id, private):
        assert isinstance(id, unicode)
        assert isinstance(private, unicode)

        self.id = id
        self.private = private


class Series(Base):
    __tablename__ = u'series'

    id = Column(Unicode(36), primary_key=True)
    title = Column(Unicode(36), primary_key=True)

    videos = relationship('Video', order_by='Video.position',
                          collection_class=ordering_list('position'))

    def __init__(self, title):
        assert isinstance(title, unicode)

        self.id = unicode(uuid.uuid4())
        self.title = title

    def set_title(self, title):
        assert isinstance(title, unicode)
        self.title = title

    def set_videos(self, videos):
        assert isinstance(videos, list)

        self.videos = self.videos[0:0]
        for video in videos:
            assert isinstance(video, Video)
            self.videos.append(video)

    def add_video(self, video, position):
        assert isinstance(video, Video)
        assert isinstance(position, int) and position >= 0

        if position == 0 or len(self.videos) > position:
            self.videos.append(video)
        else:
            self.videos.insert(position - 1, video)

    def __json__(self, request):
        return {
            u'id': self.id,
            u'title': self.title,
            u'videos': list(self.videos)
        }


class Video(Base):
    __tablename__ = u'videos'

    id = Column(Unicode(36), primary_key=True)
    title = Column(Unicode(255), nullable=False)
    series_id = Column(Unicode(36), ForeignKey(Series.id), nullable=False)
    position = Column(Integer(), nullable=False)
    objects = relationship('Object', backref=backref(u'video'), uselist=True)

    def __init__(self, title):
        assert isinstance(title, unicode)

        self.id = unicode(uuid.uuid4())
        self.title = title

        self.series_id = ''
        self.position = 0

    def add_object(self, object_):
        self.objects.append(object_)

    def __json__(self, request):
        return {
            u'id': self.id,
            u'title': self.title,
            u'objects': list(self.objects)
        }


class Object(Base):
    __tablename__ = u'objects'

    id = Column(Unicode(36), primary_key=True)
    video_id = Column(Unicode(36), ForeignKey(Video.id), nullable=False)
    s3_bucket_id = Column(Unicode(36), ForeignKey(S3Bucket.id), nullable=False)
    s3_key = Column(Unicode(255), nullable=False, unique=True)
    version = Column(Unicode(255), nullable=False)

    s3_bucket = relationship(S3Bucket, backref=backref(u'objects'))

    def __init__(self, s3_bucket, s3_key, version):
        assert isinstance(s3_bucket, S3Bucket)
        assert isinstance(s3_key, unicode)
        assert isinstance(version, unicode)

        self.id = unicode(uuid.uuid4())
        self.video_id = u''
        self.s3_bucket_id = s3_bucket.id
        self.s3_key = s3_key
        self.version = version

        self.s3_bucket = s3_bucket

    def __json__(self, request):
        return {
            u'id': self.id,
            u's3_bucket': self.s3_bucket,
            u's3_key': self.s3_key,
            u'version': self.version
        }


tag_video_assoc = Table(
    'tag_video_assoc', Base.metadata,
    Column('tag_id', Unicode(36), ForeignKey('tags.id'), nullable=False),
    Column('video_id', Unicode(36), ForeignKey('videos.id'), nullable=False)
)


tag_series_assoc = Table(
    'tag_series_assoc', Base.metadata,
    Column('tag_id', Unicode(36), ForeignKey('tags.id'), nullable=False),
    Column('series_id', Unicode(36), ForeignKey('series.id'), nullable=False)
)


class Tag(Base):
    __tablename__ = u'tags'

    id = Column(Unicode(36), primary_key=True)
    name = Column(Unicode(20), nullable=False, unique=True)

    seriess = relationship(Series, secondary=tag_series_assoc)
    videos = relationship(Video, secondary=tag_video_assoc)

    def __init__(self, name):
        assert isinstance(name, unicode)

        self.id = unicode(uuid.uuid4())
        self.name = name

    def __json__(self, reqeust):
        return {
            u'id': self.id,
            u'name': self.name,
            u'series': self.series,
            u'videos': self.videos
        }


class S3Rogics(object):

    def add_bucket(self, region, name):
        b = S3Bucket(region, name)
        DBSession.add(b)

        return b

    def get_all_buckets(self):
        buckets = DBSession.query(
            S3Bucket
        ).all()

        return list(buckets)

    def get_bucket_by_id(self, bucket_id):
        bucket = DBSession.query(
            S3Bucket
        ).filter(
            S3Bucket.id == bucket_id
        ).first()

        if bucket is None:
            raise BucketNotFound()
        return bucket

    def generate_url(self, _object):
        assert isinstance(_object, Object)

        bucket = _object.s3_bucket
        resource = u'%s%s' % (
            bucket.origin,
            _object.s3_key
        )

        conn = boto.connect_cloudfront()
        dist = conn.get_distribution_info(bucket.distribution_id)
        signers = filter(lambda signer: signer.id == u'Self',
                         dist.active_signers)
        if len(signers) < 1:
            raise SignerNotFound()

        key_pair = random.choice(filter(
            lambda key_pair: key_pair is not None,
            [
                self._get_key_pair_by_id(key_pair_id, False)
                for key_pair_id in signers[0].key_pair_ids
            ]
        ))
        signed_url = dist.create_signed_url(
            resource,
            key_pair.id,
            expire_time=int(time.time() + 60 * 60 * 6),  # 6hours
            private_key_string=key_pair.private
        )
        return signed_url

    def _get_key_pair_by_id(self, key_pair_id, raise_exception=True):
        key_pair = DBSession.query(
            KeyPair
        ).filter(
            KeyPair.id == key_pair_id
        ).first()

        if key_pair is None and raise_exception:
            raise KeyPairNotFound()

        return key_pair


class ObjectRogics(object):

    def get_all(self):

        objects = DBSession.query(
            Object
        ).all()

        return list(objects)

    def get_by_id(self, object_id):
        assert isinstance(object_id, unicode)

        _object = DBSession.query(
            Object
        ).filter(
            Object.id == object_id
        ).first()

        if _object is None:
            raise ObjectNotFound()
        return _object


class VideoRogics(object):

    def create(self, title):
        v = Video(title)
        DBSession.add(v)

        return v

    def add_object(self, video, _object):
        assert isinstance(video, Video)
        assert isinstance(_object, Object)

        _object.set_video(video)
        return True

    def get_all(self):
        videos = DBSession.query(
            Video
        ).order_by(
            Video.title
        ).all()

        return list(videos)

    def get_by_id(self, video_id):
        video = DBSession.query(
            Video
        ).filter(
            Video.id == video_id
        ).first()

        if video is None:
            raise VideoNotFound
        return video


class SeriesRogics(object):

    def create(self, title):
        assert isinstance(title, unicode)

        c = Series(title)
        DBSession.add(c)
        return c

    def get_all(self):
        series = DBSession.query(
            Series
        ).order_by(
            Series.title
        ).all()

        return list(series)

    def get_by_id(self, series_id):
        series = DBSession.query(
            Series
        ).filter(
            Series.id == series_id
        ).first()

        if series is None:
            raise SeriesNotFound()
        return series

    def add_video(self, series, video, sequence):
        assert isinstance(series, Series)
        assert isinstance(video, Video)
        assert isinstance(sequence, int)
        assert len(series.videos) + 1 >= sequence > -1

        if video in series.videos:
            return False

        if 0 < sequence <= len(series.videos):
            series.videos.insert(sequence - 1, video)
        else:
            series.videos.append(video)
        return True


class TagRogics(object):

    def create(self, name):
        assert isinstance(name, unicode)

        tag = Tag(name)
        DBSession.add(tag)

        return tag

    def get_by_id(self, tag_id):
        assert isinstance(tag_id, unicode)

        tag = DBSession.query(
            Tag
        ).filter(
            Tag.id == tag_id
        ).first()

        if tag is None:
            raise TagNotFound()
        return tag

    def get_all(self):
        tags = DBSession.query(
            Tag
        ).all()

        return list(tags)

    def add_video(self, tag, video):
        assert isinstance(tag, Tag)
        assert isinstance(video, Video)

        if video in tag.videos:
            return False

        tag.videos.append(video)
        return True

    def add_series(self, tag, series):
        assert isinstance(tag, Tag)
        assert isinstance(series, Series)

        if series in tag.seriess:
            return False

        tag.seriess.append(series)
        return True
