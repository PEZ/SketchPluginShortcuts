"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, Response

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

from functools import wraps

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    import os
    admin_user_name = os.environ.get('ADMIN_USER_NAME','')
    if admin_user_name == '':
        return False
    admin_user_password = os.environ.get('ADMIN_USER_PASSWORD','')
    if admin_user_password == '':
        return False
    return username == admin_user_name and password == admin_user_password

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    from plugin_directory import PluginDirectory as pd
    plugins = [plugin for plugin in pd.get_directory().values() if len(plugin.shortcuts) > 0]
    return render_template('home.html', plugins=sorted(plugins, key=lambda p: p.name.lower()))

@app.route('/apport')
@requires_auth
def apport():
    """Fetch shortcuts and render"""
    from plugin_directory import PluginDirectory as pd
    plugins = pd.fetch_directory(pd.REPO_SEARCH_LIMIT)
    return Response(stream_template('apport.html', plugins=plugins))

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
    app.run(debug=True)
