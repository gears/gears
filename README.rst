Gears
=====

Gears is a library to compile and concatenate JavaScript and CSS assets, highly
inspired by Ruby's Sprockets_. It includes support for writing scripts, styles
and client templates using CoffeeScript_, Handlebars_, Stylus_, Less_, SASS_
and SCSS_. New compilers can be also easily added.

There is also an app for Django called django-gears_ that integrates Gears
into Django project. You can read more on the project page.

Features
--------

* Dependency management using directives in header comments. For example::

      /* Dependencies:
       *= require jquery
       *= require underscore
       *= require backbone
       *= require_directory templates
       */

  Three directive types is supported for now:

  * ``require :path``: includes the contents of the asset ``path`` suffixed
    with the same extension as the current asset (e.g., if
    ``js/app.js.coffee`` has directive ``require views``,
    ``js/views.js.coffee`` will be included).

  * ``require_directory :path``: includes the contents of the every asset in
    the directory ``path`` with the same suffix as the current asset in
    alphabetical order.

  * ``require_self``: includes the contents of the current asset at the current
    place. If there is no ``require_self`` directive, the contents will be
    appended at the end of asset.

* Scripting and styling in modern languages like CoffeeScript, Stylus, Less,
  SASS and SCSS (support for new languages can be easily added).

* Writing client templates using Handlebars.

* The list of compilers for the asset is specified with asset
  extensions appended to the original extension. E.g., for the asset
  named ``js/app.js.coffee`` CoffeeScript compiler will be used. Here are
  extensions for the supported compilers:

  * CoffeeScript - ``.js.coffee``;
  * Handlebars - ``.js.handlebars``;
  * Stylus - ``.css.styl``;
  * Less - ``.css.less``;
  * SASS - ``.css.sass``;
  * SCSS - ``.css.scss``.

* Caching

Installation
------------

While there is no stable release of Gears yet, you can install it from this
repository using pip::

    pip install -e https://github.com/trilan/gears#egg=Gears

If you want to use compilers you need to install other dependencies:

* ``coffee-script``, ``handlebars``, ``stylus``, ``less`` node.js modules for
  CoffeeScript, Handlebars, Stylus, Less support respectively;
* ``sass`` Ruby gem for SASS and SCSS support.

Usage
-----

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
.. _SASS: http://sass-lang.com/
.. _SCSS: http://sass-lang.com/

.. _django-gears: https://github.com/trilan/django-gears
