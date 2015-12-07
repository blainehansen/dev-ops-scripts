import re
# re.sub(findHookRegex, replFunc, content, 1, re.S)

content = """window.sloyalty.customer_id = '';
Stufff that I %%LNG_verb%% will do
href="%%Panel.stuff%%other/things/that.html"
div %%Snippet_stuff%% matcherererere"""

comparison = """Just


so much other stuff is in here you >>>>? ?

I honestly do think that Stufff that I think will do

href="placeds/other/things/that.html"
	div <a      href="thingy">stuff</a>
	 matcherererere and such things you know??

I mean, it's simply the ting that Stufff that I think will do"""

def lenient(regex):
	regex = re.escape(regex)
	regex = re.sub('\\\\[\s+]', '\s+', regex)
	return regex

findHookRegex = '(?P<prev>.+?)(?P<hook>\%\%.+?\%\%)(?P<next>.+?)(?P<tail>\%\%|$)'

while re.search('\%\%[\w.]+?\%\%', content):
	match = re.search(findHookRegex, content, re.S)
	print match.group('hook')
	print match.group('prev')
	print match.group('next')
	print

	# Use prev and next in a new regex, to look at the comparison and determine what lines up with hook.
	comparisonRegex = lenient(match.group('prev')) + '(?P<desiredContent>.+?)' + lenient(match.group('next'))
	print comparisonRegex
	match = re.search(comparisonRegex, comparison, re.S)
	print match.group('desiredContent')
	print
	desiredContent = match.group('desiredContent')


	replaceHookRegex = '\g<prev>' + desiredContent + '\g<next>\g<tail>'
	content = re.sub(findHookRegex, replaceHookRegex, content, 1, re.S)
	print content