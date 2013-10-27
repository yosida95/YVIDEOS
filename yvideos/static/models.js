(function() {
    window.YVIDEOS = window.YVIDEOS || {Routers: {}, Collections: {}, Models: {}, Views: {}};

    YVIDEOS.Models.S3Bucket = Backbone.Model.extend({
        urlRoot: '/api/s3/buckets'
    });

    YVIDEOS.Models.Collection = Backbone.Model.extend({
        urlRoot: '/api/collections',
        parse: function(collection) {
            collection.videos = new YVIDEOS.Collections.Video(collection.videos);
            return collection;
        }
    });

    YVIDEOS.Models.Object = Backbone.Model.extend({
        urlRoot: '/api/objects',
        parse: function(object) {
            object.s3_bucket = new YVIDEOS.Models.S3Bucket(object.s3_bucket);
            return object;
        }
    });

    YVIDEOS.Models.Video = Backbone.Model.extend({
        urlRoot: '/api/videos',
        parse: function(video) {
            video.objects = new YVIDEOS.Collections.Object(video.objects);
            return video;
        }
    });

    YVIDEOS.Models.Tag = Backbone.Model.extend({
        urlRoot: '/api/tags'
    });
})();
