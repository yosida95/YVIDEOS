(function() {
    window.YVIDEOS = window.YVIDEOS || {Routers: {}, Collections: {}, Models: {}, Views: {}};

    YVIDEOS.Views.DropdownColumn = Backbone.View.extend({
        tagName: "li",
        initialize: function(options) {
            this.parentView = options.parentView;
            this.object = options.object;
        },
        events: {
            'click': 'click'
        },
        click: function() {
            this.parentView.renderMovie(this.object);
        },
        render: function() {
            this.$el.empty();
            var link = $("<a>")
                .text("1920x1080");
            this.$el.append(link);
            return this;
        }
    });

    YVIDEOS.Views.WatchVideo = Backbone.View.extend({
        initialize: function(options) {
            this.video = options.video;
        },
        render: function() {
            this.$el.empty();

            var title = $("<h1>").text(this.video.get("title"));
            this.$el.append(title);

            this.movie = $("<div>")
                .attr("id", "movie");

            this.objects = this.video.get('objects');
            if (this.objects.length < 1) {
                this.movie.text("This video is not available");
            } else if (this.objects.length == 1 ) {
                this.movie.text("Loading player...");
            } else {
                this.movie.text("Waiting for choose size of movie...");

                var dropdown = $("<div>").addClass("btn-group");
                this.$el.append(dropdown);

                var button = $("<button>")
                    .attr("type", "button")
                    .attr("data-toggle", "dropdown")
                    .addClass("btn")
                    .addClass("btn-default")
                    .addClass("dropdown-toggle")
                    .text("size")
                    .append($("<span>").addClass("caret"));
                dropdown.append(button);

                var menu = $("<ul>")
                    .attr("role", "menu")
                    .addClass("dropdown-menu");
                dropdown.append(menu);

                this.objects.forEach($.proxy(function(object){
                    column = new YVIDEOS.Views.DropdownColumn({
                        parentView: this,
                        object: object
                    }).render();
                    menu.append(column.$el);
                }, this));
            }

            this.$el.append(this.movie);
            return this;
        },
        renderMovie: function(object) {
            this.movie.empty().text("Loading player...");
            object.fetch().done(function(){
                var unit = Math.floor($("#movie").width() / 16);
                jwplayer("movie").setup({
                    file: object.get('url'),
                    width: unit * 16,
                    height: unit * 9
                });
            });

            return this;
        },
        afterRender: function() {
            if (this.objects.length == 1) {
                this.renderMovie(this.objects.first());
            }

            return this;
        }
    });
})();
