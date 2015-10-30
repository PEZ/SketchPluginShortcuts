import urllib2
import re
import string

DIRECTORY_RAW_URL='https://raw.githubusercontent.com/sketchplugins/plugin-directory/master/README.md'

class Plugin(object):
    name = ''
    url = ''
    description = ''

    def __init__(self, name, url='', description=''):
        self.name = name
        self.url = url
        self.description = description

def get_directory():
    return _get_directory(urllib2.urlopen(DIRECTORY_RAW_URL).read())

def _get_directory(raw):
    p = re.compile(r'^- \[(.+?)\]\((.+?)\) (.+)$', re.M)
    plugins = p.findall(raw)
    return [Plugin(plug[0], plug[1], plug[2]) for plug in plugins]
