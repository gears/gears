Gears
=====

.. image:: https://secure.travis-ci.org/gears/gears.png?branch=develop
    :target: https://travis-ci.org/gears/gears

Gears is a library to compile and concatenate JavaScript and CSS assets, highly
inspired by Ruby's Sprockets_. You can also write scripts, styles and client
templates using CoffeeScript_, Handlebars_, Stylus_, Less_, and compile them
using external packages (gears-coffeescript_, gears-handlebars_, gears-stylus_,
gears-less_). These packages already include all required node.js modules, so
you don't need to worry about installing them yourself.

There is also:

- django-gears_, an app for Django that integrates Gears with Django project;
- Flask-Gears_, an extension that integrates Gears with Flask application;
- gears-cli_, a command-line utility that compiles assets. It also can watch
  assets for changes and automaticaly re-compile them.

Features
--------

* Dependency management using directives in header comments. For example::

      /* Dependencies:
       *= require jquery
       *= require underscore
       *= require backbone
       *= require_tree views
       *= require_directory templates
       */

  Five directive types is supported for now:

  * ``require :path``: includes the contents of the asset ``path`` suffixed
    with the same extension as the current asset (e.g., if
    ``js/app.js.coffee`` has directive ``require views``,
    ``js/views.js.coffee`` will be included).

  * ``require_directory :path``: includes the contents of the every asset in
    the directory ``path`` with the same suffix as the current asset in
    alphabetical order.

  * ``require_tree :path``: includes the contents of the every asset with the
    same suffix as the current asset in the directory ``path`` and all its
    subdirectories in alphabetical order.

  * ``require_self``: includes the contents of the current asset at the current
    place. If there is no ``require_self`` directive, the contents will be
    appended at the end of asset.

  * ``depend_on :path``: it is useful when you need to specify files that
    affect an asset, but not to include them into bundled asset or to include
    them using compilers. E.g., if you use ``@import`` functionality in some
    CSS pre-processors (Less or Stylus).

* Scripting and styling in modern languages like CoffeeScript, Stylus, Less
  (support for new languages can be easily added).

* Writing client templates using Handlebars.

* The list of compilers for the asset is specified with asset
  extensions appended to the original extension. E.g., for the asset
  named ``js/app.js.coffee`` CoffeeScript compiler will be used. Here are
  extensions for the supported compilers (through external packages):

  * CoffeeScript - ``.js.coffee``;
  * Handlebars - ``.js.handlebars``;
  * Stylus - ``.css.styl``;
  * Less - ``.css.less``.

* Caching

* Compressing. Supported compressors:

  * SlimIt_ (Python, 2.X only);
  * cssmin_ (Python, 2.X only);
  * UglifyJS_ (Node.js, using gears-uglifyjs_);
  * clean-css_ (Node.js, using gears-clean-css_).

  New compilers can be also easily added.

* Supports Python 3.

Installation
------------

You can install ``Gears`` using pip::

    $ pip install Gears

If you want to use node.js-dependent compilers or compressors, you need to
install other dependencies::

    $ pip install gears-less          # LESS
    $ pip install gears-stylus        # Stylus
    $ pip install gears-handlebars    # Handlebars
    $ pip install gears-coffeescript  # CoffeeScript

    $ pip install gears-uglifyjs      # UglifyJS
    $ pip install gears-clean-css     # clean-css

Please note that all these compilers and compressors require node.js to be
installed on your system.

Usage
-----

This example compiles public assets (default: ``assets/js/script.js``,
``assets/css/style.css`` and all assets that aren't compiled to .css or .js)
from ``assets`` directory to ``static``::

    import os

    from gears.environment import Environment
    from gears.finders import FileSystemFinder


    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    ASSETS_DIR = os.path.join(ROOT_DIR, 'assets')
    STATIC_DIR = os.path.join(ROOT_DIR, 'static')

    env = Environment(STATIC_DIR)
    env.finders.register(FileSystemFinder([ASSETS_DIR]))
    env.register_defaults()

    if __name__ == '__main__':
        env.save()

There is already mentioned django-gears_ app, which you may want to use in
your Django projects.

Contributing
------------

Feel free to fork, send pull requests or report bugs and issues on github.


.. _Sprockets: http://getsprockets.org
.. _CoffeeScript: http://jashkenas.github.com/coffee-script/
.. _Handlebars: http://www.handlebarsjs.com/
.. _Stylus: http://learnboost.github.com/stylus/
.. _Less: http://lesscss.org/
.. _SlimIt: http://slimit.org/
.. _cssmin: https://github.com/zacharyvoase/cssmin
.. _UglifyJS: https://github.com/mishoo/UglifyJS
.. _clean-css: https://github.com/GoalSmashers/clean-css

.. _gears-less: https://github.com/gears/gears-less
.. _gears-stylus: https://github.com/gears/gears-stylus
.. _gears-handlebars: https://github.com/gears/gears-handlebars
.. _gears-coffeescript: https://github.com/gears/gears-coffeescript

.. _gears-uglifyjs: https://github.com/gears/gears-uglifyjs
.. _gears-clean-css: https://github.com/gears/gears-clean-css

.. _django-gears: https://github.com/gears/django-gears
.. _flask-gears: https://github.com/gears/flask-gears
.. _gears-cli: https://github.com/gears/gears-cli
