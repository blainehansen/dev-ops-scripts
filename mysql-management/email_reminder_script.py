import smtplib
from email.mime.text import MIMEText
import MySQLdb
import datetime

s = smtplib.SMTP('localhost')
db = MySQLdb.connect(host="databaseserver", user="root", passwd="secretpassword", db="sr_wordpress")

usercur = db.cursor()
# messagecur = db.cursor()

# Grab all reminder messages
# messagecur.execute("SELECT * FROM MESSAGE_TABLE_NAME")

# For each reminder message
# These could be customized for the needs of the business.
messages = [
	{'subject': 'Account Expiration Reminder: %s Days', 'message': "Your account will expire in %s days.", 'timelimit': 20},
	{'subject': 'Account Expiration Reminder: %s Days', 'message': "Your account will expire in %s days.", 'timelimit': 19},
	{'subject': 'Account Expiration Reminder: %s Days', 'message': "Your account will expire in %s days.", 'timelimit': 18},
	{'subject': 'Account Expiration Reminder: %s Days', 'message': "Your account will expire in %s days.", 'timelimit': 17},
	{'subject': 'Account Expiration Reminder: %s Days', 'message': "Your account will expire in %s days.", 'timelimit': 16},
	{'subject': 'Account Expiration Reminder: %s Days', 'message': "Your account will expire in %s days.", 'timelimit': 15},
	{'subject': 'Account Expiration Reminder: %s Days', 'message': "Your account will expire in %s days.", 'timelimit': 14},
]
# for message in messagecur.fetchall():
for message in messages:
	recipients = []
	# Grab all users whose expiration date is within this.timelimit.
	timelimit = message['timelimit']
	intervalDate = (datetime.date.today() + datetime.timedelta(days=timelimit)).isoformat()

	usercommand = """SELECT wp_users.user_email, wp_usermeta.meta_value
FROM `wp_users`
INNER JOIN `wp_usermeta` on wp_users.ID = wp_usermeta.user_id
WHERE wp_usermeta.meta_key = '_issuem_leaky_paywall_live_expires'
AND DATE(wp_usermeta.meta_value) = '%s';""" % intervalDate

	usercur.execute(usercommand)
	users = usercur.fetchall()

	# Create array of those users.
	recipients = [user[0] for user in users]

	# Send email to all using this.message
	# Create a text/plain message
	if recipients:
		msg = MIMEText(message['message'] % timelimit)

		msg['Subject'] = message['subject'] % timelimit
		sender = 'noreply@example.com'
		msg['From'] = sender
		# msg['To'] = you

		# Send the message via our own SMTP server, but don't include the envelope header.
		s.sendmail(sender, recipients, msg.as_string())

s.quit()
db.close()