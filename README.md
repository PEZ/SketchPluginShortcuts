# Sketch Plugin Shortcuts Inventory

(The source code for this [listing of Sketch plugin shortcuts](http:pluginshortcuts.herokuapp.com).)

## Work in progress

The main thing missing is that the listing fails to gather all shortcuts for all the plugin directories. This is becauase I currently rely on the `matched_text` fragment from the GitHub search API. The fragment contains at most two matches and also sometimes misses to include the shortcut information even for those matches. The fix will probably be to use GitHub's Content API to scan the `manifest.json` files.

## Contribute

The project is based on [zachwill's](https://github.com/zachwill/) template for [Flask based Heroku apps](https://github.com/zachwill/flask_heroku).

In addition to that the project uses GitHub API and you will need to use a configuration variable with your GitHUB API Token. Locally create a `.env` file and add:

    GITHUB_TOKEN=your-token

For Heroku do:

    heroku config:set GITHUB_TOKEN=your-token

I also use `redis` for storing the shortcut directory JSON blob. You'll need to install that on your dev machine and add the `Redis To Go` addon to your Heroku app. The free `nano` tier works for this project:

    heroku addons:create redistogo:nano

In order to run the actual fetching of the shortcut information (the `/apport` route), you will also need these variables configured in the `.env` file and on Heroku:

    ADMIN_USER_NAME=your-admin-user-name
    ADMIN_USER_PASSWORD=your-admin-user-password

In order for my local machine to read the `.env` variables and otherwise mimic the Heroku environment as much as possinble I start the server like so:

    heroku local:run foreman run python app.py

### Tests

For similar reasons as with the web app I also use `heroku local` for running the tests:

    heroku local:run python test.py

(All other ways of running the tests in a "Heroku-ish" manner I tried caused me to lose the traceback frames for failing tests.) 

There's also a `testapp.py` for checking that the Flask app is sane:

    heroku local:run python testapp.py

(It doesn't test the fetching of shortcuts info yet, since I haven't figured out how to not spam the GitHub API)

**NB: The tests are a bit stupid** as I have had problems figuring out how to best factor both the tests and the code under test because of the dependencies to the GitHub API and some other things. Contributions on this area is very welcome! There are also a lot of tests missing.

## Contact

I'm [https://twitter.com/cobpez](@CoBPEZ) on Twitter.

If you have suggestions please feel invited to file an issue. Pull requests are even more welcome. =)
