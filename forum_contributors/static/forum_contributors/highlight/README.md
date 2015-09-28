Mardown Editor Fork
----

This is a fork of edX's Markdown editor to add highlight features, used in lms forum (although the editor may be used somewhere else, the CSS modification, only works for forum for now).

One dash for yellow hightlight and two for blue.

	-yellow highlight-
    --blue highlight--


The modifications to original Editor consists of: 
	- Changing the 3 images for toolbar buttons
	- Adding some functions in 3 js files, and shift icons toolbar 40px right to make room for 2 new buttons. 
    -Override some CSS to use our image, see `themes/fun/static/sass/_fun.scss``

See:

	diff edx-platform/lms/static/js/Markdown.Editor.js themes/fun/static/highlight/js/Markdown.Editor.js
    diff edx-platform/lms/static/js/Markdown.Converter.js themes/fun/static/highlight/js/Markdown.Converter.js
    diff edx-platform/lms/static/js/Markdown.Sanitizer.js themes/fun/static/highlight/js/Markdown.Sanitizer.js
    

