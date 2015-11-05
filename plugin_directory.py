import urllib2
import re
import string
import jsonpickle

import os

import redis

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)


class Shortcut(object):
    SEPARATOR_RE = re.compile(r'\s+')

    _shift = False
    _cmd = False
    _ctrl = False
    _option = False
    _key = ''

    def __init__(self, shortcut_string):
        keys = Shortcut.SEPARATOR_RE.split(str(shortcut_string))
        for key in keys:
            lower_key = key.lower()
            if lower_key in ['cmd', 'command']:
                self._cmd = True
            elif lower_key == 'ctrl':
                self._ctrl = True
            elif lower_key == 'option':
                self._option = True
            elif lower_key == 'shift':
                self._shift = True
            elif len(lower_key) == 1:
                self._key = lower_key

    def to_string(self):
        s = ''
        if self._ctrl:
            s = s + 'ctrl + '
        if self._shift:
            s = s + 'shift + '
        if self._option:
            s = s + 'option + '
        if self._cmd:
            s = s + 'command + '
        s = s + self._key
        return s

class Repo(object):

    def __init__(self, name, url='', description=''):
        self.name = name
        self.url = url
        self.description = description
        self.shortcuts = []

    def add_shortcut(self, shortcut):
        self.shortcuts.append(shortcut)


class PluginDirectory(object):
    DIRECTORY_RAW_URL='https://raw.githubusercontent.com/sketchplugins/plugin-directory/master/README.md'
    DIRECTORY_RE = re.compile(r'^- \[(.+?)\]\((.+?)\) (.+)$', re.M)
    SHORTCUT_OLD_STYLE_RE = re.compile(r'\bshortcut:\s+\(([^)]*?)\)', re.M)
    FREEZER_KEY = "frozen"
    REPO_SEARCH_LIMIT = 40

    gh = None

    @staticmethod
    def _freeze(directory):
        redis.set(PluginDirectory.FREEZER_KEY, jsonpickle.encode(directory))

    @staticmethod
    def _thaw():
        import os.path
        thawed = None
        try:
            thawed = jsonpickle.decode(redis.get(PluginDirectory.FREEZER_KEY))
        except:
            pass
        return thawed

    @staticmethod
    def fetch_directory(repo_limit):
        repos = []
        repos = PluginDirectory._get_directory(urllib2.urlopen(PluginDirectory.DIRECTORY_RAW_URL).read())
        PluginDirectory._fetch_and_add_shortcuts_to_directory(repos, repo_limit)
        PluginDirectory._freeze(repos)
        return repos

    @staticmethod
    def get_directory():
        return PluginDirectory._thaw()

    @staticmethod
    def _get_directory(raw):
        repos = PluginDirectory.DIRECTORY_RE.findall(raw)
        return {repo[0]: Repo(repo[0], repo[1], repo[2]) for repo in repos}
            
    @staticmethod
    def _add_shortcuts_to_directory(directory, repo_shortcuts):
        for r, s in repo_shortcuts:
            PluginDirectory._add_shortcuts_for_repo_to_directory(directory, r, s)

    @staticmethod
    def _fetch_and_add_shortcuts_to_directory(directory, repo_limit):
        for repo, shortcuts in PluginDirectory._fetch_shortcuts(directory, repo_limit):
            PluginDirectory._add_shortcuts_for_repo_to_directory(directory, repo, shortcuts)

    @staticmethod
    def _add_shortcuts_for_repo_to_directory(directory, repo, shortcuts):
        for s in shortcuts:
            directory[repo].add_shortcut(s)

    @staticmethod
    def _get_github_token():
        return os.environ.get('GITHUB_TOKEN','')

    @staticmethod
    def _build_search_query_repos_string(directory, repo_limit):
        repo_names = sorted(directory.keys(), key=lambda v: v.lower())
        cursor = 0
        while cursor < len(repo_names) - 1:
            yield ' '.join('repo:%s' % k for k in repo_names[cursor:cursor + repo_limit])
            cursor = cursor + repo_limit

    @staticmethod
    def _github_login():
        from github3 import login
        if PluginDirectory.gh is None:
            token = PluginDirectory._get_github_token()
            PluginDirectory.gh = login(token=token)

    @staticmethod
    def _fetch_shortcuts(directory, repo_limit):
        from itertools import chain
        search_results = [PluginDirectory._fetch_shortcuts_old_style(directory, repo_limit)]
        search_results.append(PluginDirectory._fetch_shortcuts_plugin_plugin_bundle(directory, repo_limit))
        return chain.from_iterable(search_results)

    @staticmethod
    def _fetch_shortcuts_old_style(directory, repo_limit):
        search_results = PluginDirectory._search_old_style_plugin(directory, repo_limit=repo_limit)
        for result in search_results:
            for match in result.text_matches:
                matched_text = match['fragment']
                extracted_shortcuts = PluginDirectory._extract_shortcuts_old_style_from_text(matched_text)
                yield result.repository.full_name, [Shortcut(extracted_shortcut) for extracted_shortcut in extracted_shortcuts]
    
    @staticmethod
    def _fetch_shortcuts_plugin_plugin_bundle(directory, repo_limit):
        return [];

    @staticmethod
    def _search_old_style_plugin(directory, repo_limit):
        from itertools import chain
        if PluginDirectory.gh is None:
            PluginDirectory._github_login()
        sub_queries = PluginDirectory._build_search_query_repos_string(directory, repo_limit=repo_limit)
        search_results = []
        for sub_q in sub_queries:
            query = "shortcut in:file extension:sketchplugin %s" % sub_q
            search_results.append(PluginDirectory.gh.search_code(query, text_match=True))
        return chain.from_iterable(search_results)

    @staticmethod
    def _search_plugin_bundle(directory, repo_limit):
        PluginDirectory._github_login()
        query = "shortcut: in:file filename:manifest extension:json %s" % PluginDirectory._build_search_query_repos_string(directory, repo_limit=repo_limit)
        return PluginDirectory.gh.search_code(query)

    @staticmethod
    def _extract_shortcuts_old_style_from_text(text):
        return PluginDirectory.SHORTCUT_OLD_STYLE_RE.findall(text)

