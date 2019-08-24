from datetime import datetime
from bs4 import BeautifulSoup

import pprint as pp
import requests
import json
import os

# Template for how data is going to be stored
data = {
    "total_commits":0, # Number of commits tracked
    "total_repos":0, # Number of repositories tracked
    "last_activity":datetime.now().replace(microsecond=0), # Time and Date from last activity tracked
    "last_commit":{} # Information about the last commit tracked in each repository
}

# Saves the data into a json
def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file)

# Loads previously saved data
def load_data():
    with open("data.json", "r") as file:
        return json.loads(file.read())

# Reads config file and return its contents
def get_configs():
    with open("config.json") as settings:
        secret = json.loads(settings.read())
        return secret

# For each given repo returns commits made since the last tracked activity
def check_commits(href, repo, last_activity, user):

    # Formats the url so when it its requested only commits from a specific author will appear
    filtered_url = "https://github.com{}/commits?author={}".format(href, user)
    commits_page = requests.get(filtered_url)

    # Magic that get only the link for each commit in the page
    all_commits = BeautifulSoup(commits_page.text, 'html.parser').find_all("a", class_="message js-navigation-open")
    commits_date = BeautifulSoup(commits_page.text, 'html.parser').find_all("relative-time")

    # If for some reason the last tracked activity is read as string,
    # converts it to a datetime object
    if type(last_activity) == str:
        last_activity = datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S")

    commits = []
    repo = None
    for commit, date in zip(all_commits, commits_date):
        date = datetime.strptime(date["datetime"], "%Y-%m-%dT%H:%M:%SZ")

        # If current commit is older than the last tracked activity
        # the ones that come after will also be, so the loop must be broken
        if last_activity != '' and last_activity > date:
            break

        hash_ = commit['href'].split('/')[-1]

        commits.append({'hash':hash_, 'date':str(date)})

    return commits

# Main data-gathering function
def get_data(user):
    global data

    user_page = "https://github.com/{}".format(user)

    # Try to load a user homepage, if there is a problem return None
    loaded_page = requests.get(user_page)
    if loaded_page.status_code != 200:
        print("Error", loaded_page.status_code)

    profile_soup = BeautifulSoup(loaded_page.text, 'html.parser')

    # Find all repositories that have been updated and get the link to them
    commit_section = profile_soup.find_all("li", class_="ml-0 py-1")
    commit_repos = [BeautifulSoup(str(i), 'html.parser').find("a") for i in commit_section]

    tmp_date = data["last_activity"] # Stores the most recent commit date/time
    for a in commit_repos:
        repo = a['href'].split('/')[2]

        commits = check_commits(a['href'], repo, data["last_activity"], user)

        # Check if any new commits were made
        if len(commits) > 0:
            last_commit_date = datetime.strptime(commits[0]["date"], "%Y-%m-%d %H:%M:%S")
        else:
            continue

        if type(tmp_date) == str:
            tmp_date = datetime.strptime(tmp_date, "%Y-%m-%d %H:%M:%S")

        # Update tmp_date if a commit is newer than it is
        if tmp_date == "" or tmp_date < last_commit_date:
            tmp_date = last_commit_date

        # Update global data with updated stats
        data["last_commit"][repo] = commits[0]

        if repo not in data["last_commit"]:
            data["total_repos"] += 1
            if commits[0] not in data["last_commit"][repo]:
                data["total_commit"] += len(commits)


    # Update global data with newest activity
    data["last_activity"] = str(tmp_date)

if __name__ == "__main__":
    secrets = get_configs()

    # If it is not possible to load older data, use template
    try:
        data = load_data()
    except:
        pass
    
    get_data(secrets["github_user"])

    save_data(data)