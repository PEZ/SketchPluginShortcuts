#!/usr/bin/env python

"""Tests for the Plugin directory shortcuts service"""

import unittest
import re

from plugin_directory import PluginDirectory as pd

class TestDirectory(unittest.TestCase):

    def setUp(self):
        self.plugins_raw = ''' # Sketch Plugin Directory

A list of Sketch plugins hosted at GitHub, in alphabetical order.

**Note:** if you want to add yours, just open an issue with the URL, or send a pull request.

- [47deg/pointgrid](https://github.com/47deg/pointgrid) This plugin makes it easy to create different breakpoints during a responsive web design.
- [8by8/sketchplugins](https://github.com/8by8/sketchplugins) Plugins for Sketch.
- [abynim/BaseAlign](https://github.com/abynim/basealign) A Sketch Plugin to align Text Layers by their baselines
- [abynim/SketchSquares](https://github.com/abynim/sketchsquares) Replace layers in Sketch with photos from Instagram.
- [abynim/sketchy-pies](https://github.com/abynim/sketchy-pies) A Sketch plugin to magically convert regular circle layers into pie charts!
- [abynim/userflows](https://github.com/abynim/userflows) Generate user walkthroughs from Artboards in Sketch.
- [abynim/Xport](https://github.com/abynim/xport) A Sketch Plugin to export image assets directly to Xcode
- [acollurafici/Sketch-Nearest-8](https://github.com/acollurafici/sketch-nearest-8) Sketch Plugin to round shape size to the nearest multiple of 8
- [adamhowell/random-opacity-sketch-plugin](https://github.com/adamhowell/random-opacity-sketch-plugin) Randomly change the opacity of selected objects in Sketch.
- [ajaaibu/ThaanaText](https://github.com/ajaaibu/thaanatext) Sketch Plugin to generate thaana strings, paragraphs, articles.
- [alessndro/sketch-plugins](https://github.com/alessndro/sketch-plugins) An incredible collection of plugins, including some great ones for working with baselines.
- [PEZ/SketchDistributor](https://github.com/pez/sketchdistributor) Distribute selection objects vertically or horizontally with a given spacing between them.
- [utom/sketch-measure](https://github.com/utom/sketch-measure) A measure tool for Sketch.app (think Specctr for Sketch)
'''
        self.repos = pd._extract_directory(self.plugins_raw)
        self.repo_limit = 5

    def test_extract_repos(self):
        self.assertEqual(len(self.repos), 13)
        self.assertEqual(self.repos['adamhowell/random-opacity-sketch-plugin'].name, 'adamhowell/random-opacity-sketch-plugin')
        self.assertEqual(self.repos['47deg/pointgrid'].url, 'https://github.com/47deg/pointgrid')
        self.assertEqual(self.repos['ajaaibu/thaanatext'].description, '''Sketch Plugin to generate thaana strings, paragraphs, articles.''')

    def test_build_search_query_repos_string(self):
        queries = list(pd._build_search_query_repos_string(self.repos, self.repo_limit))
        self.assertEqual(len(queries), 3)
        for query in queries:
            self.assertTrue(re.search(r' repo:', query))

    def test_extract_shortcut_old_style_from_text(self):
        text = '''// shortcut: (shift cmd o)
// sketch-random-opacity
// @author	Adam Howell

var userValues = [doc
abynim/BaseAlign:  __Apply__.
![Configuration Window](config_dialog.png)'''
        self.assertEqual(pd._extract_shortcuts_old_style_from_text(text)[0], 'shift cmd o')
        
    def test_extract_shortcut_plugin_bundle_from_text(self):
        text = '''      "handler" : "onRun",
      "shortcut" : "shift ctrl d",
      "name" : "Distribute ...",
      "identifier" : "distributor"
    },
    {
      "script" : "script.cocoascript",
      "handler" : "onRepeat",
      "shortcut" : "shift ctrl a",
      "name" : "Distribute again", '''
        shortcuts = pd._extract_shortcuts_plugin_bundle_from_text(text) 
        self.assertEqual(len(shortcuts), 2)
        self.assertEqual(shortcuts[0], 'shift ctrl d')
        
    def test_fetch_and_add_shortcuts_to_repo(self):
        test_repo_name = 'adamhowell/random-opacity-sketch-plugin'
        for repo in pd._fetch_and_add_shortcuts_to_directory(self.repos, self.repo_limit):
            if repo.name == test_repo_name:
                self.assertEqual(len(self.repos[test_repo_name].shortcuts), 1)
                self.assertEqual(self.repos[test_repo_name].shortcuts[0].to_string(), 'shift + command + o')

    def test_get_shortcuts_old_style(self):
        pass

    def test_add_shortcuts_to_directory(self):
        repo_shortcuts = pd._fetch_shortcuts(self.repos, self.repo_limit)
        pd._add_shortcuts_to_directory(self.repos, repo_shortcuts)
        self.assertEqual(len(self.repos['adamhowell/random-opacity-sketch-plugin'].shortcuts), 1)
        self.assertEqual(self.repos['adamhowell/random-opacity-sketch-plugin'].shortcuts[0].to_string(), 'shift + command + o')
        self.assertEqual(len(self.repos['pez/sketchdistributor'].shortcuts), 2)
        self.assertEqual(self.repos['pez/sketchdistributor'].shortcuts[0].to_string(), 'control + shift + d')

    def test_add_shortcuts_for_repo_to_directory(self):
        repo_shortcuts = pd._fetch_shortcuts_old_style(self.repos, self.repo_limit)
        for r, s in repo_shortcuts:
            pd._add_shortcuts_for_repo_to_directory(self.repos, r, s)
            self.assertEqual(self.repos[r].shortcuts, s)

    def test_get_github_token(self):
        self.assertNotEqual(pd._get_github_token(), '')

    def test_freeze_thaw(self):
        pd._freeze(self.repos)
        thawed_repos = pd._thaw()
        self.assertEqual(self.repos['adamhowell/random-opacity-sketch-plugin'].description, thawed_repos['adamhowell/random-opacity-sketch-plugin'].description)



from plugin_directory import Shortcut

class TestShortcut(unittest.TestCase):

    def test_get_shortcut(self):
        self.assertEquals(Shortcut('ctrl shift a').to_string(), 'control + shift + a')
        self.assertEquals(Shortcut('shift ctrl a').to_string(), 'control + shift + a')
        self.assertEquals(Shortcut('ctrl shift cmd option 7').to_string(), 'control + shift + option + command + 7')
        self.assertEquals(Shortcut('command ctrl a').to_string(), 'control + command + a')
        self.assertEquals(Shortcut('CMD ctrl a').to_string(), 'control + command + a')


    
if __name__ == '__main__':
    unittest.main()
