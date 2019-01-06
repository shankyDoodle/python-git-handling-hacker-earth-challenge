from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import git
import os
import shutil
from git import Repo

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


file_to_add_web = simple_get("http://hck.re/tHEZGP")
js_soup = BeautifulSoup(file_to_add_web, "html.parser")

file_to_add = str(js_soup)
file_to_add = file_to_add.replace("<app></app>", "<App />")


f = open("index.js", "w+")
f.write(file_to_add)
f.close()

web_content = simple_get("http://hck.re/crowdstrike")
html_soup = BeautifulSoup(web_content, "html.parser")


class RepoInfo(object):
    """__init__() functions as the class constructor"""
    def __init__(self, name=None, url=None, branch=None):
        self.name = name
        self.url = url
        self.branch = branch


tds = html_soup.findAll("td")
# print(tds)

inti = 0
r = RepoInfo()
RepoList = []
for x in tds:
    if inti % 3 == 0:
        r = RepoInfo()

    if inti % 3 == 0:
        r.name = x.text.strip()

    if inti % 3 == 1:
        r.url = x.text.strip()

    if inti % 3 == 2:
        r.branch = x.text.strip()
        RepoList.append(r)

    inti = inti+1


for x in RepoList:
    if not os.path.exists(x.name):
        os.makedirs(x.name)

    try:
        cloned = git.Git(x.name).clone(x.url)
        repo = Repo("./" + x.name + "/master")
        new_branch = repo.create_head(x.branch)
        repo.head.reference = new_branch

        shutil.copy("./index.js", x.name + "/master/")

        repo.index.add(["index.js"])
        commit_message1 = "Commit in repo " + x.name + " in branch " + x.branch
        repo.index.commit(commit_message1)
        repo.git.push("origin", x.branch)

        repo.git.checkout("master")
        repo.git.merge(x.branch)
        commit_message2 = "Commit for merge branch " + x.branch + " in master"
        repo.index.commit(commit_message2)
        repo.git.push("origin", "master")

    except Exception as ex:
        print(ex)

