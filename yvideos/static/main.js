$(function() {
    var s3buckets = new YVIDEOS.Collections.S3Bucket(),
        objects = new YVIDEOS.Collections.Object(),
        videos = new YVIDEOS.Collections.Video(),
        collections = new YVIDEOS.Collections.Collection();

    window.app = new YVIDEOS.Routers.MainRouter({
        s3buckets: s3buckets,
        objects: objects,
        videos: videos,
        collections: collections
    });

    Backbone.history.start()
});
