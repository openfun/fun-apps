<%!
from django.utils.translation import ugettext as _
%>

<%
from django.core.urlresolvers import reverse
def reverse_course(handler_name, kwargs=None):
  kwargs = kwargs or {}
  kwargs['course_key_string'] = unicode(context_course.id)
  return reverse(handler_name, kwargs=kwargs)
%>
<%namespace name='static' file='../../static_content.html'/>

require(["jquery", "underscore", "backbone", "gettext",
         "js/utils/templates", "js/views/modals/base_modal", "js/views/feedback_notification",
         "videojs-fun", "libcast"],
  function ($, _, Backbone, gettext,
    TemplateUtils, BaseModal, NotificationView,
    videojs, libcast) {

    var UploadChunkMegabytes = 64;
    var ajaxSettings = (function() {
      var headers = {};

      // Previous calls to $.ajaxSetup(...) might have defined default headers
      // to send with every ajax call. Also, ajax request errors activate a popup
      // on the bottom of the screen. We need to disable additional headers for
      // CORS requests, and errors are handled by each VideoView.

      function resetHeaders() {
        if(_.size(headers) > 0 && (!$.ajaxSettings.headers || _.size($.ajaxSettings.headers) == 0)) {
          $.ajaxSettings.headers = headers;
        }
      }
      function unsetHeaders() {
        if($.ajaxSettings.headers && _.size($.ajaxSettings.headers) > 0) {
          headers = $.ajaxSettings.headers;
          $.ajaxSettings.headers = {};
        }
      }
      function unsetNotify() {
        $.ajaxSettings.notifyOnError = false;
      }
      function resetNotify() {
        $.ajaxSettings.notifyOnError = true;
      }

      return {
        unsetHeaders: unsetHeaders,
        resetHeaders: resetHeaders,
        unsetNotify: unsetNotify,
        resetNotify: resetNotify,
      }
    })();

    function popError(error) {
      var notificationView = new NotificationView.Error({
        "title": gettext("Error"),
        "message": error,
      });
      notificationView.show();
    }

    function deactivateForm(elt) {
      $(elt).find("[type='submit']").attr('disabled', '');
    }
    function reactivateForm(elt) {
      $(elt).find("[type='submit'][disabled]").removeAttr('disabled');
    }

    // Status workflow for a video:
    // preparing -> prepared -> uploading -> uploaded -> creating -> created -> processing -> ready -> published -> deleted
    var Video = Backbone.Model.extend({
      defaults: {
        created_at: "",
        created_at_timestamp: null,
        embed_url: "",
        video_sources: [],
        external_link: "",
        error: "",
        subtitles: [],
        title: "",
        encoding_progress: null,
      },

      url: function() {
        var baseUrl = '${reverse_course("videoupload:video", kwargs={"video_id": "videoid"})}';
        return baseUrl.replace("videoid", this.get("id"));
      },

      setStatus: function(status, data) {
        this.set("status", status);
        this.trigger("status-" + status, data);
      },

      setError: function(error) {
        this.setStatus("error");
        this.set("error", error);
      },

      wasUploaded: function() {
        var videoStatus = this.get("status");
        return videoStatus === "published" || videoStatus === "ready";
      },

      videoId: function() {
        return this.get("id") || "";
      },
    });

    var VideoCollection = Backbone.Collection.extend({
      model: Video,
      url: '${reverse_course("videoupload:videos")}',
      parse: function(data) {
        if (data.error) {
          this.trigger("syncError", data.error);
        }
        return data.videos;
      }
    });

    var VideoDeleteModalView = BaseModal.extend({
      options: $.extend({}, BaseModal.prototype.options, {
        title: gettext("Are you sure you want to delete this video?"),
        modalSize: "sm",
      }),

      events: $.extend({}, BaseModal.prototype.events, {
        "click .action-delete": "onClickConfirmDelete"
      }),

      getContentHtml: function() {
        return gettext("Once this video is deleted, it will no longer be available in the courses that include it. This action is irreversible.");
      },

      addActionButtons: function() {
        VideoDeleteModalView.__super__.addActionButtons.apply(this);
        this.addActionButton('delete', gettext('Delete'), true);
      },

      onClickConfirmDelete: function() {
        // This should trigger a DELETE request
        this.model.destroy();
        this.hide()
      }
    });

    var VideoView = Backbone.View.extend({
      tagName: 'tr',
      template: TemplateUtils.loadTemplate("videoupload-video"),

      events: {
        "click .action-edit-title": "toggleTitleEdit",
        "keyup .title input": "onEditTitle",
        "click .action-delete": "onClickDelete",
        "click .action-cancel": "onClickCancel",
        "click .action-publish": "onClickPublish",
        "click .action-unpublish": "onClickUnpublish",
        "click .action-parameters": "onClickParameters",
      },

      initialize: function() {
        this.listenTo(this.model, 'change', this.render);
        this.listenTo(this.model, 'change:title', this.changeTitle);
        this.listenTo(this.model, 'sync', this.modelSynced);
        this.listenTo(this.model, 'destroy', this.remove);
        this.listenTo(this.model, 'uploading-progress', this.uploadingProgress);
        this.listenTo(this.model, 'status-uploaded', this.createVideo);
        this.listenTo(this.model, 'status-publishing', this.publishVideo);
        this.listenTo(this.model, 'status-unpublishing', this.unpublishVideo);
      },

      render: function() {
        var values = this.model.toJSON();
        if (!values.id) {
            values.id = "";
        }
        this.$el.html(this.template(values));
        if (!values.embed_url && values.video_sources && values.video_sources.length > 0) {
          // Time to activate the libcast videojs player
          var video = this.$el.find('video')[0];
          libcast(video);
        }
        return this;
      },

      onEditTitle: function(e) {
        if (e.keyCode == 13) {// enter key validates input
          this.toggleTitleEdit();
          this.model.set("title", this.$(".title input").val());
        } else if (e.keyCode == 27) {// escape key cancels
          this.toggleTitleEdit();
          this.$(".title input").val(this.model.get("title"));
        }
      },

      toggleTitleEdit: function() {
        this.$(".title .togglable").toggleClass("invisible");
        this.$(".title input:visible").focus();
      },

      changeTitle: function() {
        var that = this;
        this.post(this.model.url(), {
          title: this.model.get("title")
        });
      },

      modelSynced: function() {
        if (this.model.get("status") === "processing") {
          // Update model after 5s if it is in 'processing' stage
          var that = this;
          setTimeout(function(){
            that.model.fetch();
          }, 5000)
        }
      },

      onClickDelete: function(e) {
        if (this.model.wasUploaded()) {
          var videoDeleteModalView = new VideoDeleteModalView({
            model: this.model
          });
          videoDeleteModalView.show();
        } else {
          this.model.destroy();
        }
      },

      onClickCancel: function(e) {
        this.model.destroy();
      },

      onClickPublish: function(e) {
        this.model.setStatus("publishing");
      },

      onClickUnpublish: function(e) {
        this.model.setStatus("unpublishing");
      },

      onClickParameters: function(e) {
        var parameterView = new ParameterView({model: this.model});
        parameterView.show();
      },

      createVideo: function(uploadedData) {
        ajaxSettings.resetHeaders();
        ajaxSettings.unsetNotify();
        var that = this;
        $.ajax({
          url: '${reverse_course("videoupload:create-video")}',
          data: {
            title: that.model.get("title"),
            payload: JSON.stringify(uploadedData),
          },
          type: 'POST',
          success: function(data) {
            if (data.error) {
              that.model.setError(data.error);
            } else {
              that.model.setStatus("created", data.url);
              that.model.set("id", data.id);
              that.model.fetch();
            }
          },
          error: function(jqXHR, textStatus, errorThrown) {
            that.model.setError(errorThrown);
          },
        });
      },

      uploadingProgress: function(percent) {
        this.$(".progressbar").progressbar({value: percent});
      },

      publishVideo: function() {
        this.post('${reverse_course("videoupload:publish-video")}',
          {
            title: this.model.get("title"),
            video_id: this.model.get("id"),
          },
          "published"
        );
      },

      unpublishVideo: function() {
        this.post('${reverse_course("videoupload:unpublish-video")}',
          {
            video_id: this.model.get("id"),
          },
          "ready"
        );
      },

      post: function(url, postData, successStatus) {
        var that = this;
        ajaxSettings.resetHeaders();
        return $.post(url, postData,
          function(data) {
            if (data.error) {
              that.model.setError(data.error);
            } else {
              that.model.set(data);
              if (successStatus) {
                that.model.setStatus(successStatus);
              }
            }
          }
        ).fail(function(jqXHR, textStatus, errorThrown){
            that.model.setError(errorThrown);
        });
      },
    });

    var VideoCollectionView = Backbone.View.extend({
      el: $("#videoupload-list"),
      template: TemplateUtils.loadTemplate("videoupload-list"),

      initialize: function() {
        this.sortedBy = "created_at_timestamp";
        this.sortedOrder = -1;
        this.listenTo(this.collection, 'request', this.syncing);
        this.listenTo(this.collection, 'sync', this.synced);
        this.listenTo(this.collection, 'add', this.addOne);
        this.listenTo(this.collection, 'syncError', this.syncError);
        this.listenTo(this.collection, 'sort', this.render);
        this.render();
        this.collection.fetch();
      },

      events: {
          "click [data-sortby]": "clickOnSortBy"
      },

      syncing: function(model_or_collection) {
        if (model_or_collection === this.collection) {
            this.$(".syncing").show();
            this.$(".synced").hide();
        }
        return this;
      },

      synced: function(model_or_collection) {
        if (model_or_collection === this.collection) {
            this.$(".syncing").hide();
            this.$(".synced").show();
            this.sort();
            this.render();
        }
        return this;
      },

      render: function() {
        this.$el.html(this.template());

        // Re-draw sort arrows
        this.$("th[data-sortby] .sort-indicator").html("<img src='${static.url('datatables/images/sort_both.png')}'>");
        if (this.sortedBy) {
            var imgSrc = this.sortedOrder === 1 ? "${static.url('datatables/images/sort_asc.png')}" : "${static.url('datatables/images/sort_desc.png')}";
            this.$("th[data-sortby='" + this.sortedBy + "'] .sort-indicator").html("<img src='" + imgSrc + "'>");
        }

        // Display each video
        var that = this;
        this.collection.each(function(video) {
            var videoView = new VideoView({model: video});
            that.$('tbody').append(videoView.render().el);
        });
        return this;
      },

      syncError: function(error) {
        popError(error);
      },

      clickOnSortBy: function(e) {
          var sortBy = $(e.target).attr("data-sortby");
          if (!sortBy) {
              // Click inside of "data-sortby" element
              sortBy = $(e.target).parents("[data-sortby]").attr("data-sortby");
          }
          if (sortBy === this.sortedBy) {
              // Click on same criterion twice inverts the order
              this.sortedOrder = -this.sortedOrder;
          } else {
              // When we change the order we sort by ascending values
              this.sortedOrder = 1;
          }
          this.sortedBy = sortBy;
          this.sort();
      },
      sort: function() {
          var that = this;
          this.collection.comparator = function(v1, v2) {
              function getValue(video) {
                  // Function of one Video element that returns the value from
                  // which the collection should be sorted.
                  var value = video.get(that.sortedBy);
                  if (value.toLowerCase) {
                      value = value.toLowerCase();
                  }
                  return value;
              }
              var val1 = getValue(v1);
              var val2 = getValue(v2);
              if(val1 === val2) {
                  return 0;
              }
              return val1 < val2 ? -that.sortedOrder : that.sortedOrder;
          };
          this.collection.sort();
      },
    });

    var VideoUploadFormView = Backbone.View.extend({
      events: {
        "click button": "onChooseFile",
        "change input": "onFileChosen",
      },
      onChooseFile: function(e) {
        e.preventDefault();

        // Reset content so that we may trigger 'change' events even if the
        // same file is selected twice in a row.
        this.$("input").val(null);

        // Input form is hidden so we need to manually trigger a click
        this.$("input").click();
      },

      onFileChosen: function(e) {
        for(var i=0; i < e.target.files.length; i++) {
          this.uploadToNewUrl(e.target.files[i]);
        }
      },

      uploadToNewUrl: function(videoFile) {
        var that = this;
        var video = new Video({
          title: videoFile.name,
          status: "preparing"
        });
        this.collection.add(video);
        var currentUploadRequest = null;
        this.listenToOnce(video, "destroy", function() {
          if (currentUploadRequest) {
            currentUploadRequest.abort();
          }
        });
        $.getJSON('${reverse_course("videoupload:upload-url")}', function(uploadParams) {
          video.setStatus("prepared", uploadParams);
          var fileSize = videoFile.size;
          var chunkSize = UploadChunkMegabytes*1024*1024;
          var chunkCount = Math.ceil(fileSize / chunkSize);
          ajaxSettings.unsetHeaders();
          ajaxSettings.unsetNotify();
          video.setStatus("uploading");
          // Upload chunks sequentially
          that.listenTo(video, "ready-to-upload-chunk", function(c) {
            var chunkBlob = videoFile.slice(c*chunkSize, Math.min(fileSize, (c+1)*chunkSize));
            var chunkFile = new File([chunkBlob], videoFile.name);
            var formData = new FormData();
            formData.append(uploadParams.file_parameter_name, chunkFile);
            formData.append('chunk', c);
            formData.append('chunks', chunkCount);
            currentUploadRequest = $.ajax({
              url: uploadParams.url,
              data: formData,
              type: 'POST',
              contentType: false,
              processData: false,
              crossDomain: true,
              xhr: function() {
                // Track upload progress
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function(event) {
                  if (event.lengthComputable) {
                    var progress = event.loaded + c*chunkSize;
                    video.trigger("uploading-progress", progress * 100 / fileSize)
                  }
                });
                return xhr;
              },
              success: function(data){
                if (data.error) {
                  video.setError(data.error)
                } else {
                  if (c == chunkCount - 1) {
                    video.setStatus("uploaded", data);
                  } else {
                    video.trigger("ready-to-upload-chunk", c+1);
                  }
                }
              },
              error: function(jqXHR, textStatus, errorThrown) {
                video.setError(errorThrown);
              },
            });
          });
          video.trigger("ready-to-upload-chunk", 0);
        });
      },
    });

    var Subtitle = Backbone.Model.extend({
    });

    var SubtitleCollection = Backbone.Collection.extend({
      model: Subtitle,

      initialize: function(models, options) {
        this.video = options.video;
      },

      url: function() {
        var baseUrl = '${reverse_course("videoupload:video-subtitles", kwargs={"video_id": "videoid"})}';
        return baseUrl.replace("videoid", this.video.get("id"));
      },
    });

    var SubtitleView = Backbone.View.extend({
      tagName: 'tr',
      template: TemplateUtils.loadTemplate("videoupload-parameters-subtitle"),

      initialize: function() {
        this.listenTo(this.model, 'destroy', this.remove);
        this.listenTo(this.model, 'change', this.render);
      },

      events: {
        "click .action-delete": "onClickDelete",
      },

      render: function() {
        this.$el.html(this.template(this.model.toJSON()));
        return this;
      },

      onClickDelete: function(e) {
        // Note: no confirmation required here
        this.model.destroy();
      },
    });

    var ThumbnailView = Backbone.View.extend({
      template: TemplateUtils.loadTemplate("videoupload-parameters-thumbnail"),

      initialize: function() {
        this.listenTo(this.model, 'change:thumbnail_url', this.render);
      },

      render: function() {
        this.$el.html(this.template(this.model.toJSON()));
        return this;
      },
    });

    var ParameterView = BaseModal.extend({
      template: TemplateUtils.loadTemplate("videoupload-parameters"),
      templateSubtitleForm: TemplateUtils.loadTemplate("videoupload-subtitle-form"),
      templateThumbnailForm: TemplateUtils.loadTemplate("videoupload-thumbnail-form"),

      events: $.extend({}, BaseModal.prototype.events, {
        "submit .upload-subtitles form": "onSubmitSubtitlesForm",
        "submit .upload-thumbnail form": "onSubmitThumbnailForm",
      }),

      options: $.extend({}, BaseModal.prototype.options, {
        title: gettext("Video parameters"),
        modalSize: "med",
        viewSpecificClasses: 'videoupload-parameters view-uploads'
      }),

      initialize: function() {
        // this.model is the current video
        ParameterView.__super__.initialize.apply(this);
        this.buttonTemplate = TemplateUtils.loadTemplate("videoupload-modal-button");

        // Fill subtitles
        this.subtitles = new SubtitleCollection([], {video: this.model});
        this.listenTo(this.subtitles, 'request', this.subtitlesSyncing);
        this.listenTo(this.subtitles, 'sync', this.subtitlesSynced);
        this.listenTo(this.subtitles, 'add', this.addSubtitle);

        this.render();
      },

      cancel: function(event) {
        ParameterView.__super__.cancel.apply(this, event);
        this.remove();
      },

      show: function() {
          ParameterView.__super__.show.apply(this);
          this.subtitles.fetch();
      },

      subtitlesSyncing: function(model_or_collection) {
        if (model_or_collection === this.subtitles) {
            this.$(".subtitles .syncing").show();
            this.$(".subtitles .synced").hide();
        }
      },

      subtitlesSynced: function(model_or_collection) {
        if (model_or_collection === this.subtitles) {
            this.$(".subtitles .syncing").hide();
            this.$(".subtitles .synced").show();
        }
      },

      addSubtitle: function(subtitle) {
        var subtitleView = new SubtitleView({model: subtitle});
        this.$('.subtitles tbody').append(subtitleView.render().el);
      },

      addActionButtons: function() {
        this.addActionButton('cancel', gettext('Close'));
      },

      renderContents: function() {
        ParameterView.__super__.renderContents.apply(this);

        // thumbnail view
        if (false) {
          var thumbnailView = new ThumbnailView({model: this.model});
          this.$(".thumbnail").html(thumbnailView.render().el);
          this.$(".upload-thumbnail").html(this.templateThumbnailForm());
        }// disable thumbnail upload for now

        // subtitle upload forms
        this.$(".upload-subtitles").html(this.templateSubtitleForm());

        // Fill video_id values in both subtitle/thumbnail forms
        this.$("form [name='video_id']").val(this.model.videoId());
      },

      getContentHtml: function() {
        return this.template(this.model.toJSON());
      },

      onSubmitSubtitlesForm: function(e) {
        var that = this;
        $(e.target).ajaxSubmit({
          url: this.subtitles.url(),
          beforeSend: function() {
            deactivateForm(e.target);
          },
          success: function(response) {
            if (response.error) {
              popError(response.error);
            } else {
              that.subtitles.fetch();
            }
          },
          complete: function() {
            reactivateForm(e.target);
          },
        });
      },

      updateThumbnailUrl: function() {
        // Url to which a thumbnail file can be posted
        var url = '${reverse_course("videoupload:video-update_thumbnail", kwargs={"video_id": "videoid"})}';
        return url.replace("videoid", this.model.get("id"));
      },

      onSubmitThumbnailForm: function(e) {
        var that = this;

        $(e.target).ajaxSubmit({
          url: this.updateThumbnailUrl(),
          beforeSend: function() {
            deactivateForm(e.target);
          },
          success: function(response) {
            if (response.error) {
              popError(response.error);
            } else {
              that.model.fetch();
            }
          },
          complete: function() {
            reactivateForm(e.target);
          },
        });
      },
    });

    // Initialize objects
    var Videos = new VideoCollection;
    var VideoUploadForm = new VideoUploadFormView({
        el: $("#videoupload-form"),
        collection: Videos
    });
    var VideoCollectionApp = new VideoCollectionView({
        collection: Videos
    });

  }
);
