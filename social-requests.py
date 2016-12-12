import requests
from requests_oauthlib import OAuth1

import json

import MySQLdb

from bs4 import BeautifulSoup

from selenium import webdriver

import re

db = MySQLdb.connect(host="databaseserver", user="root", passwd="secretpassword", db="sr_wordpress")

instagramCommand = """SELECT wp_posts.post_title, wp_postmeta.meta_value 
FROM wp_posts INNER JOIN wp_postmeta 
on wp_posts.ID = wp_postmeta.post_id 
WHERE post_type = 'gear-guide-brand' 
AND wp_postmeta.meta_key = 'instagram_name'"""

twitterCommand = """SELECT wp_posts.post_title, wp_postmeta.meta_value 
FROM wp_posts INNER JOIN wp_postmeta 
on wp_posts.ID = wp_postmeta.post_id 
WHERE post_type = 'gear-guide-brand' 
AND wp_postmeta.meta_key = 'twitter_name'"""

cursor = db.cursor()
cursor.execute(instagramCommand)
instagramNames = filter((lambda x: x[1]), cursor.fetchall())
instagramNames = [pair[1] for pair in instagramNames]


cursor.execute(twitterCommand)
twitterNames = filter((lambda x: x[1]), cursor.fetchall())
twitterNames = [pair[1] for pair in twitterNames]


db.close()


# Twitter pull

auth = OAuth1('various', 'secret', 'twitter', 'keys')
defaultParams = {'count': '4', 'trim_user': 'true', 'include_rts': 'true',
	'exclude_replies': 'true', 'contributer_details': 'false'}

totalTweets = {}

# for list of accounts
for account in twitterNames:
	# grab an array of the relevant info of each of their tweets
	newParams = {'screen_name': account}
	params = dict(defaultParams.items() + newParams.items())
	r = requests.get('https://api.twitter.com/1.1/statuses/user_timeline.json', params=params, auth=auth)
	tweetArray = r.json()

	params = {'include_entities': 'false', 'screen_name': account}
	r = requests.get('https://api.twitter.com/1.1/users/show.json', params=params, auth=auth)
	user = r.json()

	# put that array in a dict under their screenname
	totalTweets[account] = {'tweets': tweetArray, 'user': {'name': user['name'], 'profile_image_url': user['profile_image_url']}}
	

# save that entire dict to json at the appropriate place
with open('/skiracing.com/relvant/path/brandTweets.json', 'w') as outfile:
	json.dump(totalTweets, outfile)


# Instagram pull

totalGrams = {}

driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])

# for list of instagramNames
for account in instagramNames:
	# grab page source
	driver.get("https://www.instagram.com/%s/" % account)
	
	# get list of shortcodes
	soup = BeautifulSoup(driver.page_source, 'html.parser')

	regexPattern = '/p/(\w+)/$'
	# cut list to 6 or whatever
	instagramLinks = soup.article.find_all('a', href=re.compile(regexPattern), limit=4)
	instagramLinks = [re.search(regexPattern, link.get('href')).group(1) for link in instagramLinks]


	accountGrams = []
	for link in instagramLinks:
		# grab image with request
		r = requests.get('https://instagram.com/p/%s/media/?size=l' % link)
		accountGrams.append(r.url)

	totalGrams[account] = accountGrams

driver.close()


with open('/skiracing.com/relvant/path/brandGrams.json', 'w') as outfile:
	json.dump(totalGrams, outfile)