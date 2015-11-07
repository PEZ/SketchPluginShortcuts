#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import task
from plugin_directory import PluginDirectory as pd

@task
def fetch_shortcuts():
    total_shortcuts = 0
    total_repos = 0
    for plugin in pd.fetch_directory(pd.REPO_SEARCH_LIMIT):
        total_repos = total_repos + 1
        shortcuts = len(plugin.shortcuts)
        total_shortcuts = total_shortcuts + shortcuts
        print 'Fetched %d shortcuts for %s' % (shortcuts, plugin.name)
    print 'Total: %d shortcuts in %d repositories' % (total_shortcuts, total_repos)
