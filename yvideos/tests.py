# -*- coding: utf-8- -*-

import unittest
import uuid
import transaction

from pyramid import testing
from sqlalchemy import create_engine

from .exceptions import (
    CollectionNotFound,
    VideoNotFound
)
from .models import (
    Base,
    CollectionRogics,
    DBSession,
    Object,
    S3Bucket,
    S3Rogics,
    TagRogics,
    Video,
    VideoRogics
)


def initialize_DBSession():
    engine = create_engine('sqlite://')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    return DBSession


class TestS3Rogics(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        initialize_DBSession()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_add_bucket(self):
        inst = S3Rogics()
        with transaction.manager:
            b = inst.add_bucket(u'ap-northeast-1', u'test_bucket')

            # Test properties
            self.assertEqual(b.region, u'ap-northeast-1')
            self.assertEqual(b.name, u'test_bucket')

            # Test regioster
            count = DBSession.query(
                S3Bucket
            ).filter(
                S3Bucket.id == b.id
            ).count()
            self.assertEqual(count, 1)


class TestVideoRogics(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        initialize_DBSession()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_create(self):
        inst = VideoRogics()
        with transaction.manager:
            v = inst.create(u'video')

            # Test properties
            self.assertEqual(v.title, u'video')

            # Test register
            count = DBSession.query(
                Video
            ).filter(
                Video.id == v.id
            ).count()
            self.assertEqual(count, 1)

    def test_add_object(self):
        inst = VideoRogics()
        with transaction.manager:
            v = inst.create(u'video')
            b = S3Rogics().add_bucket(u'ap-northeast-1', u'bucket')
            self.assertTrue(inst.add_object(v, b, u's3_key', 1))

            o = DBSession.query(
                Object
            ).filter(
                Object.video == v
            ).first()

            self.assertIsNotNone(o)

            # Test Properties
            self.assertEqual(o.video, v)
            self.assertEqual(o.s3_bucket, b)
            self.assertEqual(o.s3_key, u's3_key')
            self.assertEqual(o.size_no, 1)

    def test_get_by_id(self):
        inst = VideoRogics()
        with transaction.manager:
            v = inst.create(u'video')
            got = inst.get_by_id(v.id)
            self.assertEqual(v, got)

            with self.assertRaises(VideoNotFound):
                inst.get_by_id(unicode(uuid.uuid4()))


class TestCollectionRogics(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        initialize_DBSession()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_create(self):
        inst = CollectionRogics()
        with transaction.manager:
            c = inst.create(u'collection')
            self.assertEqual(c.title, u'collection')
            self.assertEqual(len(c.videos), 0)

    def test_get_by_id(self):
        inst = CollectionRogics()
        with transaction.manager:
            c = inst.create(u'collection')
            got = inst.get_by_id(c.id)
            self.assertEqual(c, got)

            with self.assertRaises(CollectionNotFound):
                inst.get_by_id(unicode(uuid.uuid4()))


    def test_add_video(self):
        inst = CollectionRogics()
        with transaction.manager:
            c = inst.create(u'collection')

            vr = VideoRogics()
            v1 = vr.create(u'foo')
            inst.add_video(c, v1, 0)
            v2 = vr.create(u'bar')
            inst.add_video(c, v2, 1)
            v3 = vr.create(u'piyo')
            inst.add_video(c, v3, 2)

            self.assertListEqual(c.videos, [v2, v3, v1])


class TestTagRogics(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        initialize_DBSession()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_add_video(self):
        inst = TagRogics()
        vr = VideoRogics()
        with transaction.manager:
            tag = inst.get_or_create(u'tag')

            v1 = vr.create(u'video')
            self.assertTrue(inst.add_video(tag, v1))
            self.assertListEqual(tag.videos, [v1])
            self.assertListEqual(tag.collections, [])

            v2 = vr.create(u'video')
            self.assertTrue(inst.add_video(tag, v2))
            self.assertListEqual(tag.videos, [v1, v2])
            self.assertListEqual(tag.collections, [])

            self.assertFalse(inst.add_video(tag, v2))
            self.assertListEqual(tag.videos, [v1, v2])
            self.assertListEqual(tag.collections, [])

    def test_add_collection(self):
        inst = TagRogics()
        cr = CollectionRogics()
        with transaction.manager:
            tag = inst.get_or_create(u'tag')

            c1 = cr.create(u'collection')
            self.assertTrue(inst.add_collection(tag, c1))
            self.assertListEqual(tag.videos, [])
            self.assertListEqual(tag.collections, [c1])

            c2 = cr.create(u'collection')
            self.assertTrue(inst.add_collection(tag, c2))
            self.assertListEqual(tag.videos, [])
            self.assertListEqual(tag.collections, [c1, c2])

            self.assertFalse(inst.add_collection(tag, c2))
            self.assertListEqual(tag.videos, [])
            self.assertListEqual(tag.collections, [c1, c2])
