function answers_distribution (static_url, get_answers_url, refresh_string) {
    
    var current_problem_module_id = ''
    
    var ajaxload_tag = "<img src='" + static_url + "course_dashboard/images/ajaxload.gif' class='ajax-load-img' alt='ajax loading button'>";

    $('.problem-path').button().click(get_results);
    
    function get_results(event) {
	
	if ($(this).hasClass('refresh-button'))
	    var problem_module_id = this.parentNode.parentNode.id
	else
	    var problem_module_id = this.parentNode.id
	
	problem_module_selector = '.problem-module#' + problem_module_id

	/*Toggle the chevron and show/hide results*/
	if (!$(this).hasClass('refresh-button')) {
	    if ($(problem_module_selector + ' li.glyphicon').hasClass('glyphicon-chevron-right')) {
		$(problem_module_selector + ' li.glyphicon').removeClass('glyphicon-chevron-right').addClass('glyphicon-chevron-down');
		$(problem_module_selector + ' .results').show();
		$(problem_module_selector + ' .refresh-button').show();
	    }
	    else {
		$(problem_module_selector + ' li.glyphicon').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-right');
		$(problem_module_selector + ' .results').hide();
		$(problem_module_selector + ' .refresh-button').hide();
	    }
	}
	
	/*The ajax request is only done when we first unfold a problem module and when there is no other request going on.
          Then the refresh button is used.*/
	if (current_problem_module_id == '') {
	    if ($(this).hasClass('refresh-button') || !$(problem_module_selector + ' .refresh-button').length) {
	    // perform the request
	    $.get(get_answers_url, {'problem_module_id': problem_module_id}, display_results);
	    // insert ajax load tag
	    $(ajaxload_tag).insertAfter(this) // TODO insert beetween two rows not good
	    // save problem_module_id in order to insert the result of get_answers request in the right module div
	    current_problem_module_id = problem_module_id;
	    }
	}
    }

    function display_results(xml_data) {
	// called after the get_answers/ request has returned
	
	problem_module_selector = '.problem-module#' + current_problem_module_id
	// inject the xml response at the right place
	
	$(problem_module_selector + ' .results').html(xml_data);
	// remove ajaxload button
        $(problem_module_selector + ' .ajax-load-img').remove();
	// inject the refresh button tag if necessary
	if (!$(problem_module_selector + ' .refresh-button').length) {
	    var refreshbutton_tag= "<a class='btn btn-success col-lg-offset-10 refresh-button'>" + refresh_string + "</a>";
	    $(refreshbutton_tag).insertAfter($(problem_module_selector + ' .results'));
	    // bind refresh button to refresh_results
	    $(problem_module_selector + ' .refresh-button').button().click(get_results)
	}
	current_problem_module_id = '';
    }
}
