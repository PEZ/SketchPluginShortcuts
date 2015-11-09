# Sketch Plugin Shortcuts Inventory

(The source code for this [listing of Sketch plugin shortcuts](http:pluginshortcuts.herokuapp.com).)

This project is meant for developers of Sketch plugins who want to add non-conflicting keyboard shortcuts for their plugins.

## Work in progress

It's currently quite crude and begs for some sorting and filtering of the listing and whatnot. Also I'm thinking it should maybe provide an API that could be used for automatic duplication checking.

## Contribute

Fork the repository on GitHub. Then clone your fork:

    $ git clone git@github.com:<you>/<your fork>.git
    $ cd <your fork>

Then install `pip`, `foreman` and `heroku`. I'm on OS X and prefer to use `homebrew` when I can. In this case only `pip` has a tap, so:

    $ brew install pip
    $ pip install --upgrade pip setuptools

    $ sudo gem install foreman heroku

Further, you'll need to install `redis` on your dev machine. Using `homebrew` that becomes:

    $ brew install redis

Homebrew instructs you on how to start the redis server.

Now, setup an isolated environment with `virtualenv` and activate it:

    $ virtualenv --no-site-packages env
    $ . env/bin/activate

You should see your prompt return with a prefix of `(env)`. The project is based on [zachwill's](https://github.com/zachwill/) template for [Flask based Heroku apps](https://github.com/zachwill/flask_heroku). Have a look at that project's`README` for a discussion on how to deactivate and reactibvate the `virtualenv`environment.

Now install requirements into your isolated environment:

    $ pip install -r requirements.txt

Make sure the app knows you are running in `development` to enable debug logging.  Locally create a `.env` file and add:

    RUNTIME_ENVIRONMENT=development

The shortcut information is grabbed from GitHub via the GitHub API. You will need a personal GitHub access token. ([Read here how to create one.](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)) Update the `.env` file:

    GITHUB_TOKEN=your-token

You can now grab the shorcut data from GitHub. There's a `fabric` task for that:

    $ heroku local:run fab fetch_shortcuts

Now you are ready to run the web service locally:

    $ heroku local:run 'foreman start'

The application starts and is reachable on the default address of [http://localhost:5000/](http://localhost:5000/). However, while this is the most Heroku-like way to run the application, for some reason you do not get very much debug information from the output in the terminal. So, this is how I most often start the server locally:

    $ heroku local:run 'foreman run python app.py'

### Heroku

Before submitting a pull request should make sure the app handles a smoke test on Heroku. Create an Heroku app:

    $ heroku create <your app name>

Add the `Redis To Go` addon to your Heroku app. The free `nano` tier works for this project:

    $ heroku addons:create redistogo:nano

Configure environment variables:

    $ heroku config:set RUNTIME_ENVIRONMENT=production
    $ heroku config:set GITHUB_TOKEN=your-token

Deploy:

    $ git push heroku master

When it's deployed it's time to fetch the shortcut data:

    $ heroku run fab fetch_shortcuts

Now access your app on `http://<your-app-name>.herokuapp.com/`.

To schedule the fetching of shortcuts to happen automatically you'll need to add the `Scheduler` addon:

    $ heroku addons:create scheduler:standard

Then open the `Scheduler` dashboard:

    $ heroku addons:open scheduler

Add the add the job:

    fab fetch_shortcuts

And select how often you want it to run. **(Every 10th minute is probably more often than needed and also risks exhaust your GitHub API limit.)**


### Tests

Running the core tests:

    heroku local:run python test.py

There's also a `testapp.py` for checking that the Flask app is sane:

    heroku local:run python testapp.py

**NB: Some of the tests are a bit stupid** as I have had problems figuring out how to best factor the tests and the code under test because of the dependencies to the GitHub API and some other things. Contributions on this area is very welcome! There are also a lot of tests missing.

## Contact

I'm [@CoBPEZ](https://twitter.com/cobpez) on Twitter.

If you have suggestions please feel invited to file an issue. Pull requests are even more welcome. =)
