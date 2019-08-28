# **Github Chirper**

A small bot that will check someone's Github Page and make a tweet every time it notices a new commit.

This project is still in development, feel free to make pull requests, issues or comments.

## Setup

#### For local deployment:
* First you'll need to create a file called `configs.json` and have the following contents in it:

```json
{
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "access_token": "1your_access_token",
    "access_token_secret": "your_access_token_secret",
    "github_user": "github_username"
}
```
* Then all you need to do is run `python chirper --local` and the bot will start doing his job

#### For a Heroku deployment:
* First you'll need to create a Heroku app on the same folder you have this repository cloned, using the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
* Then you'll go to your Heroku and set the *Configuration Variables* (Config Vars), they can be found on Dashboard > Settings. The variable names and values should be the same ones found in the `configs.json` that is shown on the Local Deployment setup.
* After that is done you should push the repository to Heroku's remote by doing `git push heroku master`
* Lastly you'll need to run this command `heroku ps:scale worker=1` and the bot should work.

### **Warning**

**As said above, this project is still in development. The script may contain bugs. Use it at your own discretion.**