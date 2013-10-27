# -*- coding: utf-8 -*-

from pyramid.view import view_config

from .exceptions import (
    BucketNotFound,
    CollectionNotFound,
    ObjectNotFound,
    TagNotFound,
    VideoNotFound
)
from .models import (
    CollectionRogics,
    S3Rogics,
    ObjectRogics,
    TagRogics,
    VideoRogics
)


@view_config(route_name=u'home',
             request_method=[u'GET'],
             renderer=u'templates/home.pt')
def home(request):
    return {}


@view_config(route_name=u'api_s3_buckets',
             request_method=[u'GET', u'POST'],
             renderer=u'json')
def api_s3_buckets(request):
    s3r = S3Rogics()
    if request.method == u'GET':
        return s3r.get_all_buckets()
    elif request.method == u'POST':
        try:
            body = request.json_body
        except:
            request.response.status_int = 400
            return {}
        else:
            try:
                bucket = s3r.add_bucket(body[u'region'], body[u'name'])
            except (AssertionError, KeyError):
                request.response.status_int = 400
                return {}
            else:
                return bucket


@view_config(route_name=u'api_s3_bucket',
             request_method=[u'GET'],
             renderer=u'json')
def api_s3_bucket(request):
    s3r = S3Rogics()
    try:
        bucket = s3r.get_bucket_by_id(request.matchdict[u'bucket_id'])
    except (AssertionError, BucketNotFound):
        request.response.status_int = 404
        return {}

    if request.method == u'GET':
        return bucket


@view_config(route_name=u'api_collections',
             request_method=[u'GET', u'POST'],
             renderer=u'json')
def api_collections(request):
    cr = CollectionRogics()
    if request.method == u'GET':
        return cr.get_all()
    elif request.method == u'POST':
        try:
            body = request.json_body
        except:
            request.response.status_int = 400
            return {}
        else:
            try:
                collection = cr.create(body[u'title'])
            except KeyError:
                request.response.status_int = 400
                return {}
            else:
                return collection


@view_config(route_name=u'api_collection',
             request_method=[u'GET', u'PUT'],
             renderer=u'json')
def api_collection(request):
    collection_id = request.matchdict[u'collection_id']
    if request.method == u'GET':
        cr = CollectionRogics()
        try:
            collection = cr.get_by_id(collection_id)
        except CollectionNotFound:
            request.response.status_int = 404
            return {}
        else:
            return collection
    elif request.method == u'PUT':
        try:
            body = request.json_body
        except:
            request.response.status_int = 400
            return {}
        else:
            cr = CollectionRogics()
            vr = VideoRogics()
            try:
                collection = cr.get_by_id(collection_id)
                video = vr.get_by_id(body[u'video'])

                print type(body[u'seq_no'])
                cr.add_video(collection, video, body[u'seq_no'])
            except (VideoNotFound, KeyError, AssertionError):
                request.response.status_int = 400
                return {}
            else:
                return collection


@view_config(route_name=u'api_objects',
             request_method=[u'GET'],
             renderer=u'json')
def api_objects(request):
    _or = ObjectRogics()

    if request.method == u'GET':
        return _or.get_all()


@view_config(route_name=u'api_object',
             request_method=[u'GET'],
             renderer=u'json')
def api_object(request):
    _or = ObjectRogics()
    s3r = S3Rogics()

    try:
        _object = _or.get_by_id(request.matchdict[u'object_id'])
    except (AssertionError, ObjectNotFound):
        request.response.status_int = 404
        return {}

    if request.method == u'GET':
        _dict = _object.__json__(request)
        _dict[u'url'] = s3r.generate_url(_object)
        return _dict


@view_config(route_name=u'api_videos',
             request_method=[u'GET', u'POST'],
             renderer=u'json')
def api_videos(request):
    vr = VideoRogics()

    if request.method == u'GET':
        return vr.get_all()
    elif request.method == u'POST':
        try:
            body = request.json_body
        except:
            request.response.status_int = 400
            print u'here'
            print u'here'
            return {}
        else:
            try:
                video = vr.create(body[u'title'])
            except (KeyError, AssertionError) as why:
                request.response.status_int = 400
                print why
                print body
                print why
                return {}
            else:
                return video


@view_config(route_name=u'api_video',
             request_method=[u'GET'],
             renderer=u'json')
def api_video(request):
    vr = VideoRogics()
    try:
        video = vr.get_by_id(request.matchdict[u'video_id'])
    except (AssertionError, VideoNotFound):
        request.response.status_int = 404
        return {}

    if request.method == u'GET':
        return video


@view_config(route_name=u'api_tags',
             request_method=[u'GET', u'POST'],
             renderer=u'json')
def api_tags(request):
    tr = TagRogics()
    if request.method == u'GET':
        return tr.get_all()
    elif request.method == u'POST':
        try:
            body = request.json_body
        except:
            request.response.status_int = 400
            return {}
        else:
            if request.method == u'POST':
                try:
                    tag = tr.create(body[u'name'])
                except (AssertionError, KeyError):
                    request.response.status_int = 400
                    return {}
                else:
                    return tag


@view_config(route_name=u'api_tag',
             request_method=[u'GET', u'PUT'],
             renderer=u'json')
def api_tag(request):
    tr = TagRogics()
    try:
        tag = tr.get_by_id(request.matchdict[u'tag_id'])
    except (AssertionError, TagNotFound):
        request.response.status_int = 404
        return {}

    if request.method == u'GET':
        return tag
    elif request.method == u'PUT':
        try:
            body = request.json_body
        except:
            request.response.status_int = 400
            return {}
        else:
            if u'video' in body:
                vr = VideoRogics()
                try:
                    video = vr.get_by_id(body[u'video'])
                except (AssertionError, VideoNotFound):
                    request.response.status_int = 400
                    return {}
                else:
                    tr.add_video(tag, video)
            elif u'collection' in body:
                cr = CollectionRogics()
                try:
                    collection = cr.get_by_id(body[u'collection'])
                except (AssertionError, CollectionNotFound):
                    request.response.status_int = 400
                    return {}
                else:
                    tr.add_collection(tag, collection)
            else:
                request.response.status_int = 400
                return {}

            return tag
