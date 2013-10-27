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
from sqlalchemy.ext.associationproxy import association_proxy
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
    CollectionNotFound,
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


class Video(Base):
    __tablename__ = u'videos'

    id = Column(Unicode(36), primary_key=True)
    title = Column(Unicode(255), nullable=False)

    def __init__(self, title):
        assert isinstance(title, unicode)

        self.id = unicode(uuid.uuid4())
        self.title = title

    def __json__(self, request):
        return {
            u'id': self.id,
            u'title': self.title,
            u'objects': self.objects
        }


class Object(Base):
    __tablename__ = u'objects'

    id = Column(Unicode(36), primary_key=True)
    video_id = Column(Unicode(36), ForeignKey(Video.id), nullable=False)
    video = relationship(Video, backref=backref(u'objects'))
    s3_bucket_id = Column(Unicode(36), ForeignKey(S3Bucket.id), nullable=False)
    s3_bucket = relationship(S3Bucket, backref=backref(u'objects'))
    s3_key = Column(Unicode(255), nullable=False, unique=True)
    size_no = Column(Integer(), nullable=False)

    def __init__(self, s3_bucket, s3_key, size_no):
        assert isinstance(s3_bucket, S3Bucket)
        assert isinstance(s3_key, unicode)
        assert isinstance(size_no, int)

        self.id = unicode(uuid.uuid4())
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.size_no = size_no

    def set_video(self, video):
        assert isinstance(video, Video)

        self.video = video
        return True

    def __json__(self, request):
        return {
            u'id': self.id,
            u's3_bucket': self.s3_bucket,
            u's3_key': self.s3_key
        }


class CollectionVideoAssoc(Base):
    __tablename__ = u'collection_video_assoc'

    collection_id = Column(Unicode(36), ForeignKey('collections.id'),
                           primary_key=True, nullable=False)
    video_id = Column(Unicode(36), ForeignKey(Video.id),
                      primary_key=True, nullable=False)
    video = relationship(Video)
    position = Column(Integer(), nullable=False)

    def __init__(self, video, **kw):
        if video is not None:
            kw[u'video'] = video

        super(CollectionVideoAssoc, self).__init__(**kw)


class Collection(Base):
    __tablename__ = u'collections'

    id = Column(Unicode(36), primary_key=True)
    title = Column(Unicode(36), primary_key=True)
    _videos = relationship(CollectionVideoAssoc,
                           order_by=[CollectionVideoAssoc.position],
                           collection_class=ordering_list(u'position'))
    videos = association_proxy(u'_videos', u'video')

    def __init__(self, title):
        assert isinstance(title, unicode)

        self.id = unicode(uuid.uuid4())
        self.title = title

    def __json__(self, request):
        return {
            u'id': self.id,
            u'title': self.title,
            u'videos': list(self.videos)
        }


tag_video_assoc = Table(
    'tag_video_assoc', Base.metadata,
    Column('tag_id', Unicode(36), ForeignKey('tags.id'), nullable=False),
    Column('video_id', Unicode(36), ForeignKey('videos.id'), nullable=False)
)


tag_collection_assoc = Table(
    'tag_collection_assoc', Base.metadata,
    Column('tag_id', Unicode(36), ForeignKey('tags.id'), nullable=False),
    Column('collection_id', Unicode(36), ForeignKey('collections.id'),
           nullable=False)
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

    def __json__(self, reqeust):
        return {
            u'id': self.id,
            u'name': self.name,
            u'collections': self.collections,
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


class CollectionRogics(object):

    def create(self, title):
        assert isinstance(title, unicode)

        c = Collection(title)
        DBSession.add(c)
        return c

    def get_all(self):
        collections = DBSession.query(
            Collection
        ).all()

        return list(collections)

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

        if video in collection.videos:
            return False

        if 0 < sequence <= len(collection.videos):
            collection.videos.insert(sequence - 1, video)
        else:
            collection.videos.append(video)
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

    def add_collection(self, tag, collection):
        assert isinstance(tag, Tag)
        assert isinstance(collection, Collection)

        if collection in tag.collections:
            return False

        tag.collections.append(collection)
        return True
