function answers_distribution (static_url, get_answers_url, refresh_string) {

    var current_module_id = ''
    $('.problem-path').button().click(function(event) {

	var module_id = this.getAttribute("module-id");
	
	var ajaxload_tag = "<img class='" + module_id + "' src='" + static_url + "course_dashboard/images/ajaxload.gif' alt='ajax loading button' >";

	/*Toggle the chevron and show/hide results*/
	if ($('li.' + module_id).hasClass('glyphicon-chevron-right')) {
	    $('li.' + module_id).removeClass('glyphicon-chevron-right').addClass('glyphicon-chevron-down');
	    $('#' + module_id).show();
	    $('[button-id=' + module_id +']').show();	    
	 }
	else {
	    $('li.' + module_id).removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-right');
            $('#' + module_id).hide();
	    $('[button-id=' + module_id +']').hide();	    
	}
	
	/*The ajax request is only done when we first unfold a problem module.
          Then the refresh button is used.*/
	if (this.getAttribute('clicked') == 'false' &&  current_module_id == '') {
	    // perform the request
	    $.get(get_answers_url, {'problem_module_id': module_id}, display_results);
	    // insert ajax load tag
	    $(ajaxload_tag).insertAfter(this)
	    // save module_id in order to insert the result of get_answers request in the right module div
	    current_module_id = module_id;
	}
    });

    function display_results(xml_data) {
	// called after the get_answers/ request has returned
	var problem_module = $('[module-id='+ current_module_id +']')
	
	// inject the xml response at the right place
	$('#' + current_module_id).html(xml_data);
	// remove ajaxload button
        $('img.' + current_module_id).remove();
	// inject the refresh button tag if necessary
	if (problem_module.attr('clicked') == 'false'){
	    var refreshbutton_tag= " <a class='btn btn-success col-lg-offset-10' button-id='" + current_module_id +"'>" + refresh_string + "</a>";
	    $(refreshbutton_tag).insertAfter('#' + current_module_id);
	    problem_module.attr('clicked' , 'true');
	    // bind refresh button to refresh_results
	    $('a.btn').button().click(refresh_results)
	}
	current_module_id = '';
    }

    function refresh_results(event) {
	module_id = this.getAttribute('button-id');
lol
	var ajaxload_tag = "<img class='" + module_id + "' src='" + static_url + "course_dashboard/images/ajaxload.gif' alt='ajax loading button' >";
	if (current_module_id == '') {
	    $.get(get_answers_url, {'problem_module_id': module_id}, display_results);
	    current_module_id = module_id;
	    $(ajaxload_tag).insertAfter(this);
	}
    }
};

