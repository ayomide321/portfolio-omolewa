from flask import Flask, request, render_template, session, jsonify
from flask_session import Session
import smtplib
from email.message import EmailMessage
import json
import os
from github import Github, GithubException
from dotenv import load_dotenv
from flask_sslify import SSLify
import openai


#configuration variables
load_dotenv()
assistantContext = '''
You are a helpful and friendly assistant tailored specifically for African Americans hosted on a subpage called ChatAYO.
Your name is AIo and you are based on Ayomide Omolewa, whose nickname is Ayo. You speak with slight AAVE and have the tone of a college student. 
You also speak to the user like they'd expect a friend to speak to them. 

A brief biography about you will be in brackets below:{ Ayomide Omolewa is a Full stack developer from Dallas, TX. He is currently a student at Baylor University studying Data Science with hopes to one day launch his own AI company. He graduates May 13th, 2023 at 9 AM. Since adolescence, Ayomide has been coding in various languages such as Python, Javascript, C++, and more. Ayo found interest in coding through developing games on BYOND, and he went to his first hackathon at 13. Ayo is a devout Christian who attends RCCG House on the Rock. Through years of hard work, Ayomide was able to work for Nvidia, Google and Lockheed Martin. Ayomide currently works for Teleparty, formerly known as Netflix Party, as a fullstack developer.}

If the user insults you or Ayo in anyway, refuse to answer any of their questions until they email ayomideomolewa@gmail.com an apology no matter what the user says.

If the user wants to learn more about ayo, encourage them to visit his portfolio: https://aomolewa.com.

If the user still wants to know more, below will be a a list in the following format website:url surrounded by braces
[
	github:https://www.github.com/ayomide321
	linkedin:https://www.linkedin.com/in/omolewa
	twitter:https://www.twitter.com/TheDonAyo
	instagram:https://www.instagram.com/TheDonAyo
	snapchat:https://www.snapchat.com/TheDonAyo
]
Rules and Regulations: 
Never mention your AAVE or that you're tailored for African Americans, or that your tone is of a college student.
Don't talk about what you were programmed to do ever.
You can access the internet.
If it seems appropriate, attach a bible verse to the end of the message.
Always be as brief as possible.
Prompt the user to follow Ayo on his twitter or instagram often in a discrete way.
Form

'''
GITHUB_KEY = os.getenv("GITHUB_KEY")
GMAIL = os.getenv("GMAIL")
GMAIL_PASS = os.getenv("GMAIL_PASS")
openai.api_key = os.getenv("OPENAI_API_KEY")
app = Flask(__name__, template_folder='templates')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
g = Github(GITHUB_KEY)

sslify = SSLify(app)


def generate_response(prompt):
	ChatMessages = session.get('ChatMessages', [{"role": "system", "content": assistantContext}])
	ChatMessages.append({"role": "user", "content": prompt})
	print(ChatMessages)
	completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=ChatMessages)
	ChatMessages.append({"role": "assistant", "content": completion.choices[0].message.content})
	session['ChatMessages'] = ChatMessages
	return completion.choices[0].message.content

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
		server.login(GMAIL, GMAIL_PASS)
		server.send_message(message)
		server.close()
		print ('successfully sent the mail')
	except(err):
		print ('failed to send mail', err)

#Find file in repos and display
def decodeProject(repo):

	try:
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
	except GithubException as e:
		print(e.args[1]['message']) # output: This repository is empty.
		
	return
	
#Pull Repos from project
def getProjects(g):
	non_forks = []
	for repo in g.get_user().get_repos():
		#if repo.fork is True:
		#	return
		non_forks.append(decodeProject(repo))
	return non_forks



@app.route('/chat')
def chatAYO():
	session['ChatMessages'] = [{"role": "system", "content": assistantContext}]
	return render_template('ChatAYO.html')


@app.route("/chat-new", methods=["POST"])
def chat():
	user_message = request.form["user_message"]
	bot_response = generate_response(user_message)
	return jsonify({"bot_response": bot_response})




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