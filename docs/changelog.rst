Changelog
=========

next release
------------

- Add ability to disable asset fingerprinting. This can be useful, if you want
  to compile assets for humans.

0.6 (2013-04-28)
----------------

- Add processor to add missing semicolons to the end of JavaScript sources.

- Add gzip support.

- Add support for cache busting. This is done through fingerprinting public
  assets.

- Fix unknown extensions handling. Thanks @xobb1t for the report.

- Fix cssmin and slimit compressors.

0.5.1 (2012-10-16)
------------------

- Fix saving handled assets.

- Python 3.3 is also supported.

0.5 (2012-10-16)
----------------

- Support for Python 3.2 was added (Thanks to `Artem Gluvchynsky`_).

  .. note::

     SlimIt and cssmin compressors don't support Python 3 yet. But you can
     use compressors from gears-uglifyjs_ and gears-clean-css_ packages
     instead.

.. _Artem Gluvchynsky: https://github.com/excieve

0.4 (2012-09-23)
----------------

- Public assets storage was simplified. There is no registry for them anymore.
  They are set using ``public_assets`` param of
  :class:`~gears.environment.Environment` now.

  Also, public assets handling was slightly improved. ``public_assets`` must be
  a list or tuple of callables or regexps now. Default value::

      DEFAULT_PUBLIC_ASSETS = (
          lambda path: not any(path.endswith(ext) for ext in ('.css', '.js')),
          r'^css/style\.css$',
          r'^js/script\.js$',
      )

  ``css/style.css``, ``js/script.js`` and all assets that aren't compiled to
  .css or .js are public by default.

- Added ``require_tree`` directive. It works like ``require_directory``, but
  also collects assets from subdirectories recursively.

- Node.js-dependent compilers (CoffeeScript, Handlebars, Stylus and LESS) and
  compressors (UglifyJS and clean-css) have been moved into separate packages
  (gears-coffeescript_, gears-handlebars_, gears-stylus_, gears-less_,
  gears-uglifyjs_, gears-clean-css_), as they required some additional work to
  make them work (install some node.js modules, point your app to them, etc.).
  Now all these packages already include all required node.js modules, so you
  don't need to worry about installing them yourself.

- SASS and SCSS compilers have been removed since they did nothing to really
  support SASS and SCSS compilation.

- Support for Python 2.5 was dropped.

0.3 (2012-06-24)
----------------

- Added ``depend_on`` directive. It is useful when you need to specify files
  that affect an asset, but not to include them into bundled asset or to
  include them using compilers. E.g., if you use ``@import`` functionality in
  some CSS pre-processors (Less or Stylus).

- Main extensions (``.js`` or ``.css``) can be omitted now in asset file names.
  E.g., you can rename ``application.js.coffee`` asset to
  ``application.coffee``.

- Asset requirements are restricted by MIME type now, not by extension. E.g.,
  you can require Handlebars templates or JavaScript assets from CoffeeScript
  now.

- Added file-based cache.

- Environment cache is pluggable now.

- Fixed cache usage in assets.

0.2 (2012-02-18)
----------------

- Fix ``require_directory`` directive, so it handles removed/renamed/added
  assets correctly. Now it adds required directory to asset's dependencies set.

- Added asset dependencies. They are not included to asset's bundled source,
  but if dependency is expired, then asset is expired. Any file of directory
  can be a dependency.

- Cache is now asset agnostic, so other parts of Gears are able to use it.

- Added support for SlimIt_ as JavaScript compressor.

- Added support for cssmin_ as CSS compressor.

- Refactored compressors, compilers and processors. They are all subclasses of
  :class:`~gears.asset_handler.BaseAssetHandler` now.

- Added config for Travis CI.

- Added some docs.

- Added more tests.

0.1.1 (2012-02-26)
------------------

- Added missing files to MANIFEST.in

0.1 (2012-02-26)
----------------

First public release.


.. _gears-less: https://github.com/gears/gears-less
.. _gears-stylus: https://github.com/gears/gears-stylus
.. _gears-handlebars: https://github.com/gears/gears-handlebars
.. _gears-coffeescript: https://github.com/gears/gears-coffeescript

.. _gears-uglifyjs: https://github.com/gears/gears-uglifyjs
.. _gears-clean-css: https://github.com/gears/gears-clean-css

.. _SlimIt: http://slimit.org/
.. _cssmin: https://github.com/zacharyvoase/cssmin
