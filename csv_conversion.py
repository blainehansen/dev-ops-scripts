import string
import re
import datetime

srcObj = open("examplecom.users.2015-06-29-14-38-07.csv", 'r+')
contents = srcObj.read()
contents = re.sub(r'^\S+[\n]', '', contents)
contents = re.sub(r'(?<=[^"])(\s*[\n]\s*)', ' ', contents)
destObj = open("examplecom.users.2015-06-29-14-38-07.fixed.csv", 'w')
destObj.write(contents)
srcObj.close()
destObj.close()

srcObj = open("examplecom.users.2015-06-29-14-38-07.fixed.csv", 'r')
destObj = open("example.users.compiled.csv", 'w')
rejectObj = open("example.users.without-email.txt", 'w')

oneYear = datetime.timedelta(weeks=52, days=1)
compareDate = datetime.datetime(2014, 10, 1)

for line in srcObj:
	if line[0] != '"':
		print "failed column", line
		continue

	columns = line.split('","')
	# print 'full array: ', columns

	try:
		registered = columns[5].strip('"')
	except:
		print columns
		continue

	registeredObj = datetime.datetime.strptime(registered, "%Y-%m-%d %H:%M:%S")
	if registeredObj < compareDate:
		expires = datetime.datetime(2015, 9, 25)
	else:
		expires = registeredObj.date() + oneYear

	indices = [1, 3, 0]
	columns = [columns[i].strip('"') for i in indices]

	email = columns[1].strip('"')
	if not email:
		rejectObj.write(string.join(columns, ',') + '\n')

	columns.insert(2, '15.00')
	columns.insert(3, '%s' % expires)
	columns.insert(4, 'active')
	columns.insert(5, '0')
	# print 'sliced array: ', columns

	compiled = string.join(columns, ',')
	# print 'final string: ', compiled
	# print

	destObj.write(compiled + '\n')

srcObj.close()
destObj.close()
rejectObj.close()

# 0 		1 		2 		3 		4 		5 			6
# username, email, price, expires, status, level-id, subscriber-id

# 1 			3 			N 			N		6 				N		0
# user_login, user_email, price??, expires??, user_status, level-id??, id