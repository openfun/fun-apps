function build_json_tree(course_tree_data) {
    $('#course-tree').jstree({'core' :
			      {
				  'data': course_tree_data,
				  'themes' : {'name' : 'proton',
					      'responsive' : true}
			      }});
    $('#course-tree').on("activate_node.jstree", get_stats);
    $('#show-left-panel').on("click", show_left_panel);
    $('#hide-left-panel').on("click", hide_left_panel);
    $('#refresh-button').on('click', refresh_stats);
}

var cache = {};
var current_requested_problem = null;
var refreshing_button = null;
    
function get_stats(e, data) {
    if (data.node.li_attr.category == 'problem') {
	display_header(data.node.li_attr.report_url);
	display_footer(data.node.a_attr.href);
	if (data.node.a_attr.href in cache)
	    $('#problem-stat').html(cache[data.node.a_attr.href]);
	else if (!current_requested_problem) {
	    $('#problem-stat').html('');
	    $('#loading-message').css('visibility', 'visible');
	    $.ajax(data.node.a_attr.href).done(display_stats);
	    current_requested_problem = data.node.a_attr.href;
	}
    }
}

function refresh_stats() {
    var refresh_url = $(this).attr('refresh-url');
    if (!current_requested_problem) {
	$(this).button('loading');
	current_requested_problem = refresh_url;
	refreshing_button = $(this);
	$.ajax(refresh_url).done(display_stats);
    }
}

function display_stats(data) {
    $('#loading-message').css('visibility', 'hidden');
    $('#problem-stat').html(data);
    cache[current_requested_problem] = data;
    if (refreshing_button) {
	refreshing_button.button('reset');
	refreshing_button.css('visibility', 'visible');
	refreshing_button = null;
    }
    current_requested_problem = null;
}

function show_left_panel() {
    $('#left-panel').show();
    $('#right-panel').toggleClass('col-xs-8 col-xs-12');
    $('#show-left-panel').css('visibility', 'hidden');
}

function hide_left_panel() {
    $('#left-panel').hide();
    $('#right-panel').toggleClass('col-xs-8 col-xs-12');
    $('#show-left-panel').css('visibility', 'visible');
}

function display_header(report_url) {
    $('#generate-raw-data').attr('href', report_url);
    $('#generate-raw-data').removeAttr('hidden');
}

function display_footer(refresh_url) {
    $('#refresh-button').attr('refresh-url', refresh_url);
    refreshing_button = $('#refresh-button');
}
