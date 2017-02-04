Modern Paste
===========

[![Build Status](https://travis-ci.org/LINKIWI/modern-paste.svg?branch=master)](https://travis-ci.org/LINKIWI/modern-paste) [![Coverage Status](https://coveralls.io/repos/LINKIWI/modern-paste/badge.svg?branch=master&service=github)](https://coveralls.io/github/LINKIWI/modern-paste?branch=master) [![Join the chat at https://gitter.im/LINKIWI/modern-paste](https://badges.gitter.im/LINKIWI/modern-paste.svg)](https://gitter.im/LINKIWI/modern-paste?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

![Screenshot](http://i.imgur.com/BPvBFl2.png)

## About

**Modern Paste** is a self-hosted Pastebin alternative that is
+ Visually pleasing, with a contemporary and minimalistic user interface
+ Feature-rich
+ Mobile-friendly
+ Open source
+ Backed by a robust, RESTful API
+ Apache WSGI-friendly
+ Easy to install and highly configurable
+ [Impressively well-tested](https://coveralls.io/github/LINKIWI/modern-paste)

[**Live demo site**](https://demo.modernpaste.com)

Modern Paste is intended for system administrators who wish to host their own installation of a code/text Pastebin on personal servers. It's free and open source: contributions from the developer community are encouraged and always welcome.

## Features

+ Modern user interface with a consistent design language
+ Syntax highlighting for [all languages supported by CodeMirror](https://codemirror.net/mode/)
+ Ability to set paste expiration dates
+ Ability to password-protect pastes
+ Full user account functionality
	+ Associate new pastes with a user account
	+ View, modify, or delete pastes posted with a user account
	+ Directly query the Modern Paste API with the account's API key/authtoken
+ Public archive of pastes, sorted reverse chronologically or by popularity
+ RESTful API for externally creating, reading, and managing pastes
+ Ability to enforce security restrictions: can configure that only authenticated users can post pastes (ideal for private, non-public-facing installations)
+ Ability to encrypt the front-facing-display of paste IDs (e.g. so that `/paste/1` might display as `/paste/9~AEygplxfCPHW4eJctbjMnRi-rYnlYzizqToCmG3BY=`)

## Installation

*The following instructions assume an Apache web server, though any WSGI-aware server should work.*

1. **Meet all prerequisites.**
   In order to build the application locally, you **must** have the following installed:
   + MySQL - Used as Modern Paste's persistent data store. Make sure you know the password to the `root` (or equivalent) user.
   + Python - Implementation language of Modern Paste's backend. **Python version 2.7+ is required**, as the backend makes use of language features not available in 2.6 and earlier.
   + Java - Used to compile compile controllers into single `.js` files.
   + Package managers `pip`, `gem`, and `npm` - Used for fulfilling application dependencies.

   If you have all of the above, you should be able to run all tests and build the application.

2. **Get the code.**
   ```bash
   $ git clone https://github.com/LINKIWI/modern-paste /modern-paste/installation/directory
   ```

3. **Initialize the MySQL database for Modern Paste.**
   You will need to create a new MySQL user that has R/W privileges to the Modern Paste databases. (You may use the default `root` user, but it is highly recommended to create a separate user that only has access to the databases that Modern Paste will use.)
   First, generate a secure password for the new database user.
   ```bash
   $ pwgen -s 96 1
   ```
   Then, open up a session to your MySQL server as `root` (the below will prompt you for the `root` password to authenticate).
   ```bash
   $ mysql -u root -p
   ```
   You'll need to create the new user and all the databases Modern Paste will use. *If you only need a production environment and don't plan on running the unit tests on your local server, you may skip creation of the `dev` and `test` databases. However, it's recommended that you create all three.*
   ```sql
   CREATE USER 'modern_paste'@'localhost' IDENTIFIED BY '<password>';
   CREATE DATABASE modern_paste;
   CREATE DATABASE modern_paste_dev;
   CREATE DATABASE modern_paste_test;
   GRANT ALL ON modern_paste.* TO 'modern_paste'@'localhost';
   GRANT ALL ON modern_paste_dev.* TO 'modern_paste'@'localhost';
   GRANT ALL ON modern_paste_test.* TO 'modern_paste'@'localhost';
   FLUSH PRIVILEGES;
   ```
   `<password>` is the output of `pwgen` above, or your own password. Please be aware that this password will be stored in plain text in the Modern Paste configuration file.

4. **Modify the configuration file to customize your installation.**
   In the directory the code was cloned to, modify the file `app/config.py` to customize your install of Modern Paste. Each setting is accompanied with fairly extensive documentation, but below is a summary of fields that you are **required** to set in order to continue (it's recommended you take a look at the other configuration options as well, but these are the bare minimum to get the app up and running):
   + `DOMAIN` - Set this to the external domain name at which Modern Paste will be hosted. *This doesn't impact your web server configuration; it's only used for generating URLs within the app.*
   + `DEFAULT_HTTPS` - Set this to `True` or `False` depending on whether you plan to host Modern Paste behind an SSL-secured domain. *This doesn't impact your web server configuration; it's only used for generating URLs within the app.*
   + `BUILD_ENVIRONMENT` - Choose whether this particular installation should run in a dev or production environment. The production environment will use the `modern_paste` database and will serve minified CSS and [Closure](https://developers.google.com/closure/compiler/)-compiled Javascript. The dev environment will use the `modern_paste_dev` database and will serve unminified CSS and non-compiled Javascript.
   + `DATABASE_PASSWORD` - The password for the `modern_paste` MySQL account from step 3.
   + `DATABASE_NAME` and `DATABASE_USER` - If you created the user and databases in step 3 as it is shown above, there's no need to modify these from their default values.
   + `FLASK_SECRET_KEY` - For security reasons, replace the string here with the output of `os.urandom(32)` from a Python shell.

5. **Build the app.**
   At this point, before continuing, ensure you have the MySQL and Python dev packages installed. This corrects common errors during the `make dependencies` stage of the build. To avoid conflicts with the system Python's modules, it is recommended to use [pyenv](https://github.com/yyuu/pyenv) so the app's Python dependencies remain segregated from the base system's environment.
   ```bash
   $ sudo apt-get install build-essential python-dev libmysqlclient-dev
   ```
   Or for Fedora/RedHat variants:
   ```bash
   $ sudo dnf install python-devel community-mysql-devel redhat-rpm-config mod_wsgi gem npm community-mysql-server
   $ sudo dnf groupinstall "C Development Tools and Libraries"
   $ sudo dnf groupinstall "Development Tools"
   ```
   Then, in the directory you cloned the repository to:
   ```bash
   $ sudo make
   ```
   This will:
   + Install dependencies via `pip` and `gem`, and initialize this repository's submodules.
   + Run all tests.
   + Create all tables in the database.
   + Compile CSS and Javascript depending on the `BUILD_ENVIRONMENT` constant set in `app/config.py`.

6. **Add an Apache virtual host entry.**
   Below is an example entry you can add to your virtual hosts file to serve the app via Apache over HTTP. If you don't already have `mod_wsgi` installed, [you should do so now](https://modwsgi.readthedocs.org/en/develop/).
   ```apache
   <VirtualHost *:80>
       ServerName modernpaste.example.com
       DocumentRoot /modern-paste/installation/directory
       WSGIScriptAlias / /modern-paste/installation/directory/modern_paste.wsgi

       ErrorLog ${APACHE_LOG_DIR}/modernpaste-error.log
       CustomLog ${APACHE_LOG_DIR}/modernpaste-access.log combined
   </VirtualHost>
   ```
   You're almost ready to go! Reload the Apache configuration:
   ```bash
   $ sudo service apache2 reload
   ```
   If you visit `http://modernpaste.example.com`, you should be presented with your installation of Modern Paste.

## Contributing

Contributions from the developer community lie at the heart of open source software. Contributions to Modern Paste--in the form of new features, bug fixes, or anything else--are encouraged and always welcome. Please read the Workflow section carefully on how to get started. The Continuous Integration and Testing sections describe practices on ensuring the integrity of Modern Paste.

#### Workflow

This project follows the standard [git-flow workflow](https://es.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow). In a nutshell, the `dev` branch serves as an integration branch for new features and fixes, and the `master` branch serves as the project's stable release branch.

To contribute, you should

1. Fork this project to your own account
2. `git checkout dev` (Make sure to do this, since `master` is the default branch)
3. Create a new branch (based off `dev`), with a name that describes the change you're making (e.g. `feature-x` or `fix-bug-y`)
4. Write code. Write tests. Push commits.
5. When you're ready to merge your work into the main Modern Paste repository, create a pull request to merge your work into the `dev` branch.
6. If your build passes on Travis and your code is thoroughly tested, your work will be merged into `dev`, and eventually make its way into `master`.

#### Development

The app's backend infrastructure lives in `app/database` and `app/api`. Templates live in `app/templates`, and SCSS/Javascript lives in `app/static/scss` and `app/static/js`. SCSS and JS builds are handled automatically by the templating system.

As a general guideline,

+ Operations that directly interact with the database (e.g. reading or creating a paste) should reside in the appropriate file in `database` module. Modern Paste follows the exceptional design pattern, and since these methods exist at the lowest level of the stack, these methods should throw exceptions that are handled at a higher level of the stack.
+ Any database method that will be queried from the frontend (by an AJAX call) should have a corresponding endpoint path defined in the relevant file in the `uri` module, and an API method in the relevant file in the `api` module.
+ All new SCSS should be in a [partial](http://sass-lang.com/guide), and imported by `app/static/scss/stylesheet.scss`. The templates fetch CSS from the `app/static/build` directory, so you should have a Sass watcher compiling your SCSS in the background: `sass --watch app/static/scss:app/static/build/css --style compressed`.
+ Modern Paste makes use of the [Google Closure Library](https://developers.google.com/closure/library/) and [Closure Compiler](https://developers.google.com/closure/compiler/). Place controllers under the appropriate module in `app/static/js` as `xxxxxController.js`, and be sure to import it in the template using the existing `import_js` templating utility. `make prod` will generate Closure-compiled controllers, and the `import_js` utility will automatically point to the compiled single file.

#### Continuous Integration

Modern Paste uses [Travis CI](https://travis-ci.org/LINKIWI/modern-paste) as a continuous integration system. The CI build
+ Runs all Python, SCSS, JSON, and yaml linters
+ Checks for stylistic errors (missing newline at end of file, trailing whitespace, etc.)
+ Runs all Python tests
+ Reports test coverage statistics
+ Builds CSS and Closure-compiles Javascript controllers

Your pull request must pass the build in order to be merged. You can run everything Travis runs locally with `make check-style`, `make test-coverage`, and `make prod`.

#### Testing

[Modern Paste has high standards of testing](https://coveralls.io/github/LINKIWI/modern-paste): every line of Python should be tested. This is to ensure accuracy of your intended changes, and to make sure future changes don't break existing functionality.

This means
+ Every new Python component should be accompanied with one or more unit tests.
+ Changes to existing code should be accompanied with changes to existing unit tests.
+ You should run existing unit tests frequently to ensure that you're not breaking existing functionality. If existing unit tests fail, decide if it was intentional (in which case the old tests should be updated to reflect the new behavior), or if you've accidentally broken something that shouldn't be broken.

## License

This work is licensed under the MIT license.
