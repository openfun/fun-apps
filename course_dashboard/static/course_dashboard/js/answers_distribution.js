function answers_distribution (static_url, get_answers_url, refresh_string) {
    
    var current_problem_module_id = ''
    
    var ajaxload_tag = "<img src='" + static_url + "fun/images/spinner.gif' class='ajax-load-img' alt='ajax loading button'>";
    
    $('.problem-path').button().click(get_results);

    // prevent triggering the get_results call when get-answers button is pressed
    $('.get-answers-button').button().click(function(ev) {ev.stopPropagation();});
    
    function get_results(event) {
	
	var problem_module_id = $(this).parents('.problem-module').attr('id')
	
	problem_module_selector = '.problem-module#' + problem_module_id
	
	/*Toggle the chevron and show/hide results*/
	if (!$(this).hasClass('refresh-button')) {
	    if ($(problem_module_selector + ' span.glyphicon').hasClass('glyphicon-chevron-right')) {
		$(problem_module_selector + ' span.glyphicon').removeClass('glyphicon-chevron-right').addClass('glyphicon-chevron-down');
		$(problem_module_selector + ' .results').show();
	    }
	    else {
		$(problem_module_selector + ' span.glyphicon').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-right');
		$(problem_module_selector + ' .results').hide();
	    }
	}

	/*The ajax request is only done when we first unfold a problem module and when there is no other request going on.
          Then the refresh button is used.*/
	if (current_problem_module_id == '') {
	    if ($(this).hasClass('refresh-button') || !$(problem_module_selector + ' .refresh-button').length) {
		// perform the request

		$.get(get_answers_url, {'problem_module_id': problem_module_id}, display_results);

		// insert ajax load tag at the right place
		$(problem_module_selector + ' .results .control .data-results').append(ajaxload_tag);

		// save problem_module_id in order to insert the result of get_answers request in the right module div
		current_problem_module_id = problem_module_id;
	    }
	}
    }

    function display_results(xml_data) {
	// called after the get_answers/ request has returned

	problem_module_selector = '.problem-module#' + current_problem_module_id
	
	// inject the xml response at the right place
	$(problem_module_selector + ' .results .data').html(xml_data);
	
	// remove ajaxload button
        $(problem_module_selector + ' .ajax-load-img').remove();
	
	// inject the refresh button tag if necessary
	if (!$(problem_module_selector + ' .refresh-button').length) {
	    var refreshbutton_tag= "<a class='btn btn-success refresh-button'>" + refresh_string + "</a>";
	    $(problem_module_selector + ' .results .control .data-results').html(refreshbutton_tag)
	    $(refreshbutton_tag).insertAfter($(problem_module_selector + ' .results.buttons'));
	    // bind refresh button to refresh_results
	    $(problem_module_selector + ' .refresh-button').button().click(get_results)
	}
	
	current_problem_module_id = '';
    }


    // toggle the color of a problem path when we put the mouse hover it
    // couldn't achieve this using the css :hover method since two
    // different elements need to change color simultaneously.
    $('.problem-path').hover(handler_in, handler_out)
    
    function handler_in() {
	$(this).css('background-color', '#EEEEEE')
	$(this.getElementsByClassName('breadcrumb')).css('background-color','#EEEEEE')
    }
    function handler_out() {
	$(this).css('background-color', '#E9E9E9')
	$(this.getElementsByClassName('breadcrumb')).css('background-color','#E9E9E9')
    }
}
