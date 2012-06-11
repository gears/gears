Changelog
=========

next release
------------

- Asset requirements are restricted by MIME type now, not by extension. E.g.,
  you can require Handlebars templates or JavaScript assets from CoffeeScript
  now.

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
