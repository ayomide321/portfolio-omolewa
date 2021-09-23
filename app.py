from flask import Flask, request, render_template
import smtplib
from email.message import EmailMessage
import json
import os
from github import Github
from dotenv import load_dotenv
load_dotenv()
GITHUB_KEY = os.getenv("GITHUB_KEY")
GMAIL = os.getenv("GMAIL")
GMAIL_PASS = os.getenv("GMAIL_PASS")
app = Flask(__name__, template_folder='templates')
g = Github(GITHUB_KEY)

# Email information
def send_email(name, incoming_email, subject, body):

	FROM = incoming_email
	TO = GMAIL
	SUBJECT = subject
	TEXT = body

	# Prepare actual message
	message = EmailMessage()
	message.set_content("""From: %s\nEmail: %s\nSubject: %s\n\n%s
	""" % (name, FROM, SUBJECT, TEXT))
	message['Subject'] = subject
	message['From'] = FROM
	message['TO'] = TO
	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		print (GMAIL)
		print (GMAIL_PASS)
		server.login(GMAIL, GMAIL_PASS)
		server.send_message(message)
		server.close()
		print ('successfully sent the mail')
	except(err):
		print ('failed to send mail', err)

#Find file in repos and display
def decodeProject(repo):
	portfolioFile = 'portfolio.json'
	all_files = []
	contents = repo.get_contents("")
	while contents:
		file_content = contents.pop(0)
		if file_content.type == "dir":
			continue
		all_files.append(str(file_content).replace('ContentFile(path="','').replace('")',''))
		
	if portfolioFile in all_files:
		raw_data = json.loads(repo.get_contents(portfolioFile).decoded_content.decode())
		return raw_data
	
	return
	
#Pull Repos from project
def getProjects(g):
	non_forks = []
	for repo in g.get_user().get_repos():
		#if repo.fork is True:
		#	return
		non_forks.append(decodeProject(repo))
	return non_forks


@app.route('/')
def index():
	portfolio = getProjects(g)
	return render_template('index.html', portfolioList = filter(None, portfolio))

@app.route('/handle-contact', methods = ['POST'])
def contact():
	try:
		name = request.form['name']
		email = request.form['email']
		subject = request.form['subject']
		body = request.form['message']
		send_email(name, email, subject, body)
		return 'OK'
	except:
		return 'The message failed to send'



if(__name__ == "__main__"):
	app.run(debug=True)