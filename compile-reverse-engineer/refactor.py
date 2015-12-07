import os
import re
import fnmatch
import bs4

# Go through each top level file, replacing every Panel, Snippet, and Asset.

srcDirName = './example_raw/main_site/'
destDirName = './example_processed/main_site/'
crawlDirName = './example_crawled_stage/main_site/'

def prettyHtml(html):
	soup = BeautifulSoup(html, 'lxml')
	return soup.prettify()

def getFileContent(path):
	fileObj = open(path, 'rb')
	content = fileObj.read()
	fileObj.close()
	return content

def panelReplace(match):
	panelName = match.group('panelName')
	return getFileContent(srcDirName + 'Panels/' + panelName + '.html')

def snippetReplace(match):
	snippetName = match.group('snippetName')
	try:
		return getFileContent(srcDirName + 'Snippets/' + snippetName + '.html')
	except:
		print "failure with snippet name: " + snippetName

	try:
		return getFileContent(srcDirName + 'Snippets/' + snippetName + 'Item.html')
	except:
		print "failure with snippet name: " + snippetName + 'Item.html'

	try:
		return getFileContent(srcDirName + 'Snippets/' + re.sub('s$', '', snippetName) + '.html')
	except:
		print "failure with snippet name: " + re.sub('s$', '', snippetName) + '.html'
		return "\%\SNIPPET_" + snippetName + "\%"

def assetReplace(match):
	assetName = match.group('assetName')
	print assetName
	return srcDirName + assetName

def staticContent(content):
	# while re.search('\%\%(Panel\.).+?\%\%', content):
	# while re.search('\%\%(Panel\.|SNIPPET_).+?\%\%', content):
	while re.search('\%\%(Panel\.|SNIPPET_|Asset_)\w+?\%\%', content):
		# print bool(re.search('\%\%(Panel\.).+?\%\%', content))
		print 'panels'
		content = re.sub('\%\%Panel\.(?P<panelName>\w+?)\%\%', panelReplace, content)
		print 'snippets'
		content = re.sub('\%\%SNIPPET_(?P<snippetName>\w+?)\%\%', snippetReplace, content)
		print 'assets'
		content = re.sub('\%\%Asset_(?P<assetName>\w+?)\%\%', assetReplace, content)

	return content		


def arrayContentsSame(array):
    return all(x == array[0] for x in array)

def stripParens(hook):
	return re.sub('%', '', hook)

def lenient(regex):
	regex = re.escape(regex)
	regex = re.sub('\\\\[\s+]', '\s*', regex)
	return regex

crawlHtmlFiles = []
for root, dirnames, filenames in os.walk(crawlDirName):
	for filename in fnmatch.filter(filenames, '*.html'):
		crawlHtmlFiles.append(os.path.join(root, filename))

# crawlTrees = []
# for crawlContent in crawlHtmlFiles:
# 	crawlTrees.append(bs4.BeautifulSoup(crawlContent, 'lxml'))

findHookRegex = '(?P<prev>.+?)(?P<hook>\%\%[\w.]+?\%\%)(?P<next>.+?)(?P<tail>\%\%|$)'
def naiveDynamicContent(content):
	# We're given content, and for each hook we have to scan over all the crawled files to look for that content
	while re.search('\%\%[\w.]+?\%\%', content):
		match = re.search(findHookRegex, content, re.S)
		hook = match.group('hook')
		# print hook
		# print
		comparisonRegex = lenient(match.group('prev')) + '(?P<desiredContent>.*?)' + lenient(match.group('next'))
		
		# for each file in the crawled content:
		comparisonDesiredArray = []
		for crawlFileName in crawlHtmlFiles:
			crawlFileContent = getFileContent(crawlFileName)

			# Use prev and next in a new regex, to look at the comparison and determine what lines up with hook.
			match = re.search(comparisonRegex, crawlFileContent, re.S)
			if match:
				# print match.group('desiredContent')
				# print
				comparisonDesiredArray.append(match.group('desiredContent'))

		if len(comparisonDesiredArray) == 0:
			desiredContent = '{{%s}}' % stripParens(hook)
			print "FAILURE", hook
			print
		elif len(comparisonDesiredArray) == 1 or arrayContentsSame(comparisonDesiredArray):
			desiredContent = comparisonDesiredArray[0]
			print "SUCCESS", hook, desiredContent
			print
		else:
			desiredContent = comparisonDesiredArray[0]
			print "CONFLICT", hook, comparisonDesiredArray
			print

		replaceHookRegex = '\g<prev>' + desiredContent + '\g<next>\g<tail>'
		content = re.sub(findHookRegex, replaceHookRegex, content, 1, re.S)
		# break # not this time right now

	return content


def attrsHaveHooks(tag):
	attrs = tag.attrs
	keyHas = False
	valueHas = False
	for key, value in attrs.iteritems():
		keyHas = re.search('\%\%[\w.]+?\%\%', key) or keyHas
		if not isinstance(value, list):
			valueHas = re.search('\%\%[\w.]+?\%\%', value) or valueHas

	return keyHas or valueHas

def hasId(tag):
	return tag.has_attr('id') #or tag.has_attr('class')

def nonHookAttrs(attrs):
	removeKeys = []
	for key, value in attrs.iteritems():
		if isinstance(value, list):
			continue
			# for item in value:
			# 	if re.search('\%\%[\w.]+?\%\%', item)
		elif re.search('\%\%[\w.]+?\%\%', key) or re.search('\%\%[\w.]+?\%\%', value):
			removeKeys.append(key)
	for key in removeKeys:
		del attrs[key]
	return attrs

def parserDynamicContent(content):
	# at block level. in between complete tags. these are strings or contents in bs4 parlance.
	# Go through the raw, finding all tags with hooks in their strings

	# at attribute level. Either forming a complete attribute, or in the value of an attribute. Or just broken entirely.
	# Go through the raw, finding all tags with hooks in their attrs.
	raw = bs4.BeautifulSoup(content, 'lxml')
	hookAttrTags = raw.find_all(nonHookAttrs)
	# Go through each of those tags,
	for tag in hookAttrTags:
		# and if it doesn't have enough identifying information (almost certainly id)
		if not tag.id:
			# then we find the closest parent that does.
			tag = tag.find_parent(hasId)

		# look through the crawl for that same identifying tag.
		for crawlContent in crawlHtmlFiles:
			crawl = bs4.BeautifulSoup(crawlContent, 'lxml')
			# Gather it's name, id, and non-hook attrs
			tags = crawl.find_all(tag.name, id=tag.id, attrs=nonHookAttrs(tag.attrs))

		# Gather the resolutions to the attrs
		# the resolutions in this situation are simply a correct attr mix. The tags have to be the same in every detail though. The tricky part of this is that we can't at this point guarantee that they can be the same at the string level. The tags can be the same, but the strings could be different for semantic reasons.
		# 	push the data attribute you're looking for to an array. 
			



# iterate through top level files
for srcName in os.listdir(srcDirName):
	print srcName
	srcPath = srcDirName + srcName
	destPath = destDirName + srcName

	# for each file, open and scan its content
	content = getFileContent(srcPath)

	# regex it's content, replacing each match with its appropriate static form.
	content = staticContent(content)
	# content = naiveDynamicContent(content)
	# content = parserDynamicContent(content)
	print prettyHtml(content).encode('utf-8')

	# write back to the file with the new iterated content
	break # we don't actually want to do any real writing yet
	destFileObj = open(destPath, 'wb')
	destFileObj.write(content)
	destFileObj.close()