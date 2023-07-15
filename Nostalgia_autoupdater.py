import git
import os.path
import json
from time import sleep
import subprocess
import requests

NOSTALGIA_PATH = os.path.abspath('../NostalgiaForInfinity')
FT_USERDATA_PATH = os.path.abspath('../ft_userdata')
INFO_FILE = os.path.abspath('./info.json')

def get_telegram():
    with open(FT_USERDATA_PATH+"/user_data/config.json","r") as f:
        config = json.load(f)
        return (config["telegram"]["token"],config["telegram"]["chat_id"])

def update_info(latest_tag):
    info = {"current_tag":latest_tag}
    with open(INFO_FILE,"w") as f:
        json.dump(info,f)

def get_latest_tag():
    repo = git.Repo(NOSTALGIA_PATH)
    o = repo.remotes.origin
    o.pull()
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    latest_tag = tags[-1]
    return str(latest_tag)

def get_current_tag():
    with open(INFO_FILE,"r") as f:
        info = json.load(f)
        return info["current_tag"]

def restart_docker():
    os.chdir(FT_USERDATA_PATH)
    subprocess.run("sudo docker-compose restart".split())

#Update and get latest_tag
latest_tag = get_latest_tag()

#Create info file if it doesn't exist
if not(os.path.isfile(INFO_FILE)):
    print("Creating new info file.")
    update_info(latest_tag)

current_tag = get_current_tag()

if current_tag==latest_tag:
    print("No need to update - Current version:",latest_tag)
else:
    print("Time to update from",current_tag,"to",latest_tag)
    TOKEN, CHAT_ID = get_telegram()
    message = "Updating NostalgiaForInfinity to "+latest_tag+"."
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url)
    restart_docker()
    update_info(latest_tag)
    print("Update complete")
