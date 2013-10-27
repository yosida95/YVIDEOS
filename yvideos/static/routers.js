(function() {
    window.YVIDEOS = window.YVIDEOS || {Routers: {}, Collections: {}, Models: {}, Views: {}};

    YVIDEOS.Routers.MainRouter = Backbone.Router.extend({
        initialize: function(options) {
            this.s3buckets = options.s3buckets;
            this.objects = options.objects;
            this.videos = options.videos;
            this.collections = options.collections;

            this.ready = this.s3buckets.fetch()
                .then($.proxy(function() {
                        return this.objects.fetch();
                }, this))
                .then($.proxy(function() {
                    return this.videos.fetch();
                }, this))
                .then($.proxy(function() {
                    return this.collections.fetch();
                }, this));
        },
        routes: {
            "videos/:video_id": "watch_video"
        },
        watch_video: function(video_id) {
            this.ready.done($.proxy(function(){
                this.currentView = new YVIDEOS.Views.WatchVideo({video: this.videos.get(video_id)});
                $("#content").html(this.currentView.render().el);
                this.currentView.afterRender();
            }, this));
        }
    });
})();
