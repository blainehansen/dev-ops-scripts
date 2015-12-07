import os
import fnmatch
import bs4
import re
from fuzzywuzzy import fuzz

def getFileContent(path):
	fileObj = open(path, 'rb')
	content = fileObj.read()
	fileObj.close()
	return content

def writeFileContent(path, content):
	fileObj = open(path, 'wb')
	fileObj.write(content)
	fileObj.close()

crawlHtmlFiles = []
for root, dirnames, filenames in os.walk('example_crawled_stage/main_site'):
	for filename in fnmatch.filter(filenames, '*.html*'):
		crawlHtmlFiles.append(os.path.join(root, filename))

# indexContent = getFileContent('/home/place/example/example_crawled_stage/main_site/index.html')
# indexSource = bs4.BeautifulSoup(indexContent, 'lxml')

cssLinks = set()
jsLinks = set()
for htmlFile in crawlHtmlFiles:
	content = getFileContent(htmlFile)
	source = bs4.BeautifulSoup(content, 'lxml')
	tempCssLinks = source.find_all('link', href=re.compile('.+?\.css.*?'))
	# print tempCssLinks
	tempJsLinks = source.find_all('script', src=True)
	# print tempJsLinks

	tempCssLinks = [re.sub('(\?*)?(\w+)?$', '', '%s' % link.attrs['href']) for link in tempCssLinks]
	# print tempCssLinks
	tempJsLinks = [re.sub('(\?*)?(\w+)?$', '', '%s' % link.attrs['src']) for link in tempJsLinks]
	# print tempJsLinks	

	cssLinks.update(tempCssLinks)
	jsLinks.update(tempJsLinks)
	# print cssLinks
	print len(cssLinks)
	# print jsLinks
	print len(jsLinks)
	# break

cssLinks = sorted(cssLinks)
jsLinks = sorted(jsLinks)

cssLinksString = '\n'.join(cssLinks)
print cssLinksString
writeFileContent('cssLinks.txt', cssLinksString)

jsLinksString = '\n'.join(jsLinks)
print jsLinksString
writeFileContent('jsLinks.txt', jsLinksString)

# These two halves of this script, above and below this point, were written and run separately with the other one commented out. This was simply because of the iterative creation cycle.


tempCssLinks = getFileContent('cssLinks.txt').split()
tempJsLinks = getFileContent('jsLinks.txt').split()

cssLinks = set()
jsLinks = set()
for link in tempCssLinks:
	highestRatio = 0
	linkDirname, linkBasename = os.path.split(link)
	
	print 'COMPARING LINK: ', link
	for setLink in cssLinks:
		print '... with: ', setLink
		curDirname, curBasename = os.path.split(setLink)

		if curBasename != linkBasename:
			continue

		curRatio = fuzz.ratio(linkDirname, curDirname)
		print curRatio
		if curRatio > highestRatio: highestRatio = curRatio

	print highestRatio
	if highestRatio < 90: cssLinks.add(link)

for link in tempJsLinks:
	highestRatio = 0
	linkDirname, linkBasename = os.path.split(link)
	
	print 'COMPARING LINK: ', link
	for setLink in jsLinks:
		print '... with: ', setLink
		curDirname, curBasename = os.path.split(setLink)

		if curBasename != linkBasename:
			continue

		curRatio = fuzz.ratio(linkDirname, curDirname)
		print curRatio
		if curRatio > highestRatio: highestRatio = curRatio

	print highestRatio
	if highestRatio < 90: jsLinks.add(link)


cssLinksString = '\n'.join(cssLinks)
print cssLinksString
writeFileContent('cssLinksFinal.txt', cssLinksString)

jsLinksString = '\n'.join(jsLinks)
print jsLinksString
writeFileContent('jsLinksFinal.txt', jsLinksString)