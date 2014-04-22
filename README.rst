Settei: Config system which bases on entry points of setuptools
===============================================================

The ``settei`` package is a library which gives you possibility to get config settings from entry points for
specific application and environment.
Generic purpose python settings library which uses entry points as a registry.

Introduces terms ``application`` and ``environment``:

- ``application`` is part of group's name in which you are storing entry points.

- ``environment`` is name of entry point.


.. image:: https://api.travis-ci.org/paylogic/settei.png
   :target: https://travis-ci.org/paylogic/settei
.. image:: https://pypip.in/v/settei/badge.png
   :target: https://crate.io/packages/settei/
.. image:: https://coveralls.io/repos/paylogic/settei/badge.png?branch=master
   :target: https://coveralls.io/r/paylogic/settei


Installation
------------

.. sourcecode::

    pip install settei


Usage
-----

First of all you need to create entry points and put them into group, group comprises from two parts first of them is prefix
``settings_`` and second one is name of your application, e.g. ``settings_backoffice`` or ``settings_frontoffice``
where ``backoffice`` or ``frontoffice`` is your application.

.. code-block:: python

    # in your setup.py
    setup (
        # ...
        entry_points = {
            'settings_frontoffice': [
                'default = path.to.package.of.frontoffice.default_settings:generate_config',
                'local= path.to.package.of.frontoffice.local_settings:generate_config',
            ],
            'settings_backoffice': [
                'default = path.to.package.of.backoffice.default_settings:generate_config',
                'local= path.to.package.of.backoffice.local_settings:generate_config',
            ]
        }
        # ...
    )

The ``generate_config`` function should return instance of ``settei.config.Config`` class.

.. code-block:: python

    # default_settings.py
    from settei.config import Config


    def generate_config():
        config = Config()

        # adding some settings
        config['QUESTION'] = 'The Ultimate Question of Life, the Universe, and Everything'
        config['ANSWER'] = 41

        # or loading them from object
        config.from_pyfile('full/path/to/file.py')

        # or from object
        config.from_object('path.to.object')

        return config

You can also do inheriting one settings by others but only inside group of entry points, e.g if you want to inherit
default settings by local settings you just should mention name of entry point which you want to inherit

.. code-block:: python

    # in your local_settings.py file
    def generate_config(default):

        # changing settings, the right answer is 42
        default['ANSWER'] = 42

        return default

And if in your code you will get local settings and check them

.. code-block:: python

    >> from settei import get_config
    >> config = get_config('frontoffice', 'local')
    >> print config['QUESTION']
    The Ultimate Question of Life, the Universe, and Everything
    >> print config['ANSWER']
    42

Then you will need to install your package and after it with ``settei`` you will be able to get config settings for your
application.

.. code-block:: python

    from settei import get_config

    # get config settings for frontoffice application and local environment
    config = get_config('frontoffice', 'local')

    # get config settings for backoffice application and local environment
    config = get_config('backoffice', 'local')

    # now you can use it as you want
    DEBUG = config['DEBUG']

.. code-block:: bash

    # you can also get environment from CONFIG_ENVIRONMENT
    # just run your script/application in this way
    $ ENV CONFIG_ENVIRONMENT='dev' python my_incredible_script.py


.. code-block:: python

    # and in script you can use get_config like
    from settei import get_config

    # get config settings for frontoffice application and dev environment because we have already specified environment
    config = get_config('frontoffice')


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/paylogic/settei>`_.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `<LICENSE.txt>`_

© 2013 Paylogic International.
