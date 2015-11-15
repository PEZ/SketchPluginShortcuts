#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

        keys = Shortcut.SEPARATOR_RE.split(shortcut_string)
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
    FREEZER_KEY = 'frozen'
    REPO_SEARCH_LIMIT = 40

    @staticmethod
    def _freeze(directory, prefix):
        redis.set(prefix + PluginDirectory.FREEZER_KEY, jsonpickle.encode(directory))

    @staticmethod
    def _thaw(prefix):
        import os.path
        thawed = None
        try:
            thawed = jsonpickle.decode(redis.get(prefix + PluginDirectory.FREEZER_KEY))
        except:
            pass
        return thawed

    def __init__(self, freezer_prefix=''):
        self._repo_search_limit = PluginDirectory.REPO_SEARCH_LIMIT
        self._freezer_prefix = freezer_prefix
        self.gh = None
        self._github_token = os.environ.get('GITHUB_TOKEN','')
        self._github_login()

    def get_directory(self):
        return self._thaw(self._freezer_prefix)

    def fetch_directory(self, raw_directory_text=None):
        if raw_directory_text is not None:
            self.repos = self._extract_directory(raw_directory_text)
        else:
            self.repos = self._extract_directory(self._fetch_raw_directory_text())
        PluginDirectory._freeze(self.repos, self._freezer_prefix)

    def fetch_shortcuts(self):
        for repo in self._fetch_and_add_shortcuts_to_directory():
            yield repo
            PluginDirectory._freeze(self.repos, self._freezer_prefix)

    def _fetch_raw_directory_text(self):
        return self._authorized_github_api_read(PluginDirectory.DIRECTORY_RAW_URL)
    
    def _extract_directory(self, raw):
        repos = PluginDirectory.DIRECTORY_RE.findall(raw)
        return {repo[0].lower(): Repo(repo[0], repo[1], repo[2]) for repo in repos}

    def _fetch_and_add_shortcuts_to_directory(self):
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
        for repo_name, shortcuts in self._fetch_shortcuts():
            self._add_shortcuts_for_repo_to_directory(repo_name, shortcuts)
            _check_and_manage_duplicates(shortcuts, seen_shortcuts)
            yield self.repos[repo_name]

    def _add_shortcuts_for_repo_to_directory(self, repo_name, shortcuts):
        for s in shortcuts:
            self.repos[repo_name].add_shortcut(s)

    def _authorized_github_api_read(self, url):
        req = urllib2.Request(url, headers={ 'Authorization': 'token %s' % self._github_token });
        return urllib2.urlopen(req).read()

    def _build_search_query_repos_string(self):
        repo_names = sorted(self.repos.keys(), key=lambda v: v.lower())
        cursor = 0
        while cursor < len(repo_names) - 1:
            yield ' '.join('repo:%s' % k for k in repo_names[cursor:cursor + self._repo_search_limit])
            cursor = cursor + self._repo_search_limit

    def _github_login(self):
        from github3 import login
        if self.gh is None:
            self.gh = login(token=self._github_token)

    def _fetch_shortcuts(self):
        from itertools import chain
        search_results = [self._fetch_shortcuts_old_style()]
        search_results.append(self._fetch_shortcuts_plugin_bundle())
        return chain.from_iterable(search_results)

    def _fetch_shortcuts_old_style(self):
        search_results = self._search_old_style_plugin()
        for result in search_results:
            for match in result.text_matches:
                matched_text = match['fragment']
                extracted_shortcuts = self._extract_shortcuts_old_style_from_text(matched_text)
                if len(extracted_shortcuts) > 0:
                    yield result.repository.full_name.lower(), [Shortcut(extracted_shortcut) for extracted_shortcut in extracted_shortcuts]
    
    def _fetch_manifest_text_from_git_url(self, git_url):
        import json
        from base64 import b64decode
        content_dict = json.loads(self._authorized_github_api_read(git_url))
        return b64decode(content_dict['content'])

    def _fetch_shortcuts_plugin_bundle(self):
        search_results = self._search_plugin_bundle()
        for result in search_results:
            if result.path.endswith('.sketchplugin/Contents/Sketch/manifest.json'):
                text = self._fetch_manifest_text_from_git_url(result.git_url)
                extracted_shortcuts = self._extract_shortcuts_plugin_bundle_from_text(text)
                if len(extracted_shortcuts) > 0:
                    yield result.repository.full_name.lower(), [Shortcut(extracted_shortcut) for extracted_shortcut in extracted_shortcuts]

    def _search_plugin_repo(self, query_prefix, text_match=False):
        from itertools import chain
        sub_queries = self._build_search_query_repos_string()
        search_results = []
        for sub_q in sub_queries:
            query = "%s %s" % (query_prefix, sub_q)
            search_results.append(self.gh.search_code(query, text_match=text_match))
        return chain.from_iterable(search_results)

    def _search_old_style_plugin(self):
        return self._search_plugin_repo("shortcut in:file extension:sketchplugin", text_match=True)

    def _search_plugin_bundle(self):
        return self._search_plugin_repo("shortcut in:file filename:manifest extension:json", text_match=False)

    def _extract_shortcuts_old_style_from_text(self, text):
        return [extracted.decode('utf-8') for extracted in PluginDirectory.SHORTCUT_OLD_STYLE_RE.findall(text)]

    def _extract_shortcuts_plugin_bundle_from_text(self, text):
        return [extracted.decode('utf-8') for extracted in PluginDirectory.SHORTCUT_PLUGIN_BUNDLE_RE.findall(text) if extracted.strip() != '']

