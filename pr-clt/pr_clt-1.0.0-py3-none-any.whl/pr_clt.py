import argparse
import requests
from webbrowser import open_new_tab

def run(args):
	username = args.username 
	repository = args.repository
	password = args.PASSWORD
	open_in_browser = args.BROWSER
	
	url = 'https://api.bitbucket.org/2.0/repositories/' + username + '/' + repository + \
			'/pullrequests/?q=state="OPEN"&fields=values.links.self.href'
	
	if (password != None):
		request = requests.get(url, auth=(username, password))
	else:
		request = requests.get(url)
	

	if request.status_code == 401:
		print("Incorrect password")
	elif request.status_code == 403:
		print("This is private repository. Please enter password using --password or -p")
	elif request.status_code == 404:
		print("Repository " + username + "/" + repository + " not found.\nIncorrect username or repository.")
	elif request.status_code == 200:
		
		data = request.json()
		isPRFound = False

		for repo in data['values']:
			repo_url = repo['links']['self']['href']
			
			if (password != None):
				request2 = requests.get(repo_url, auth=(username, password))
			else:
				request2 = requests.get(repo_url)
			
			pullrequests = request2.json()
			
			for participant in pullrequests['participants']:
				if participant['role'] == "REVIEWER" \
							and participant['user']['username'] == username \
							and not participant['approved']:
					
					print("__________________________________________________")
					print("Title: \"" + pullrequests['title'] + "\"")
					print("Description: \"" + pullrequests['description'] + "\"")
					print("Created by: " + pullrequests['author']['display_name'] + " (username: " + pullrequests['author']['username'] + ")")
					print("At " + pullrequests['created_on'])
					print("Link: " + pullrequests['links']['html']['href'])
					
					isPRFound = True
					if open_in_browser:
						open_new_tab(pullrequests['links']['html']['href'])

		if not isPRFound:
			print("There is no Pull Requests sent to " + username + ".")

	   		
def main():
	parser=argparse.ArgumentParser(description="Command line tool that searches for pull requests in BitBucket repository.")
	parser.add_argument("username", type=str, help="BitBucket username")
	parser.add_argument("repository", type=str, help="BitBucket repository")
	parser.add_argument("-b", "--browser", help="open link in new tab of browser", action='store_true', dest="BROWSER")
	parser.add_argument("-p", "--password", help="BitBucket Password", type=str, dest="PASSWORD")
	parser.set_defaults(func=run)
	args=parser.parse_args()
	args.func(args)

if __name__ =="__main__":
	main()