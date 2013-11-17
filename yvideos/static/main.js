$(function() {
    var s3buckets = new YVIDEOS.Collections.S3Bucket(),
        objects = new YVIDEOS.Collections.Object(),
        videos = new YVIDEOS.Collections.Video(),
        series = new YVIDEOS.Collections.Series();

    window.app = new YVIDEOS.Routers.MainRouter({
        s3buckets: s3buckets,
        objects: objects,
        videos: videos,
        series: series
    });

    Backbone.history.start();
});
