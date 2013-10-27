(function() {
    window.YVIDEOS = window.YVIDEOS || {Routers: {}, Collections: {}, Models: {}, Views: {}};

    YVIDEOS.Collections.S3Bucket = Backbone.Collection.extend({
        model: YVIDEOS.Models.S3Bucket,
        url: '/api/s3/buckets'
    });

    YVIDEOS.Collections.Object = Backbone.Collection.extend({
        model: YVIDEOS.Models.Object,
        url: '/api/objects'
    });

    YVIDEOS.Collections.Collection = Backbone.Collection.extend({
        model: YVIDEOS.Models.Collection,
        url: '/api/collections'
    });

    YVIDEOS.Collections.Video = Backbone.Collection.extend({
        model: YVIDEOS.Models.Video,
        url: '/api/videos'
    });

    YVIDEOS.Collections.Tag = Backbone.Collection.extend({
        model: YVIDEOS.Models.Tag,
        url: '/api/tags'
    });
})();