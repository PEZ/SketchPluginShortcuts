"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
"""

import os
import re
from flask import Flask, render_template, request, redirect, url_for, Response, config

from flask_sslify import SSLify

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

app = Flask(__name__)
if 'DYNO' in os.environ: # only trigger SSLify if the app is running on Heroku
    sslify = SSLify(app)

@app.context_processor
def inject_FB_APP_ID():
    return dict(FB_APP_ID = os.environ.get('FB_APP_ID', 'configure this in the Heroku environment'))

@app.context_processor
def inject_GA_UA_ID():
    return dict(GA_UA_ID = os.environ.get('GA_UA_ID', 'configure this in the Heroku environment'))

# request.url seems to always be http: ...
@app.context_processor
def inject_LISTING_BASE_URL():
    return dict(REQUEST_URL = re.sub(r'^http:', 'https:', request.url))

###
# Routing
###

@app.route('/')
def home():
    """Render website's home page."""
    from plugin_directory import PluginDirectory as pd
    plugins = [plugin for plugin in pd.get_directory().values() if len(plugin.shortcuts) > 0]
    return Response(stream_template('home.html', plugins=sorted(plugins, key=lambda p: p.name.lower())))

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    debug = False
    if os.environ.get('RUNTIME_ENVIRONMENT', '') == 'development':
        debug = True
    app.run(debug=debug)
