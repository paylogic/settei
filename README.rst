Settei
######

:code:`settei` is a generic purpose python settings library based on the concept of
entry points as a registry, inspired by
`setuptools <http://pythonhosted.org/setuptools/pkg_resources.html#entry-points>`_.

It introduces terms ``environment``, ``group``, and ``application``:

* **environment** is the name of an entry point
* **group** is a group of defined environments
* **application** is part of a group's name and refers to the application to which
  settings apply

.. image:: https://api.travis-ci.org/paylogic/settei.png
   :target: https://travis-ci.org/paylogic/settei
.. image:: https://pypip.in/v/settei/badge.png
   :target: https://crate.io/packages/settei/
.. image:: https://coveralls.io/repos/paylogic/settei/badge.png?branch=master
   :target: https://coveralls.io/r/paylogic/settei

A minimal app that illustrates the use of `settei` can be found
`here <https://github.com/paylogic/settei-example>`_.

Installation
============

.. sourcecode::

    pip install settei

Usage
=====

Define groups and environments
------------------------------

:code:`settei` can be configured and used in a series of simple steps.

As a first step, we need to define environments and put them into groups. We are
free to choose the name of the function to be used as an entry point. In this case,
we chose the name :code:`generate_config`. Let's assume that our package contains
two applications.

.. code-block:: python

    # package/setup.py
    setup (
        # ...
        entry_points = {
            'settings_application1': [
                'default = path.to.application1.default_settings:generate_config',
                'local = path.to.application1.local_settings:generate_config',
            ],
            'settings_application2': [
                'default = path.to.application2.default_settings:generate_config',
                'local = path.to.application2.local_settings:generate_config',
            ]
        }
        # ...
    )

Create settings
---------------

To create settings, we need an instance of the :code:`Config` class.
In the following example, we are using the function named :code:`generate_config`,
which we specified as an entry point when we defined the groups and environments.
The :code:`generate_config` function, in our case, returns an instance of the
:code:`Config` class. Settings can be created either directly,
read them from a python file, or from an object.

.. code-block:: python

    # package/application1/default_settings.py
    from settei.config import Config

    def generate_config():
        config = Config()

        # create settings directly
        config['QUESTION'] = 'The Ultimate Question of Life, the Universe, and Everything'
        config['ANSWER'] = 41

        # or load them from a file
        config.from_pyfile('full/path/to/file.py')

        # or from an object
        config.from_object('path.to.object')

        return config

Read settings
-------------

In order to use the settings of our package, we need to first install it using
:code:`python setup.py install` and make sure that it is in our path. We can then
read and use settings in the rest of our package
by using the :code:`get_config` function. Note that in :code:`get_config`
function we specify the application name and not the group name.

For example, if we want to load settings for the application :code:`application1`
and we have defined a group of environments with the name :code:`settings_application1`,
then in the :code:`get_config` function we just use the name of the application,
which in this case is :code:`application1`.

.. code-block:: python

    from settei import get_config

    # get config settings for 'applicaion1' application and 'local' environment
    config = get_config('application1', 'local')

    # get config settings for 'application2' application and 'local' environment
    config = get_config('application2', 'local')

    # now you can use it as you want
    DEBUG = config['QUESTION']

Another way to define the desired environment is using the :code:`CONFIG_ENVIRONMENT`
variable.

.. code-block:: bash

    # run in this way
    $ env CONFIG_ENVIRONMENT='dev' python my_incredible_script.py

Then, in ``my_incredible_script.py`` when the :code:`get_config` function is
used, we do not need to specify an environment as it will use the :code:`dev`
environment that is defined by :code:`CONFIG_ENVIRONMENT`.

.. code-block:: python

    # in my_incredible_script.py we can use get_config
    from settei import get_config

    # get config settings for 'application1' application and 'dev' environment,
    # which has been specified when running my_incredible_script.py
    config = get_config('application1')

Settings inheritance
--------------------

Settings can also inherit other settings. However, this is only possible
for settings that belong to the same group of environments. For instance, if
you want your :code:`local` settings to inherit the :code:`default` settings,
then in the :code:`generate_config` function you should mention the name of
environment from which you want to inherit.

.. code-block:: python

    # in your application1/local_settings.py file
    # 'default' is the environment from which we want to inherit settings
    def generate_config(default):

        # change a setting, the right answer is 42
        default['ANSWER'] = 42

        return default

If we read the :code:`local` settings, then we will see that
:code:`config['ANSWER']` setting returns the value defined in
:code:`local_settings.py`, as we would expect.

.. code-block:: bash

    >> from settei import get_config
    >> config = get_config('application1', 'local')
    >> print config['QUESTION']
    The Ultimate Question of Life, the Universe, and Everything
    >> print config['ANSWER']
    42

Inheriting other settings does not stop us from introducing additional ones.
Attention should be paid though as new settings could be overwritten by any
inherited ones with the same name.

.. code-block:: python

    # in your package/application1/local_settings.py file
    from settei.config import Config

    def generate_config(default):
        local = Config()

        # change a setting, the right answer is 42
        default['ANSWER'] = 42

        # introduce an additional setting
        local['NEW'] = 'A new setting'

        # this will be overwritten with the 'ANSWER' from the 'default' environment
        local['ANSWER'] = 43

        # update the 'local' settings with the 'default' settings
        local.update(default)

        # local['ANSWER'] will be 42 here again

        return local

Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/paylogic/settei>`_.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `<LICENSE.txt>`_

© 2013 Paylogic International.
