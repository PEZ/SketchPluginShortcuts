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

import plugin_directory as pd

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
'''

    def test_extract_plugins(self):
        plugins = pd._get_directory(self.plugins_raw)
        self.assertEqual(len(plugins), 10)
        self.assertEqual(plugins[8].name, 'adamhowell/random-opacity-sketch-plugin')
        self.assertEqual(plugins[0].url, 'https://github.com/47deg/pointgrid')
        self.assertEqual(plugins[9].description, '''Sketch Plugin to generate thaana strings, paragraphs, articles.''')


    
if __name__ == '__main__':
    unittest.main()
