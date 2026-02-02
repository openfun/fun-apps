(function() {
    var form_origin_position;

    // select current page menu item
    var page = window.location.pathname.split('/')[1];
    $('#sandwich-overlay [data-location="'+ page +'"]').addClass('selected');

    /* Login overlay / Keycloak
     *
     * Expected behaviour:
     * - on the LMS login page (/login...), the red "Connexion" button
     *   must redirect directly to /keycloak-login (SSO), without opening the overlay.
     * - on other pages (FUN / marketing site), we keep the existing overlay behaviour.
     */
    // Use event delegation to ensure the event is attached even if the element doesn't exist yet
    $(document).on('click', '#top-menu .right-header .login-link', function(event) {
        var path = window.location.pathname || '';
        var href = $(this).attr('href') || '';
        var host = window.location.hostname || '';

        // 1) LMS login pages: /login and /login?next=/account/settings
        //    → redirect current tab to /keycloak-login (SSO)
        if (path.indexOf('/login') === 0) {
            event.preventDefault();
            event.stopImmediatePropagation(); // Prevent other handlers from executing
            event.stopPropagation();
            window.location.href = '/keycloak-login';
            return false;
        }

        // 2) Other LMS pages (e.g. /courses/...) with a login link pointing to /login
        //    → open /keycloak-login in a new tab AND refresh the current page
        //    We restrict this behaviour to LMS hostnames to avoid touching the marketing site.
        var isLmsHost = (
            host.indexOf('lms.') === 0 ||                 // lms.preprod-fun.apps.openfun.fr
            host === 'localhost'                          // local dev (nginx on 8073)
        );
        if (isLmsHost && href && href.indexOf('/login') !== -1) {
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();

            // Open Keycloak login in a new tab
            window.open('/keycloak-login', '_blank');
            // Refresh current page to keep it in sync (user will still be anonymous here)
            window.location.reload();
            return false;
        }

        // 3) Historical behavior: open/close overlay on the FUN marketing site
        //    This only applies when href is '#' (overlay trigger).
        if (href === '#' || !href) {
            event.preventDefault();
            $('#login-overlay').toggle();
            if ($('#login-overlay').is(':visible')) {
                $('#login-overlay input[name=\"email\"]').focus();
            }
            return false;
        }

        // 4) Fallback: let the browser handle the click normally
        return true;
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
        $('#search-site').val(getParameterByName('query'));
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
                    if (next !== undefined) {
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
    });

    $('#pwd_reset_form').on('submit', function(event) {
        event.preventDefault();
        $.ajax({ url: '/password_reset/',
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
