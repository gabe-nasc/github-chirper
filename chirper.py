from bs4 import BeautifulSoup

import requests
import json

secret = []
with open("config.json") as settings:
    secret = json.loads(settings.read())

user_page = "https://github.com/{}".format(secret["github_user"])

loaded_page = requests.get(user_page)

if loaded_page.status_code != 200:
    print("Error", loaded_page.status_code)

soup = BeautifulSoup(loaded_page.text, 'html.parser')

commit_section = soup.find_all("li", class_="ml-0 py-1")
commit_repos = BeautifulSoup(str(commit_section), 'html.parser').find_all("a")

new_repo_section = soup.find_all("li", class_="d-block mt-1 py-1")
new_repos = BeautifulSoup(str(commit_section), 'html.parser').find_all("a")
