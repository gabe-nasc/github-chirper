from datetime import datetime
from bs4 import BeautifulSoup

import pprint as pp
import requests
import json
import os

data = {
    "total_commit":0,
    "total_repos":0,
    "last_activity":datetime.now().replace(microsecond=0),
    "last_commit":{}
}

def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file)
        
def load_data():
    with open("data.json", "r") as file:
        return json.loads(file.read())    
    

def get_configs():
    with open("config.json") as settings:
        secret = json.loads(settings.read())
        return secret

def check_commits(href, repo, last_activity, user):
    filtered_url = "https://github.com{}/commits?author={}".format(href, user)
    commits_page = requests.get(filtered_url)

    all_commits = BeautifulSoup(commits_page.text, 'html.parser').find_all("a", class_="message js-navigation-open")
    commits_date = BeautifulSoup(commits_page.text, 'html.parser').find_all("relative-time")
    
    if type(last_activity) == str:
        last_activity = datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S")

    commits = []
    repo = None
    for commit, date in zip(all_commits, commits_date):
        date = datetime.strptime(date["datetime"], "%Y-%m-%dT%H:%M:%SZ")

        if last_activity != '' and last_activity > date:
            break

        hash_ = commit['href'].split('/')[-1]

        commits.append({'hash':hash_, 'date':str(date)})

    return commits


def get_data(user):
    global data

    user_page = "https://github.com/{}".format(user)

    loaded_page = requests.get(user_page)
    if loaded_page.status_code != 200:
        print("Error", loaded_page.status_code)

    profile_soup = BeautifulSoup(loaded_page.text, 'html.parser')

    commit_section = profile_soup.find_all("li", class_="ml-0 py-1")
    commit_repos = [BeautifulSoup(str(i), 'html.parser').find("a") for i in commit_section]

    tmp_date = data["last_activity"]
    for a in commit_repos:
        repo = a['href'].split('/')[2]

        commits = check_commits(a['href'], repo, data["last_activity"], user)
        
        if len(commits) > 0:
            last_commit_date = datetime.strptime(commits[0]["date"], "%Y-%m-%d %H:%M:%S")
        else:
            continue

        if type(tmp_date) == str:
            tmp_date = datetime.strptime(tmp_date, "%Y-%m-%d %H:%M:%S")

        if tmp_date == "" or tmp_date < last_commit_date:
            tmp_date = last_commit_date

        data["last_commit"][repo] = commits[0]
        data["total_commit"] += len(commits)
        data["total_repos"] += 1

    data["last_activity"] = str(tmp_date)
    
    return data

if __name__ == "__main__":
    secrets = get_configs()
    
    try:
        data = load_data()
    except:
        pass

    log = get_data(secrets["github_user"])
    save_data(log)