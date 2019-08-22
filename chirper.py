from datetime import datetime
from bs4 import BeautifulSoup

import pprint as pp
import requests
import json

data = {
    "total_commit":0,
    "total_repos":0,
    "last_activity":"",
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

def get_data(user, data):
    user_page = "https://github.com/{}".format(user)

    loaded_page = requests.get(user_page)
    if loaded_page.status_code != 200:
        print("Error", loaded_page.status_code)

    profile_soup = BeautifulSoup(loaded_page.text, 'html.parser')

    commit_section = profile_soup.find_all("li", class_="ml-0 py-1")
    commit_repos = [BeautifulSoup(str(i), 'html.parser').find("a") for i in commit_section]
    
    for a in commit_repos:
        filtered_url = "https://github.com{}/commits?author={}".format(a["href"], user)
        commits_page = requests.get(filtered_url)

        last_commit = BeautifulSoup(commits_page.text, 'html.parser').find("a", class_="message js-navigation-open")["href"]
        
        commit_date = BeautifulSoup(commits_page.text, 'html.parser').find("relative-time")["datetime"]
        commit_date = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")

        if data["last_activity"] == '' or data["last_activity"] < commit_date:
            data["last_activity"] = commit_date

        last_commit_page = "https://github.com{}".format(last_commit)
        repo, commit = last_commit_page.split('/')[4], last_commit_page.split('/')[-1]

        data['last_commit'][repo] = {'hash':commit, 'date':str(commit_date)}

    data["last_activity"] = str(commit_date)    
    
    return data

if __name__ == "__main__":
    secrets = get_configs()
    
    try:
        data = load_data()    
    except:
        pass

    log = get_data(secrets["github_user"], data)
    save_data(log)