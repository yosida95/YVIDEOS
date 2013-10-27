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
            "videos/:video_id": "watch_video",
            "collections/:collection_id/:video_id": "watch_video"
        },
        watch_video: function() {
            var collection_id,
                video_id;

            if (arguments.length == 1) {
                video_id = arguments[0];
            } else {
                collection_id = arguments[0];
                video_id = arguments[1];
            }

            this.ready.done($.proxy(function(){
                var collection,
                    video;
                if (collection_id) {
                    collection = this.collections.get(collection_id);
                    if(collection === undefined){
                        // NotFound
                        return;
                    }

                    console.log(collection);
                    video = collection.get('videos').detect(function(video){
                        return video.get('id') == video_id;
                    });
                } else {
                    video = this.videos.get(video_id);
                }

                if (video === undefined) {
                    // NotFound
                    console.log('here');
                    return;
                }

                this.currentView = new YVIDEOS.Views.WatchVideo({
                    video: video
                });
                $("#content").html(this.currentView.render().el);
                this.currentView.afterRender();
            }, this));
        }
    });
})();
