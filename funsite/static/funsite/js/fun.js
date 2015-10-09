(function() {
    var form_origin_position;
    // Handle FUN overlays closing by hiting escape
    $(document).keydown(function(event) {
        if (event.keyCode == 27) { // ESC key
            $('div.sequence-nav').css('z-index', 'auto');
            $('nav.sequence-bottom').css('z-index', 'auto');
            $('.hide-on-escape-key:visible').hide();
        }
    });

    // select current page menu item
    var page = window.location.pathname.split('/')[1];
    $('#sandwich-overlay [data-location="'+ page +'"]').addClass('selected');

    /* Handle FUN overlays closing by clicking X */
    $('.close-overlay').on('click', function(event) {
        $('div.sequence-nav').css('z-index', 'auto');
        $(this).parent().hide()
    });

    /* Sandwich menu overlay */
    $('#sandwich-menu').on('click', function(event) {
        // change z-index of courseware elements which have it set to 'auto'
        $('div.sequence-nav').css('z-index', 1);
        $('nav.sequence-bottom').css('z-index', 1);
        $('#sandwich-overlay').show();
    });
    /* Login overlay */
    $('#top-menu .login.not-connected').on('click', function(event) {
        $('#login-overlay').toggle();
        if ($('#login-overlay').is(':visible')) {
            $('#login-overlay input[name="email"]').focus();
        }
    });

    $('.login-form').on('submit', function(event) {
	if ($(this).hasClass("login-form-page")) {
	    form_origin_position = "login-page";
	}
	else {
	    form_origin_position = "overlay";
	}
        event.preventDefault();
        $.ajax({
            url: '/login_ajax',
            method: 'POST',
            data: $(this).serialize(),
            success: function(json){
                if (json.success) {
                    var u = decodeURI(window.location.search);
                    var next = u.split("next=")[1];
                    if (next != undefined) {
                        // if next is undefined, decodeURI returns "undefined" causing a bad redirect.
                        next = decodeURIComponent(next);
                    }
                    if (next && !isExternal(next)) {
                        location.href=next;
                    }  else if (json.redirect_url) {
                        location.href=json.redirect_url;
                    } else {
                        location.href="/dashboard";
                    }
                } else if (json.hasOwnProperty('redirect')) {
                    var u = decodeURI(window.location.search);
                    if (!isExternal(json.redirect)) { // a paranoid check.  Our server is the one providing json.redirect
                        location.href=json.redirect+u;
                    } // else we just remain on this page, which is fine since this particular path implies a login failure
                // that has been generated via packet tampering (json.redirect has been messed with).
                } else {
		    if (form_origin_position == "overlay") {
			$('#login-overlay').find('input').addClass('loginerror');
			$('#login-overlay').find('.error').html(json.value);
		    }
		    else {
			$('.login-row').find('.form-group').addClass('has-error');
			var error_div = $('.login-form-page').find('.error-login-page');
			error_div.html(json.value);
			error_div.addClass('alert alert-danger');
		    }
                }
            },
            error: function(response) {
                $('#login-overlay').find('input').addClass('loginerror');
                $('#login-overlay').find('.error').html(gettext("Your request could not be completed. Please try again"));
            }
        });
    })

    $('#pwd_reset_form').on('submit', function(event) {
        event.preventDefault();
        $.ajax({ url: 'password_reset/',
                 method: 'POST',
                 data: $(this).serialize(),
                 success: onSuccessPasswordReset,
               });
    });

    function onSuccessPasswordReset(html) {
        $('#modal-forget-password .modal-header .modal-title').html($('.modal-header').data().success);
	$('#modal-forget-password .modal-body').html($('.modal-body').data().success);
    }
})();
