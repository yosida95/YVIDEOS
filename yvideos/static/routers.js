(function() {
    window.YVIDEOS = window.YVIDEOS ||
        {Routers: {}, Collections: {}, Models: {}, Views: {}};

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
            'series': 'series',
            'collections/:collection_id/:video_id': 'watch_video',
            'videos': 'videos',
            'videos/:video_id': 'watch_video',
            'object/register': 'object_register'
        },
        series: function() {
            this.currentView && this.currentView.remove();
            this.currentSideView && this.currentSideView.remove();

            this.ready.done($.proxy(function() {
                this.currentView = (new YVIDEOS.Views.SeriesView({
                    series: this.collections
                })).render();
                $('#content').html(this.currentView.el);
            }, this));

        },
        videos: function() {
            this.currentView && this.currentView.remove();
            this.currentSideView && this.currentSideView.remove();

            this.ready.done($.proxy(function() {
                this.currentView = (new YVIDEOS.Views.VideosView({
                    videos: this.videos
                })).render();
                $('#content').html(this.currentView.el);
            }, this));

        },
        object_register: function() {
            this.currentView && this.currentView.remove();

            this.ready.done($.proxy(function() {
                this.currentView = (new YVIDEOS.Views.ObjectRegisterView({
                    objects: this.objects.slice(0, 10)
                })).render();
                $('#content').html(this.currentView.el);
            }, this));
        },
        watch_video: function() {
            this.currentView && this.currentView.remove();

            var collection_id,
                video_id;

            if (arguments.length == 1) {
                video_id = arguments[0];
            } else {
                collection_id = arguments[0];
                video_id = arguments[1];
            }

            this.ready.done($.proxy(function() {
                var collection,
                    video;
                if (collection_id) {
                    collection = this.collections.get(collection_id);
                    if (collection === undefined) {
                        // NotFound
                        return;
                    }

                    video = collection.get('videos').detect(function(video) {
                        return video.get('id') == video_id;
                    });
                } else {
                    video = this.videos.get(video_id);
                }

                if (video === undefined) {
                    // NotFound
                    return;
                }

                this.currentView = new YVIDEOS.Views.WatchVideo({
                    video: video
                });
                $('#content').html(this.currentView.render().el);

                if (collection) {
                    this.currentSideView =
                        new YVIDEOS.Views.CollectionSideView({
                            watchView: this.currentView,
                            collection: collection
                        });
                    $('#sidebar').html(this.currentSideView.render().el);
                }
            }, this));
        }
    });
})();
