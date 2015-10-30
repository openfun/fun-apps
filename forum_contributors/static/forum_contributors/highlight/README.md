Mardown Editor Fork
----

This is a fork of edX's Markdown editor to add highlight features, used in lms forum (although the editor may be used somewhere else, the CSS modification, only works for forum for now).

One dash for yellow hightlight and two for blue.

	-yellow highlight-
    --blue highlight--


Modifications to original Editor consist of: 
	- Changing the 3 images for toolbar buttons
	- Adding some functions in 3 js files, and shift icons toolbar 40px right to make room for 2 new buttons. 
    - Override some CSS to use our image
        + highlight.scss is compiled using command: `scss highlight.scss --update`
        + then added to CSS pipeline in our settings


See:

	diff ~/edx-platform/lms/static/js/Markdown.Editor.js ~/fun-apps/forum_contributors/static/forum_contributors/highlight/js/Markdown.Editor.js
    diff ~/edx-platform/lms/static/js/Markdown.Converter.js ~/fun-apps/forum_contributors/static/forum_contributors/highlight/js/Markdown.Converter.js
    diff ~/edx-platform/lms/static/js/Markdown.Sanitizer.js ~/fun-apps/forum_contributors/static/forum_contributors/highlight/js/Markdown.Sanitizer.js
    

