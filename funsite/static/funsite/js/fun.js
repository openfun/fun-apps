(function() {
    var form_origin_position;

    // select current page menu item
    var page = window.location.pathname.split('/')[1];
    $('#sandwich-overlay [data-location="'+ page +'"]').addClass('selected');

    /* Login overlay */
    $('#top-menu .right-header .login-link').on('click', function(event) {
        $('#login-overlay').toggle();
        if ($('#login-overlay').is(':visible')) {
            $('#login-overlay input[name="email"]').focus();
        }
    });

    /* Handle search course global widget */
    $('#search-site').keyup(function(event) {
        var pattern = $(this).val();
        if (pattern != '') {
            if (event.keyCode == 13) {
                window.location.href = '/cours/#filter?page=1&rpp=50&query=' + pattern;
            }
        }
    });

    /* Handle search course global widget */
    $('#search-site').keyup(function(event) {
        var pattern = $(this).val();
        if ((window.location.pathname == '/cours/') || ((pattern != '') && (event.keyCode == 13))) {
            window.location.href = '/cours/#filter?page=1&rpp=50&query=' + pattern;
        }
    });

    function getParameterByName(name) {
        // Retrieve query parameters in url using hash character:
        // /cours/#filter?page=1&rpp=50&query=test
        url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) {return null;}
        if (!results[2]) {return '';}
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    if (window.location.pathname == '/cours/') {
        // when on course list page this will set search widget to current search value is any
        $('#search-site').val(getParameterByName('query'))
    }

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
