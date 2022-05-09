# encoding: utf-8

from workflow import Workflow, PasswordNotFound
import mureq
import os
import base64

ORG_NAME = os.getenv('ORG_NAME')
USER_NAME = os.getenv('USER_NAME')
USER_TOKEN = os.getenv('USER_TOKEN')

def get_repos():
    
    userTokenBase64 = base64.b64encode('{}:{}'.format(USER_NAME, USER_TOKEN).encode('ascii')).decode('ascii')
    response = mureq.get('https://dev.azure.com/'+ORG_NAME+'/_apis/git/repositories?api-version=6.0', headers=({'Authorization': 'Basic '+userTokenBase64}))

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    response.raise_for_status()

    # Parse the JSON returned and extract the repos
    return response.json()["value"]


def main(wf):
    def fetch_repos():
        return get_repos()

    repos = wf.cached_data('repos', fetch_repos, max_age=3600)

    # Record our progress in the log file
    log.debug('{} repos cached'.format(len(repos)))


if __name__ == "__main__":
    wf = Workflow()
    log = wf.logger
    wf.run(main)
