/* This file is included both in funsite and edx-platorm/lms */

(function() {
    /* select current page menu item */
    var page = window.location.pathname.split('/')[1];
    $('#sandwich-overlay [data-location="'+ page +'"]').addClass('selected');

    /* Handle FUN overlays closing by clicking X */
    $('.close-overlay').on('click', function(event) {
        $('div.sequence-nav').css('z-index', 'auto');
        $(this).closest('.overlay').slideUp();
    });

    /* Sandwich menu overlay */
    $('#sandwich-menu').on('click', function(event) {
        // change z-index of courseware elements which have it set to 'auto'
        $('div.sequence-nav').css('z-index', 1);
        $('nav.sequence-bottom').css('z-index', 1);
        $('#sandwich-overlay').slideDown();
    });

    /* Dropdown menu */
    $('#top-menu .right-nav .toggle-dropdown-menu').on('click', toggleDropdown);

     $('body').click(function() {
     	if ($('#top-menu .fun-dropdown-menu').is(":visible")) {
     	    $('#top-menu .fun-dropdown-menu').slideUp();
     	    toggleAccessiblePopUpAria(false);
     	}
     });

    function toggleDropdown(event) {
        if ($('#top-menu .fun-dropdown-menu').is(":hidden")) {
            $('#top-menu .fun-dropdown-menu').slideDown();
            toggleAccessiblePopUpAria(true);
        }
        else {
            $('#top-menu .fun-dropdown-menu').hide();
            toggleAccessiblePopUpAria(false);
        }
        event.preventDefault();
        event.stopPropagation();
    }

    function toggleAccessiblePopUpAria(display) {
        // aria-haspopup is used to improve accessibility.
        $('#top-menu .right-nav .toggle-dropdown-menu').attr('aria-haspopup', display);
    }
 })();
