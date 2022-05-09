# encoding: utf-8

import sys
import argparse
from workflow import Workflow3, ICON_WARNING, ICON_INFO, PasswordNotFound
from workflow.background import run_in_background, is_running

log = None


def search_for_repo(repo):
    """Generate a string search key for a repo"""
    elements = [repo['name'], repo['project']['name']]
    return u' '.join(elements)


def main(wf):
    query = wf.args[0]
    repos = wf.cached_data('repos', None, max_age=0)

    # Notify the user if the cache is being updated
    if is_running('update') and not repos:
        wf.rerun = 0.5
        wf.add_item('Updating repo list...',
                    subtitle=u'This can take some time if you have a large number of repos.',
                    valid=False,
                    icon=ICON_INFO)

    # Start update script if cached data is too old (or doesn't exist)
    if not wf.cached_data_fresh('repos', max_age=3600) and not is_running('update'):
        cmd = [sys.executable, wf.workflowfile('update.py')]
        run_in_background('update', cmd)
        wf.rerun = 0.5

    # If script was passed a query, use it to filter repos
    if query and repos:
        repos = wf.filter(query, repos, key=search_for_repo, min_score=20)

    if not repos:  # we have no data to show, so show a warning and stop
        wf.add_item('No repos found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for repo in repos:
        wf.add_item(title=repo['project']['name'],
                    subtitle=repo['name'],
                    arg=repo['webUrl'],
                    valid=True,
                    icon=None,
                    uid=repo['id'])

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
