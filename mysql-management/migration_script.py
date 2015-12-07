import argparse
import subprocess
import sys
import string
import datetime
import socket

def ensure_path (path):
	if path:
		if path[-1] != '/':
			return path + '/'
		else:
			return path
	return path

# Setup Area

parser = argparse.ArgumentParser(description='Migration Script')
parser.add_argument('--mode', default='server', choices=['local', 'server', 'both'],
	help='Choose the operation mode. ' +
	'local updates the local installation. server updates the dev installation. both updates both. Default is server.')

parser.add_argument('-a', dest='archive', default='archived_dumps/', help='archive directory path')
parser.add_argument('--appendage', dest='appendage', default='', help='a string to use in the filename, after the date')
# parser.add_argument('-s', help='search text')
# parser.add_argument('-r', help='replace text')

parser.add_argument('--server-user', dest='serverUser', default='root', help='mysql user on the server')
parser.add_argument('--server-password', dest='serverPassword', help='mysql password on the server')
parser.add_argument('--local-user', dest='localUser', default='root', help='local mysql user')
parser.add_argument('--local-password', dest='localPassword', help='local mysql password')

parser.add_argument('--local-path', dest='localPath', default='./',
	help='if local is being updated, where to put the dump file locally')
parser.add_argument('--image-path', dest='imagePath', default='/var/www/sr/wp-content/uploads/',
	help='if local is being updated, the directory to sync with the remote image directory')
parser.add_argument('--local-database', dest='localDatabase', default='sr_wordpress',
	help='if local database is being updated, the database to use')
parser.add_argument('--server-database', dest='serverDatabase', default='sr_wordpress_dev',
	help='if server database is being updated, the database to use')

parser.add_argument('--dry-run', dest='dryRun', action='store_true',
	help='Does a dry run. Doesn\'t migrate the database or sync image files.')


args = vars(parser.parse_args())

mode = args['mode']
archive = ensure_path(args['archive'])
appendage = args['appendage']

serverUser = args['serverUser']
localUser = args['localUser']
serverPassword = args['serverPassword']
serverPasswordOption = '-p' + serverPassword if serverPassword else ''
localPassword = args['localPassword']
localPasswordOption = '-p' + localPassword if localPassword else ''

localPath = ensure_path(args['localPath'])
imagePath = ensure_path(args['imagePath'])
serverDatabase = args['serverDatabase']
localDatabase = args['localDatabase']

dryRun = args['dryRun']

def command (string):
	print string
	if not dryRun: subprocess.call([string], shell=True)


# Actual Execution

# First, we create the dump. This happens the same no matter where we are or what mode we're in.
# Needs to happen on the database server.

serverReqFromLocal, serverReqFromServer, localReqFromLocal, localReqFromServer = False, False, False, False

location = socket.gethostname()
if location == 'example.com':
	serverReqFromServer = mode in ('server', 'both')
	localReqFromServer = mode in ('local', 'both')
elif location != 'db.new.example.com':
	serverReqFromLocal = mode in ('server', 'both')
	localReqFromLocal = mode in ('local', 'both')
else:
	parser.error("on the db server")


dateString = str(datetime.datetime.now()).replace(' ', '_') + appendage

sqlFileName = dateString + '.sql'
zipFileName = dateString + '.tar.gz'

serverSqlPath = archive + sqlFileName
serverZipPath = archive + zipFileName


command("ssh root@databaseserver 'mysqldump -u%s %s sr_wordpress > %s'" % (serverUser, serverPasswordOption, serverSqlPath))
command("ssh root@databaseserver 'tar -cvzf %s %s'" % (serverZipPath, serverSqlPath))


if serverReqFromServer:
	command("ssh root@databaseserver 'mysql -u%s %s %s < %s'"
		% (serverUser, serverPasswordOption, serverDatabase, serverSqlPath))
	command('rsync -avP /var/www/wp-content/uploads/ /var/dev.example.com/public_html/wp-content/uploads/')

if serverReqFromLocal:
	command("ssh root@databaseserver 'mysql -u%s %s %s < %s'"
		% (serverUser, serverPasswordOption, serverDatabase, serverSqlPath))
	command("ssh root@example.com 'rsync -avP /var/www/wp-content/uploads/ /var/dev.example.com/public_html/wp-content/uploads/'")

if localReqFromServer:
	parser.error("can't do local from server")

if localReqFromLocal:
	command("scp root@databaseserver:%s %s" % (serverZipPath, localPath))

	localSqlPath = localPath + sqlFileName
	localZipPath = localPath + zipFileName

	command("tar -xvzf %s" % (localZipPath))
	command("mysql -u%s %s %s < %s" % (localUser, localPasswordOption, localDatabase, localSqlPath))

	command("rsync -avP root@example.com:/var/www/wp-content/uploads/ %s" % (imagePath))