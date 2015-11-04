#!/usr/bin/env python

"""Tests for the Flask Heroku template."""

import unittest
from app import app


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_home_page_works(self):
        rv = self.app.get('/')
        self.assertTrue(rv.data)
        self.assertEqual(rv.status_code, 200)

    def test_about_page_works(self):
        rv = self.app.get('/about/')
        self.assertTrue(rv.data)
        self.assertEqual(rv.status_code, 200)

    def test_default_redirecting(self):
        rv = self.app.get('/about')
        self.assertEqual(rv.status_code, 301)

    def test_404_page(self):
        rv = self.app.get('/i-am-not-found/')
        self.assertEqual(rv.status_code, 404)

    def test_static_text_file_request(self):
        rv = self.app.get('/robots.txt')
        self.assertTrue(rv.data)
        self.assertEqual(rv.status_code, 200)
        rv.close()

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
'''

    def test_extract_repos(self):
        repos = pd._get_directory(self.plugins_raw)
        self.assertEqual(len(repos), 11)
        self.assertEqual(repos[8].name, 'adamhowell/random-opacity-sketch-plugin')
        self.assertEqual(repos[0].url, 'https://github.com/47deg/pointgrid')
        self.assertEqual(repos[9].description, '''Sketch Plugin to generate thaana strings, paragraphs, articles.''')

    def test_search_old_style_plugin(self):
        repos = pd._get_directory(self.plugins_raw)
        search_results = pd._search_old_style_plugin(repos)
        self.assertEqual(search_results, 'foo')
        #for result in search_results:
        #    self.assertEqual(result.repository, repo.name)

    def test_get_github_token(self):
        self.assertNotEqual(pd._get_github_token(), '')

    
if __name__ == '__main__':
    unittest.main()
