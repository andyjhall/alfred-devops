# encoding: utf-8
import sys
import os
from workflow import Workflow3, ICON_WEB, ICON_WARNING, ICON_INFO, web, Variables
from base64 import b64encode

log = None

ORG_NAME = os.getenv('ORG_NAME')
USER_NAME = os.getenv('USER_NAME')
USER_TOKEN = os.getenv('USER_TOKEN')

def get_repos():
    url = 'https://dev.azure.com/'+ORG_NAME+'/_apis/git/repositories?api-version=6.0'

    userAndPass = b64encode(USER_NAME+":"+USER_TOKEN).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass }

    r = web.get(url, None, headers)

    r.raise_for_status()

    result = r.json()
    repos = result['value']
    return repos

def search_for_repo(repo):
    """Generate a string search key for a repo"""
    elements = []
    elements.append(repo['name'])
    return u' '.join(elements)

def main(wf):
    query = wf.args[0]
    repos = wf.cached_data('repos', get_repos, max_age=3600)

    if query and repos:
        repos = wf.filter(query, repos, key=search_for_repo, min_score=20)

    if not repos: 
        wf.add_item('No repos found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    for repo in repos:
        wf.add_item(title=repo['name'],
                    subtitle=repo['project']['name'],
                    arg=repo['webUrl'],
                    valid=True,
                    icon=None,
                    uid=repo['id'])

    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))