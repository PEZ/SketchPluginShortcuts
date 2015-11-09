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

Now, setup an isolated environment with `virtualenv`:

    $ virtualenv --no-site-packages env
    $ . env/bin/activate

You should see your prompt return with a prefix of `(env)`. Now install requirements into your isolated environment:

    $ pip install -r requirements.txt

The project is based on [zachwill's](https://github.com/zachwill/) template for [Flask based Heroku apps](https://github.com/zachwill/flask_heroku). Have a look at that project's`README` for a discussion on how to deactivate and reactibvate the `virtualenv`environment.

The shortcut information is grabbed from GitHub via the GitHub API. You will need a personal GitHub access token. [Read here how to create one.](https://help.github.com/articles/creating-an-access-token-for-command-line-use/) Then update the `GITHUB_TOKEN` configuration variable with your GitHub API Token. Locally create a `.env` file and add:

    GITHUB_TOKEN=your-token

You can now grab the shorcut data from GitHub. There's a `fabric` task for that:

    $ heroku local:run fab fetch_shortcuts

Now you are ready to run the web service locally:

    $ heroku local:run foreman run python app.py

`foreman` informs you where the service is running. The default is [http://localhost:5000/](http://localhost:5000/).

There is also a way to run the fetching of the shortcut information from the web browser - [http://localhost:5000/apport](http://localhost:5000/apport). Basic Auth is used to protect that route from non-admins. To use it you will  need these variables configured in the `.env`:

    ADMIN_USER_NAME=your-admin-user-name
    ADMIN_USER_PASSWORD=your-admin-user-password

### Heroku

Before submitting a pull request should make sure the app handles a smoke test on Heroku. Create an Heroku app:

    $ heroku create <your app name>


Add the `Redis To Go` addon to your Heroku app. The free `nano` tier works for this project:

    $ heroku addons:create redistogo:nano

To be able to run scheduled `fabric` tasks on Heroku, add the Scheduler addon:

    $ heroku addons:create scheduler:standard

Configure environment variables:

    $ heroku config:set GITHUB_TOKEN=your-token
    $ heroku config:set ADMIN_USER_NAME=your-admin-user-name
    $ heroku config:set ADMIN_USER_PASSWORD=your-admin-user-password

Deploy:

    $ git push heroku master

When it's done you can access your app on `http://your-app-name.herokuapp.com/`. The current version will give you a `500 Server Error` when there is no shortcut data fetched yet.  Use the `/apport` route to make your Heroku app fetch the shortcuts.

### Tests

For similar reasons as with the web app I also use `heroku local` for running the tests:

    heroku local:run python test.py

(All other ways of running the tests in a "Heroku-ish" manner I tried caused me to lose the traceback frames for failing tests.) 

There's also a `testapp.py` for checking that the Flask app is sane:

    heroku local:run python testapp.py

(It doesn't test the fetching of shortcuts info yet, since I haven't figured out how to not spam the GitHub API)

**NB: Some of the tests are a bit stupid** as I have had problems figuring out how to best factor both the tests and the code under test because of the dependencies to the GitHub API and some other things. Contributions on this area is very welcome! There are also a lot of tests missing.

## Contact

I'm [https://twitter.com/cobpez](\@CoBPEZ) on Twitter.

If you have suggestions please feel invited to file an issue. Pull requests are even more welcome. =)
