(function() {
    window.YVIDEOS = window.YVIDEOS ||
        {Routers: {}, Collections: {}, Models: {}, Views: {}};

    YVIDEOS.Collections.S3Bucket = Backbone.Collection.extend({
        model: YVIDEOS.Models.S3Bucket,
        url: '/api/s3/buckets'
    });

    YVIDEOS.Collections.Object = Backbone.Collection.extend({
        model: YVIDEOS.Models.Object,
        url: '/api/objects'
    });

    YVIDEOS.Collections.Series = Backbone.Collection.extend({
        model: YVIDEOS.Models.Series,
        url: '/api/series'
    });

    YVIDEOS.Collections.Video = Backbone.Collection.extend({
        model: YVIDEOS.Models.Video,
        url: '/api/videos',
        search: function(text) {
            return this.models.filter(function(video) {
                return video.get('title').toLowerCase().
                    indexOf(text.toLowerCase()) > -1;
            });
        }
    });

    YVIDEOS.Collections.Tag = Backbone.Collection.extend({
        model: YVIDEOS.Models.Tag,
        url: '/api/tags'
    });
})();
