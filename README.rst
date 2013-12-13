Settei: Config system which bases on entry points of setuptools
===============================================================

The ``settei`` package is a library which gives you possibility to get config settings from entry points for
specific application and environment.
Generic purpose python settings library which uses entry points as a registry.

Introduces terms ``application`` and ``environment``:

- ``application`` is part of group's name in which you are storing entry points

- ``environment`` is name of entry point


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
            'settings_backoffice': [
                'default = path.to.package.of.settings:generate_config',
            ]
        }
        # ...
    )

The ``generate_config`` function should return instance of ``settei.config.Config`` class.

.. code-block:: python

    def generate_config():
        config = Config()

        # adding some settings
        config['ANSWER'] = 42

        # or loading them from object
        config.from_pyfile('full/path/to/file.py')

        # or from object
        config.from_object('path.to.object')

        return config

Then you will need to install your package and after it with ``settei`` you will be able to get config settings for your
application.


.. code-block:: python

    from settei import get_config

    # get config settings for frontoffice application and dev environment
    config = get_config('frontoffice', 'dev')

    # get config settings for backoffice application and staging environment
    config = get_config('frontoffice', 'dev')

    # your config can be any structure which you want
    DEBUG = config['DEBUG']

    # or even
    DEBUG = config.DEBUG

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