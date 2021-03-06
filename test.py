#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the Plugin directory shortcuts service"""

import unittest
import re

from plugin_directory import PluginDirectory

class TestDirectory(unittest.TestCase):

    def setUp(self):
        self.raw = ''' # Sketch Plugin Directory

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
- [PEZ/Sketch-Plugin-Testing-Repo](https://github.com/PEZ/Sketch-Plugin-Testing-Repo) testing only
- [PEZ/SketchDistributor](https://github.com/pez/sketchdistributor) Distribute selection objects vertically or horizontally with a given spacing between them.
- [utom/sketch-measure](https://github.com/utom/sketch-measure) A measure tool for Sketch.app (think Specctr for Sketch)
'''
        self.pd = PluginDirectory(freezer_prefix='test-')
        self.pd.fetch_directory(raw_directory_text=self.raw)
        self.pd._repo_search_limit = 5

    def test_extract_repos(self):
        self.assertEqual(len(self.pd.repos), 14)
        self.assertEqual(self.pd.repos['adamhowell/random-opacity-sketch-plugin'].name, 'adamhowell/random-opacity-sketch-plugin')
        self.assertEqual(self.pd.repos['47deg/pointgrid'].url, 'https://github.com/47deg/pointgrid')
        self.assertEqual(self.pd.repos['ajaaibu/thaanatext'].description, '''Sketch Plugin to generate thaana strings, paragraphs, articles.''')
        self.assertEqual(self.pd.repos['pez/sketch-plugin-testing-repo'].description, '''testing only''')

    def test_build_search_query_repos_string(self):
        queries = list(self.pd._build_search_query_repos_string())
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
        self.assertEqual(self.pd._extract_shortcuts_old_style_from_text(text)[0], 'shift cmd o')
        
    def test_extract_shortcut_plugin_bundle_from_text(self):
        text = '''{
          "name": "Sketch Mate",
          "description": "These plugins will make you best friends with Sketch",
          "author": "Florian Schulz",
          "homepage": "https://github.com/getflourish/Sketch-Mate",
          "version": 1.0,
          "identifier": "com.getflourish.sketch.mate",
          "updateURL": "https://github.com/downloads/example/sketchplugins/sketchplugins.json",
          "compatibleVersion": 3.3,
          "bundleVersion": 1,
          "commands": [

            {
              "name": "Duplicate Artboard",
              "identifier": "com.getflourish.mate.artboards.duplicate",
              "shortcut": "shift command d",
              "script": "Artboards/Duplicate Artboard.js"
            },
            {
              "name": "Fit Artboard",
              "identifier": "com.getflourish.mate.artboards.fitArtboard",
              "shortcut": "",
              "script": "Artboards/Fit Artboard.js"
            },
            {
              "name": "Remove Artboard",
              "identifier": "com.getflourish.mate.artboards.remove",
              "shortcut": "cmd shift ⌫",
              "script": "Artboards/Remove Artboard.js"
            },
            {
              "name": "Sort Artboards by Position",
              "identifier": "com.getflourish.mate.artboards.sortByPosition",
              "shortcut": "",
              "script": "Artboards/Sort Artboards by Position.js"
            },

            {
              "name": "Goto Artboard",
              "identifier": "com.getflourish.mate.misc.gotoArtboard",
              "shortcut": " ",
              "script": "Misc/Goto Artboard.js"
            },
            {
              "name": "Distribute Horizontally",
              "identifier": "com.getflourish.mate.smartAlign.distributeHorizontally",
              "shortcut": "control option cmd ,",
              "script": "Smart Align/Distribute Horizontally.js"
            },
            {
              "name": "Distribute Vertically",
              "identifier": "com.getflourish.mate.smartAlign.distributeVertically",
              "shortcut": "control option cmd .",
              "script": "Smart Align/Distribute Vertically.js"
            },
            {
              "name": "Space Horizontally",
              "identifier": "com.getflourish.mate.smartAlign.spaceHorizontally",
              "shortcut": "command Ö",
              "script": "Smart Align/Space Horizontally.js"
            },
            {
              "name": "Space Vertically",
              "identifier": "com.getflourish.mate.smartAlign.spaceVertically",
              "shortcut": "command Ä",
              "script": "Smart Align/Space Vertically.js"
            },
            {
              "name": "Pull Up",
              "identifier": "com.getflourish.mate.smartMove.pullUp",
              "shortcut": "shift cmd option ↑",
              "script": "Smart Move/Pull Up.js"
            },
            {
              "name": "Push Down",
              "identifier": "com.getflourish.mate.smartMove.pushDown",
              "shortcut": "shift cmd option ↓",
              "script": "Smart Move/Push Down.js"
            },
            {
              "name": "Pull Left",
              "identifier": "com.getflourish.mate.smartMove.pullLeft",
              "shortcut": "shift cmd option ←",
              "script": "Smart Move/Pull Left.js"
            },
            {
              "name": "Push Right",
              "identifier": "com.getflourish.mate.smartMove.pushRight",
              "shortcut": "shift cmd option →",
              "script": "Smart Move/Push Right.js"
            }

          ],
          "menu": {
            "items": [
                {
                   "title": "Artboards",
                   "items": [ '''
        shortcuts = self.pd._extract_shortcuts_plugin_bundle_from_text(text) 
        self.assertEqual(len(shortcuts), 10)
        self.assertEqual(shortcuts[0], u'shift command d')
        self.assertEqual(shortcuts[1], u'cmd shift ⌫')
        self.assertEqual(shortcuts[2], u'control option cmd ,')
        self.assertEqual(shortcuts[3], u'control option cmd .')
        self.assertEqual(shortcuts[4], u'command Ö')
        self.assertEqual(shortcuts[5], u'command Ä')
        self.assertEqual(shortcuts[6], u'shift cmd option ↑')
        self.assertEqual(shortcuts[7], u'shift cmd option ↓')
        self.assertEqual(shortcuts[8], u'shift cmd option ←')
        self.assertEqual(shortcuts[9], u'shift cmd option →')

    def test_fetch_and_add_shortcuts_to_repo(self):
        test_repo_name = 'PEZ/Sketch-Plugin-Testing-Repo'
        test_repo_found = False
        for repo in self.pd._fetch_and_add_shortcuts_to_directory():
            if repo.name == test_repo_name:
                test_repo_found = True
                self.assertEqual(len(self.pd.repos[test_repo_name].shortcuts), 1)
                self.assertEqual(self.pd.repos[test_repo_name].shortcuts[0].to_string(), u'shift + command + d')
                self.assertEqual(self.pd.repos[test_repo_name].shortcuts[1].to_string(), u'shift + command + ⌫')
                self.assertEqual(self.pd.repos[test_repo_name].shortcuts[2].to_string(), u'control + option + command + ,')
                self.assertEqual(self.pd.repos[test_repo_name].shortcuts[3].to_string(), u'control + option + command + .')
                self.assertEqual(self.pd.repos[test_repo_name].shortcuts[4].to_string(), u'command + Ö')
                self.assertEqual(self.pd.repos[test_repo_name].shortcuts[5].to_string(), u'command + Ä')
                self.assertEqual(self.pd.repos[test_repo_name].shortcuts[6].to_string(), u'shift + option + command + ↑')
                self.assertEqual(self.pd.repos[test_repo_name].shortcuts[7].to_string(), u'shift + option + command + ↓')
                self.assertEqual(self.pd.repos[test_repo_name].shortcuts[8].to_string(), u'shift + option + command + ←')
                self.assertEqual(self.pd.repos[test_repo_name].shortcuts[9].to_string(), u'shift + option + command + →')
        self.assertTrue(test_repo_found)

    def test_fetch_shortcuts_from_forked_repo(self):
        pd = PluginDirectory('test-')
        pd.fetch_directory(raw_directory_text='''- [PEZ/Sketch-Plugin-Testing-Repo](https://github.com/PEZ/Sketch-Plugin-Testing-Repo) testing only''')
        forked_repo_name = ''
        forked_repo_found = False
        for repo in pd._search_plugin_bundle():
            if repo.name == forked_repo_name:
                forked_repo_found = True
        self.assertTrue(forked_repo_found)

    def test_get_shortcuts_old_style(self):
        pass

    def test_add_shortcuts_for_repo_to_directory(self):
        repo_shortcuts = self.pd._fetch_shortcuts()
        for r, s in repo_shortcuts:
            self.pd._add_shortcuts_for_repo_to_directory(r.lower(), s)
            self.assertEqual(self.pd.repos[r].shortcuts, s)
        self.assertEqual(len(self.pd.repos['adamhowell/random-opacity-sketch-plugin'].shortcuts), 1)
        self.assertEqual(self.pd.repos['adamhowell/random-opacity-sketch-plugin'].shortcuts[0].to_string(), 'shift + command + o')
        self.assertEqual(len(self.pd.repos['pez/sketchdistributor'].shortcuts), 2)
        self.assertEqual(self.pd.repos['pez/sketchdistributor'].shortcuts[0].to_string(), u'control + option + d')

    def test_get_github_token(self):
        self.assertNotEqual(self.pd._github_token, '')

    def test_freeze_thaw(self):
        self.pd._freeze(self.pd.repos, 'test-')
        thawed= self.pd._thaw('test-')
        self.assertEqual(self.pd.repos['adamhowell/random-opacity-sketch-plugin'].description, thawed['adamhowell/random-opacity-sketch-plugin'].description)


from plugin_directory import Shortcut

class TestShortcut(unittest.TestCase):

    def test_get_shortcut(self):
        self.assertEquals(Shortcut(u'ctrl shift a').to_string(), u'control + shift + a')
        self.assertEquals(Shortcut(u'shift ctrl a').to_string(), u'control + shift + a')
        self.assertEquals(Shortcut(u'ctrl shift cmd option 7').to_string(), u'control + shift + option + command + 7')
        self.assertEquals(Shortcut(u'command ctrl a').to_string(), u'control + command + a')
        self.assertEquals(Shortcut(u'CMD ctrl a').to_string(), u'control + command + a')
        self.assertEquals(Shortcut(u'shift cmd option ↑').to_string(), u'shift + option + command + ↑')


    
if __name__ == '__main__':
    unittest.main()
