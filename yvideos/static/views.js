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
                .text(this.object.get("version"));
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
                this.renderMovie(this.objects.first());
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
            object.fetch().done($.proxy(function(){
                var unit = Math.floor(this.movie.width() / 16);
                jwplayer(this.movie[0]).setup({
                    file: object.get('url'),
                    width: unit * 16,
                    height: unit * 9
                });
            }, this));

            return this;
        }
    });

    YVIDEOS.Views.CollectionSideView = Backbone.View.extend({
        initialize: function(options) {
            this.watchView = options.watchView;
            this.collection = options.collection;
        },
        render: function() {
            this.$el.append($('<h2>').text(this.collection.get('title')));

            this.collection.get('videos').forEach($.proxy(function(video) {
                var row = new YVIDEOS.Views.CollectionSideViewRow({
                    watchView: this.watchView,
                    collection: this.collection,
                    video: video
                }).render();
                this.$el.append(row.$el);
            }, this));
            return this;
        }
    });

    YVIDEOS.Views.CollectionSideViewRow = Backbone.View.extend({
        tagName: 'div',
        initialize: function(options) {
            this.watchView = options.watchView;
            this.collection = options.collection;
            this.video = options.video;
        },
        events: {
            'click': 'click'
        },
        render: function() {
            this.$el.empty();
            this.$el.css('cursor', 'pointer');

            this.$el.append($('<h3>').text(this.video.get('title')));
            return this;
        },
        click: function() {
            console.log('clicked');
            app.navigate("collections/" + this.collection.get('id') + "/" + this.video.get("id"), {trigger: true});
        }
    });

    YVIDEOS.Views.ObjectRegisterView = Backbone.View.extend({
        initialize: function(options) {
            this.objects = options.objects;
        },
        render: function() {
            this.$el.empty();

            this.objects.forEach($.proxy(function(object) {
                this.$el.append((new YVIDEOS.Views.ObjectRegisterRowView({
                    object: object
                })).render().$el)
            }), this);

            return this;
        }
    });


    YVIDEOS.Views.ObjectRegisterRowView = Backbone.View.extend({
        tagName: "div",
        className: "row",
        initialize: function(options) {
            this.object = options.object;
        },
        render: function() {
            var preview = (new YVIDEOS.Views.ObjectPreviewView({
                    object: this.object
                })).render(),
                register = (new YVIDEOS.Views.VideoRegisterFormView({
                    object: this.object
                })).render();

            console.log(preview);

            this.$el
                .append($('<div>')
                    .addClass('row')
                        .append($('<div>')
                            .addClass('col-lg-3')
                            .append(preview.$el))
                        .append($('<div>')
                            .addClass('col-lg-5')
                            .append(register.$el)))
                .append($('<div>')
                    .addClass('row'));

            return this;
        }
    });

    YVIDEOS.Views.ObjectPreviewView = Backbone.View.extend({
        initialize: function(options) {
            this.object = options.object;
            this._id = (function() {;
                var id = [];
                for(var i = 0; i < 20; i++) {
                    var seed = Math.floor(Math.random() * 32);
                    if(seed < 26) {
                        id.push(String.fromCharCode(65 + seed));
                    }else{
                        id.push(String.fromCharCode(71 + seed));
                    }
                }
                return id.join("");
            })();
        },
        render: function() {
            this.$el.empty();
            this.movie = $('<div>')
                .attr('id', this._id)
                .text("Loading player...");
            this.$el.append(this.movie);

            this.object.fetch().done($.proxy(function(){
                var unit = Math.floor(this.movie.width() / 16);
                jwplayer(this._id).setup({
                    file: this.object.get('url'),
                    width: unit * 16,
                    height: unit * 9
                });
            }, this));

            return this;
        }
    });

    YVIDEOS.Views.VideoRegisterFormView = Backbone.View.extend({
        tagName: 'form',
        attributes: {
            className: 'form-horizontal',
            role: "form"
        },
        events: {
            'submit': 'submit',
            'click #video-register': 'register',
            'click #video-search': 'search'
        },
        initialize: function(options) {
            this.object = options.object;
        },
        render: function() {
            this.$el.empty();

            var title = $('<div>')
                .addClass('form-group')
                .append($('<label>')
                    .addClass('col-lg-2')
                    .addClass('control-label')
                    .text('Title'))
                .append($('<div>')
                    .addClass('col-lg-10')
                    .append($('<input>')
                        .attr('type', 'text')
                        .attr('placeholder', 'Title')
                        .addClass('form-control')));
            this.$el.append(title);

            var button = $('<div>')
                .addClass('form-group')
                .append($('<div>')
                    .addClass('col-lg-offset-2')
                    .addClass('col-lg-10')
                    .append($('<button>')
                        .attr('id', 'video-register')
                        .attr('type', 'button')
                        .addClass('btn')
                        .addClass('btn-primary')
                        .text('Register'))
                    .append($('<button>')
                        .attr('id', 'video-search')
                        .attr('type', 'button')
                        .addClass('btn')
                        .addClass('btn-default')
                        .text('Search')));
            this.$el.append(button);

            return this;
        },
        submit: function() {
            return false;
        },
        register: function() {
            var video = new YVIDEOS.Models.Video({
                title: this.$el.find('input[type="text"]').val()
            });
            video.save({}, {success: function(model, response) {
                model.set('id', response.id);
            }}).done($.proxy(function(){
                app.videos.add(video);

                video.get('objects').push(this.object);
                video.save();
            }, this));

            return false;
        },
        search: function() {
            var videos = app.videos.search(this.$el.find('input[type="text"]').val());
            console.log(videos);
            return false;
        }
    });
})();
