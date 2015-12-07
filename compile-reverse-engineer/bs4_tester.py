import bs4
import re

def getFileContent(path):
	fileObj = open(path, 'rb')
	content = fileObj.read()
	fileObj.close()
	return content

def tagHasHook(tag):
	return re.search('\%\%[\w.]+?\%\%', tag.string)

def attrsHaveHooks(tag):
	attrs = tag.attrs
	keyHas = False
	valueHas = False
	for key, value in attrs.iteritems():
		keyHas = re.search('\%\%[\w.]+?\%\%', key) or keyHas
		if not isinstance(value, list):
			valueHas = re.search('\%\%[\w.]+?\%\%', value) or valueHas

	return keyHas or valueHas

def hasIdOrClass(tag):
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

unfilled = """<div class="sloyalty-loyalty-widget"
     data-key="88401b58-d219-4596-bf1d-7e4e2a3460cd"
     data-shop="www.lamav.com"
     data-version="3"
     data-widget-css=""
     data-overlay-css=""
     data-customer="%%GLOBAL_CurrentCustomerID%%"
     data-email="%%GLOBAL_CurrentCustomerEmail%%"></div>"""

messyAttr = """<div>
	<a %%Thing.whatever%% href="thing.html">various stuff</a>
</div>
"""

# rawContent = getFileContent('./lamav_raw/main_site/Panels/ChooseShippingProvider.html')
# crawlContent = getFileContent('./lamav_crawled_stage/main_site/blog/tag/Organic+Face+Wash.html')

# raw = bs4.BeautifulSoup(rawContent, 'lxml')
# crawl = bs4.BeautifulSoup(crawlContent, 'lxml')
# # print raw.prettify()
# hookTags = raw.find_all(attrsHaveHooks)

# print hookTags

# for tag in hookTags:
#      print tag.name, tag.attrs
#      print tag.find_parent(hasIdOrClass).prettify()
#      print
#      print

messy = bs4.BeautifulSoup(unfilled, 'lxml')
hookTags = messy.find_all(attrsHaveHooks)
for tag in hookTags:
	print nonHookAttrs(tag.attrs)