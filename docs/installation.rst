Installation
============

You can install Gears with pip_::

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

It is strongly recommended to install Gears within activated virtualenv_.

If you want to use one of available extensions (django-gears_, Flask-Gears_ or
gears-cli_), please refer to its documentation instead.

Installing the Development Version
----------------------------------

If you want to work with the latest version of Gears, install it from the
public repository (Git_ is required)::

    $ pip install -e git+https://github.com/gears/gears@develop#egg=Gears


.. _pip: http://www.pip-installer.org/
.. _virtualenv: http://virtualenv.org/
.. _Git: http://git-scm.com/

.. _django-gears: http://django-gears.readthedocs.org
.. _flask-gears: https://github.com/gears/flask-gears
.. _gears-cli: https://github.com/gears/gears-cli
