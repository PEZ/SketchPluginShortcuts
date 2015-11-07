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

    def __init__(self, shortcut_string):
        self._shift = False
        self._cmd = False
        self._ctrl = False
        self._option = False
        self._key = ''
        self._is_duplicate = False

        keys = Shortcut.SEPARATOR_RE.split(str(shortcut_string))
        for key in keys:
            lower_key = key.lower()
            if lower_key in ['cmd', 'command']:
                self._cmd = True
            elif lower_key in ['ctrl', 'control']:
                self._ctrl = True
            elif lower_key in ['opt', 'option']:
                self._option = True
            elif lower_key == 'shift':
                self._shift = True
            elif len(lower_key) == 1:
                self._key = lower_key

    def to_string(self):
        s = ''
        if self._ctrl:
            s = s + 'control + '
        if self._shift:
            s = s + 'shift + '
        if self._option:
            s = s + 'option + '
        if self._cmd:
            s = s + 'command + '
        s = s + self._key
        return s

    def is_duplicate(self):
        return self._is_duplicate

    def mark_as_duplicate(self):
        self._is_duplicate = True

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
    SHORTCUT_OLD_STYLE_RE = re.compile(r'\bshortcut:\s*\(([^)]*?)\)', re.M)
    SHORTCUT_PLUGIN_BUNDLE_RE = re.compile(r'"shortcut"\s*:\s*"([^"]+?)"', re.M)
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
        repos = PluginDirectory._extract_directory(PluginDirectory._authorized_github_api_read(PluginDirectory.DIRECTORY_RAW_URL))
        PluginDirectory._freeze(repos)
        for repo in PluginDirectory._fetch_and_add_shortcuts_to_directory(repos, repo_limit):
            yield repo
            PluginDirectory._freeze(repos)

    @staticmethod
    def get_directory():
        return PluginDirectory._thaw()

    @staticmethod
    def _extract_directory(raw):
        repos = PluginDirectory.DIRECTORY_RE.findall(raw)
        return {repo[0].lower(): Repo(repo[0], repo[1], repo[2]) for repo in repos}
            
    @staticmethod
    def _add_shortcuts_to_directory(directory, repo_shortcuts):
        for r, s in repo_shortcuts:
            PluginDirectory._add_shortcuts_for_repo_to_directory(directory, r.lower(), s)

    @staticmethod
    def _fetch_and_add_shortcuts_to_directory(directory, repo_limit):
        def _check_and_manage_duplicates(shortcuts, seen):
            for shortcut in shortcuts:
                shortcut_string = shortcut.to_string()
                if shortcut_string in seen:
                    seen[shortcut_string].append(shortcut)
                    for duplicate_shortcut in seen[shortcut_string]:
                        duplicate_shortcut.mark_as_duplicate()
                else:
                    seen[shortcut_string] = [shortcut]

        seen_shortcuts = {}
        for repo_name, shortcuts in PluginDirectory._fetch_shortcuts(directory, repo_limit):
            PluginDirectory._add_shortcuts_for_repo_to_directory(directory, repo_name, shortcuts)
            _check_and_manage_duplicates(shortcuts, seen_shortcuts)
            yield directory[repo_name]

    @staticmethod
    def _add_shortcuts_for_repo_to_directory(directory, repo_name, shortcuts):
        for s in shortcuts:
            directory[repo_name].add_shortcut(s)

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
        search_results.append(PluginDirectory._fetch_shortcuts_plugin_bundle(directory, repo_limit))
        return chain.from_iterable(search_results)

    @staticmethod
    def _fetch_shortcuts_old_style(directory, repo_limit):
        search_results = PluginDirectory._search_old_style_plugin(directory, repo_limit=repo_limit)
        for result in search_results:
            for match in result.text_matches:
                matched_text = match['fragment']
                extracted_shortcuts = PluginDirectory._extract_shortcuts_old_style_from_text(matched_text)
                if len(extracted_shortcuts) > 0:
                    yield result.repository.full_name.lower(), [Shortcut(extracted_shortcut) for extracted_shortcut in extracted_shortcuts]
    
    @staticmethod
    def _authorized_github_api_read(url):
        req = urllib2.Request(url, headers={'Authorization': 'token %s' % PluginDirectory._get_github_token()});
        return urllib2.urlopen(req).read()

    @staticmethod
    def _fetch_manifest_text_from_git_url(git_url):
        import json
        from base64 import b64decode
        content_dict = json.loads(PluginDirectory._authorized_github_api_read(git_url))
        return b64decode(content_dict['content'])

    @staticmethod
    def _fetch_shortcuts_plugin_bundle(directory, repo_limit):
        search_results = PluginDirectory._search_plugin_bundle(directory, repo_limit=repo_limit)
        for result in search_results:
            if result.path.endswith('.sketchplugin/Contents/Sketch/manifest.json'):
                text = PluginDirectory._fetch_manifest_text_from_git_url(result.git_url)
                extracted_shortcuts = PluginDirectory._extract_shortcuts_plugin_bundle_from_text(text)
                if len(extracted_shortcuts) > 0:
                    yield result.repository.full_name.lower(), [Shortcut(extracted_shortcut) for extracted_shortcut in extracted_shortcuts]

    @staticmethod
    def _search_plugin_repo(directory, repo_limit, query_prefix, text_match=False):
        from itertools import chain
        if PluginDirectory.gh is None:
            PluginDirectory._github_login()
        sub_queries = PluginDirectory._build_search_query_repos_string(directory, repo_limit=repo_limit)
        search_results = []
        for sub_q in sub_queries:
            query = "%s %s" % (query_prefix, sub_q)
            search_results.append(PluginDirectory.gh.search_code(query, text_match=text_match))
        return chain.from_iterable(search_results)

    @staticmethod
    def _search_old_style_plugin(directory, repo_limit):
        return PluginDirectory._search_plugin_repo(directory, repo_limit, "shortcut in:file extension:sketchplugin", text_match=True)

    @staticmethod
    def _search_plugin_bundle(directory, repo_limit):
        return PluginDirectory._search_plugin_repo(directory, repo_limit, "shortcut in:file filename:manifest extension:json", text_match=False)

    @staticmethod
    def _extract_shortcuts_old_style_from_text(text):
        return PluginDirectory.SHORTCUT_OLD_STYLE_RE.findall(text)

    @staticmethod
    def _extract_shortcuts_plugin_bundle_from_text(text):
        return [extracted for extracted in PluginDirectory.SHORTCUT_PLUGIN_BUNDLE_RE.findall(text) if extracted.strip() != '']

