"""
Settei

Config system which bases on entry points of setuptools.
"""
import inspect
import os
import pkg_resources

from . import config


class WrongConfigTypeError(Exception):
    """Raises if list of entry points has duplicates."""
    message = "You should return instance of Config class from settei.config"

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.message


class DuplicateEntryPoint(Exception):
    """Raises if list of entry points has duplicates."""
    message = "You have several entry points with the same name."

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.message


class EnvironmentNotSpecified(Exception):
    """Raises if environment is not specified."""
    message = "You forget to specify environment."

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.message


class MoreThanOneDependencyInjection(Exception):
    """Raises if entry point has more than one dependency injection."""
    message = "You specified more than one dependency injection."

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.message


class ConfigGenerator(object):
    """ConfigGenerator is simple entry points reader. Its main feature get list of entry points for application
     then get entry point for environment, calculate all dependency injection and return result."""
    def __init__(self, application, environment):
        self.application = application
        self.environment = environment

        self.entry_points = {}

    def get_entry_points(self):
        """Fill in self.entry_points dict.

        :return: dictionary entry_points contains entry points for application.
        """
        for entry_point in pkg_resources.iter_entry_points('settings_{0}'.format(self.application)):
            if entry_point.name not in self.entry_points:
                self.entry_points[entry_point.name] = entry_point
            else:
                raise DuplicateEntryPoint()

        return self.entry_points

    def evaluate_dependency_injection(self, args):
        """Evaluate dependency injection of entry point.

        :param args: list of dependency injection which need to calculate

        :return: tuple of calculated dependency injection for entry point.
        """

        if len(args) > 1:
            raise MoreThanOneDependencyInjection()

        arguments = []
        for dependency in args:
            entry_point = self.entry_points[dependency]
            dependency_args = self.evaluate_dependency_injection(
                inspect.getargspec(entry_point.load()).args
            )
            arguments.append(self.invoke_entry_point(entry_point, *tuple(dependency_args)))

        return tuple(arguments)

    @staticmethod
    def invoke_entry_point(entry_point, *args):
        """Invoke given entry point."""
        config_instance = entry_point.load()(*args)
        if not isinstance(config_instance, config.Config):
            raise WrongConfigTypeError()
        return config_instance

    def get_config(self):
        """Get entry point for environment and return result.

        :return: result of calling entry point with pre calculated dependency injection.
        """
        try:
            entry_point = self.get_entry_points()[self.environment]
        except KeyError:
            raise EnvironmentNotSpecified()

        return self.invoke_entry_point(entry_point, *tuple(
            self.evaluate_dependency_injection(inspect.getargspec(entry_point.load()).args)
        ))


class ConfigStorage(dict):
    """Dict for memoization already calculated configs for applications and environments."""
    def __getitem__(self, *key):
        return dict.__getitem__(self, key)

    def __missing__(self, key):
        config = self[key] = ConfigGenerator(*key).get_config()
        return config

_config_storage = ConfigStorage()


def get_config(application, environment=None):
    """Get config for specific application and environment.

    :param application: group of entry points
    :param environment: name of entry point from which you want to get config

    :return: result of calling entry point"""
    if not environment:
        environment = os.environ.get('CONFIG_ENVIRONMENT')

    if not environment:
        raise EnvironmentNotSpecified()

    return _config_storage.__getitem__(application, environment)
