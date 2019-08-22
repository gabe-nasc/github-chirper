from datetime import datetime
from bs4 import BeautifulSoup

import pprint as pp
import requests
import json

def save(data):
    with open("data.json", "w") as file:
        json.dump(data, file)
        
def load():
    with open("data.json", "r") as file:
        json.loads(file.read)

def get_configs():
    with open("config.json") as settings:
        secret = json.loads(settings.read())
        return secret

if __name__ == "__main__":    
    secret = get_configs()
    user_page = "https://github.com/{}".format(secret["github_user"])

    loaded_page = requests.get(user_page)
    if loaded_page.status_code != 200:
        print("Error", loaded_page.status_code)

    profile_soup = BeautifulSoup(loaded_page.text, 'html.parser')

    # ----
    commit_section = profile_soup.find_all("li", class_="ml-0 py-1")
    commit_repos = [BeautifulSoup(str(i), 'html.parser').find("a") for i in commit_section]

    log = {
        'last_activity':'', # Date
        'last_commit':{},
        'new_repos':[]# Repository, Last Commit tweeted
    }
    for a in commit_repos:
        filtered_url = "https://github.com{}/commits?author={}".format(a["href"], secret["github_user"])
        commits_page = requests.get(filtered_url)

        last_commit = BeautifulSoup(commits_page.text, 'html.parser').find("a", class_="message js-navigation-open")["href"]
        commit_date = BeautifulSoup(commits_page.text, 'html.parser').find("relative-time")["datetime"]
        commit_date = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")

        if log["last_activity"] == '' or log["last_activity"] < commit_date:
            log["last_activity"] = commit_date

        last_commit_page = "https://github.com{}".format(last_commit)
        # print(last_commit_page.split('/'))
        repo, commit = last_commit_page.split('/')[4], last_commit_page.split('/')[-1]

        log['last_commit'][repo] = {'page':commit, 'date':commit_date}

    pp.pprint(log)

    new_repo_section = profile_soup.find_all("a", class_="mr-2")#find_all("li", class_="d-block mt-1 py-1")
    # new_repos = BeautifulSoup(str(commit_section), 'html.parser').find_all("a", class_="mr-2")

    # pp.pprint(new_repo_section)

    # print(len(new_repos))
    for a in new_repo_section:
    #     print(a)
        repo_name = a['href'].split('/')[-1]
        full_url = "https://github.com" + a['href']
        print("->", repo_name)
        print("->", full_url)
