from flask import Flask, request, render_template
import json
import os

from github import Github

GITHUB_KEY = os.getenv("MY_SECRET")

app = Flask(__name__, template_folder='templates')


g = Github("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")

		
#url = 'https://api.github.com/repos/{repo_name}/contents/{path_to_file}'


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



if(__name__ == "__main__"):
	app.run(debug=True)