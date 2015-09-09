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

require(["jquery", "underscore", "backbone", "gettext", "js/utils/templates", "js/views/modals/base_modal", "js/views/feedback_notification"],
  function ($, _, Backbone, gettext, TemplateUtils, BaseModal, NotificationView) {

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
    // pending -> preparing -> prepared -> uploading -> uploaded -> creating -> created -> processing -> ready -> published -> deleted
    var Video = Backbone.Model.extend({
      defaults: {
        created_at: "",
        embed_url: "",
        error: "",
        progress: null,
        title: "",
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
    var Videos = new VideoCollection;

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
        this.request = null;
        this.listenTo(this.model, 'change', this.render);
        this.listenTo(this.model, 'change:title', this.changeTitle);
        this.listenTo(this.model, 'sync', this.modelSynced);
        this.listenTo(this.model, 'destroy', this.remove);
        this.listenTo(this.model, 'status-preparing', this.getUploadUrl);
        this.listenTo(this.model, 'status-prepared', this.uploadFile);
        this.listenTo(this.model, 'status-uploaded', this.createVideo);
        this.listenTo(this.model, 'status-publishing', this.publishVideo);
        this.listenTo(this.model, 'status-unpublishing', this.unpublishVideo);

        if (this.model.get('status') === 'pending') {
          this.model.setStatus("preparing");
        }
      },

      render: function() {
        var values = this.model.toJSON();
        if (!values.id) {
            values.id = "";
        }
        this.$el.html(this.template(values));
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
        if (this.request) {
          this.request.abort();
          this.model.destroy();
        }
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

      getUploadUrl: function() {
        var that = this;
        $.getJSON('${reverse_course("videoupload:upload-url")}',
          function(data) {
            that.model.setStatus("prepared", data.upload_url);
          }
        );
      },

      uploadFile: function(uploadUrl) {
        var formData = new FormData();
        formData.append("file", this.model.get("file"))

        var that = this;
        ajaxSettings.unsetHeaders();
        ajaxSettings.unsetNotify();
        this.request = $.ajax({
          url: uploadUrl,
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
                var percent = event.loaded * 100. / event.total;
                that.uploadingProgress(percent);
              }
            });
            return xhr;
          },
          beforeSend: function() {
            that.model.setStatus("uploading");
          },
          success: function(data){
            if (data.error) {
              that.model.setError(data.error)
            } else {
              that.model.setStatus("uploaded", data.url);
            }
          },
          error: function(jqXHR, textStatus, errorThrown) {
            that.model.setError(errorThrown);
          },
        });
      },

      createVideo: function(url) {
        ajaxSettings.resetHeaders();
        ajaxSettings.unsetNotify();
        var that = this;
        $.ajax({
          url: '${reverse_course("videoupload:create-video")}',
          data: {
            title: that.model.get("title"),
            url: url,
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
        this.listenTo(Videos, 'add', this.addOne);
        this.listenTo(Videos, 'syncError', this.syncError);
        this.render();
        Videos.fetch();
      },

      render: function() {
        this.$el.html(this.template());
        return this;
      },

      addOne: function(video) {
        var videoView = new VideoView({model: video});
        // Note that this will always display the newest elements first.
        this.$('tbody').prepend(videoView.render().el);
      },

      syncError: function(error) {
        popError(error);
      },
    });
    var VideoCollectionApp = new VideoCollectionView;

    var VideoUploadFormView = Backbone.View.extend({
      el: $("#videoupload-form"),

      events: {
        "click button": "onChooseFile",
        "change input": "onFileChosen",
      },

      onChooseFile: function(e) {
        e.preventDefault();
        this.$("input").click();
      },

      onFileChosen: function(e) {
        for(var i=0; i < e.target.files.length; i++) {
          Videos.add(new Video({
            title: e.target.files[i].name,
            file: e.target.files[i],
            status: "pending"
          }));
        }
      }
    });
    var VideoUploadForm = new VideoUploadFormView;


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

        // Fill subtitles
        this.subtitles = new SubtitleCollection([], {video: this.model});
        this.listenTo(this.subtitles, 'add', this.addSubtitle);
        this.subtitles.fetch();
      },

      cancel: function(event) {
        ParameterView.__super__.cancel.apply(this, event);
        this.remove();
      },

      addSubtitle: function(subtitle) {
        var subtitleView = new SubtitleView({model: subtitle});
        this.$('.subtitles').append(subtitleView.render().el);
      },

      addActionButtons: function() {
        this.addActionButton('cancel', gettext('Close'));
      },

      renderContents: function() {
        ParameterView.__super__.renderContents.apply(this);

        // thumbnail view
        var thumbnailView = new ThumbnailView({model: this.model});
        this.$(".thumbnail").html(thumbnailView.render().el);

        // subtitle/thumbnail upload forms
        this.$(".upload-subtitles").html(this.templateSubtitleForm());
        this.$(".upload-thumbnail").html(this.templateThumbnailForm());

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
  }
);
