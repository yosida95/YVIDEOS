# -*- coding: utf-8 -*-

from pyramid.view import (
    view_config,
    view_defaults
)

from .exceptions import (
    BucketNotFound,
    SeriesNotFound,
    ObjectNotFound,
    TagNotFound,
    VideoNotFound
)
from .models import (
    SeriesRogics,
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


@view_defaults(route_name='api_series_list', renderer='json')
class Collections(object):

    def __init__(self, request):
        self.request = request
        self.sr = SeriesRogics()

    @view_config(request_method='GET')
    def get(self):
        return self.sr.get_all()

    @view_config(request_method='POST')
    def post(self):
        try:
            body = self.request.json_body
        except:
            self.request.response.status_int = 400
            return {}
        else:
            try:
                series = self.sr.create(body[u'title'])
            except KeyError:
                self.request.response.status_int = 400
                return {}
            else:
                return series


@view_defaults(route_name='api_series', renderer='json')
class Series(object):

    def __init__(self, request):
        self.request = request

        self.sr = SeriesRogics()
        self.vr = VideoRogics()

        try:
            self.series = self.sr.get_by_id(request.matchdict['series_id'])
        except SeriesNotFound:
            self.series = None

    @view_config(request_method='GET')
    def get(self):
        if self.series is None:
            self.request.response.status_int = 404
            return {}

        return self.series

    @view_config(request_method='PUT')
    def put(self):
        if self.series is None:
            self.request.response.status_int = 404
            return {}

        try:
            body = self.request.json_body
        except:
            self.request.response.status_int = 400
            return {}
        else:
            try:
                self.series.set_title(body['title'])
                self.series.set_videos([
                    self.vr.get_by_id(video['id']) for video in body['videos']
                ])
            except (VideoNotFound, KeyError, AssertionError):
                self.request.response.status_int = 400
                return {}
            else:
                return self.series


@view_defaults(route_name=u'api_videos', renderer=u'json')
class Videos(object):

    def __init__(self, request):
        self.request = request
        self.vr = VideoRogics()

    @view_config(request_method='GET')
    def get(self):
        return self.vr.get_all()

    @view_config(request_method='POST')
    def post(self):
        try:
            body = self.request.json_body
            video = self.vr.create(body[u'title'])
        except:
            self.request.response.status_int = 400
            print u'here'
            print u'here'
            return {}
        else:
            return video


@view_defaults(route_name='api_video', renderer='json')
class Video(object):

    def __init__(self, request):
        self.request = request

        self.vr = VideoRogics()
        self.or_ = ObjectRogics()
        try:
            self.video = self.vr.get_by_id(request.matchdict['video_id'])
        except VideoNotFound:
            self.video = None

    def get(self):
        if self.video is None:
            self.request.response.status_int = 404
            return {}

        return self.video

    def put(self):
        if self.video is None:
            self.request.response.status_int = 404
            return {}

        try:
            body = self.request.json_body
            self.video.set_title(body[u'title'])
            self.video.set_objects([
                self.or_.get_by_id(object_['id'])
                for object_ in body['objects']
            ])
        except:
            self.request.response.status_int = 400
            return {}
        else:
            return self.video


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


"""
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
            elif u'series' in body:
                cr = SeriesRogics()
                try:
                    series = cr.get_by_id(body[u'series'])
                except (AssertionError, SeriesNotFound):
                    request.response.status_int = 400
                    return {}
                else:
                    tr.add_series(tag, series)
            else:
                request.response.status_int = 400
                return {}

            return tag
"""
