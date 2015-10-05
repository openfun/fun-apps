(function() {

    // Handle FUN overlays closing by hiting escape
    $(document).keydown(function(event) {
        if (event.keyCode == 27) { // ESC key
            $('.hide-on-escape-key:visible').hide();
        }
    });

    /* Handle FUN overlays closing by clicking X */
    $('.close-overlay').on('click', function(event) {
        $(this).parent().hide()
    });

    /* Sandwich menu overlay */
    $('#sandwich-menu').on('click', function(event) {
        $('#sandwich-overlay').show();
    });

    /* Login overlay */
    $('#top-menu .login.not-connected').on('click', function(event) {
        $('#login-overlay').show();
    });

    $('#login-form').on('submit', function(event) {
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
                    $('#login-overlay').find('input').addClass('loginerror');
                    $('#login-overlay').find('.error').html(json.value)
                }

            },
            error: function(response) {
                $('#login-overlay').find('input').addClass('loginerror');
                $('#login-overlay').find('.error').html(gettext("Your request could not be completed. Please try again"));
            }
        });
    })

})();
