Changelog
=========

next release
------------

- SASS and SCSS compilers have been removed since they did nothing to really
  support SASS and SCSS compilation.

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


.. _SlimIt: http://slimit.org/
.. _cssmin: https://github.com/zacharyvoase/cssmin
