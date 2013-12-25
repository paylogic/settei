"""Test getting entry points."""
import os

import pkg_resources
import pytest

import settei
from settei import config

# used for checking loading setting by from_envvar and from_pyfile
TEST_KEY = 'foo'


class SettingsHandler(object):
    """SettingsHandler is object which used for getting settings from object."""
    DEBUG = True
    ANSWER = 43


def default():
    """Function which is used by entry points for getting settings for default environment."""
    settings = config.Config()
    settings.update({'QUESTION': 'The Ultimate Question of Life, the Universe, and Everything'})
    return settings


def dev(default):
    """Function which is used by entry points for getting settings for dev environment.

    :param default: it is dependency which will be calculated in moment of getting settings from this env.
    """
    default['ANSWER'] = 42
    return default


def wrong_config_object():
    """Function which is used by entry points for getting wrong config object."""
    return {}


def settings_from_object(default):
    """Function which is used by entry points for getting settings from object.

    :param default: it is dependency which will be calculated in moment of getting settings from this env.
    """
    default.from_object(SettingsHandler)
    return default


def settings_from_object_with_path_to_object(default):
    """Function which is used by entry points for getting settings from object with path to object.

    :param default: it is dependency which will be calculated in moment of getting settings from this env.
    """
    default.from_object('tests.test_get_entry_points.SettingsHandler')
    return default


def settings_from_object_with_invalid_path_to_object(default):
    """Function which is used by entry points for getting settings from object with invalid path to object.
    When we will try to get this settings then ImportStringError exception should be raised.

    :param default: it is dependency which will be calculated in moment of getting settings from this env.
    """
    default.from_object('tests.test_get_entry_points.SuperSettingsHandler')
    return default


def settings_from_envvar(default):
    """Function which is used by entry points for gettings settings from environment variable.

    :param default: it is dependency which will be calculated in moment of getting settings from this env.
    """
    os.environ['path_to_object'] = 'tests/test_get_entry_points.py'
    default.from_envvar('path_to_object')
    return default


def settings_from_invalid_path(default):
    """Function which is used by entry points for gettings settings from invalid path.
    When we will try to get this settings then IOError exception should be raised.

    :param default: it is dependency which will be calculated in moment of getting settings from this env.
    """
    os.environ['path_to_object'] = 'tests/test_entry_points.py'
    default.from_envvar('path_to_object')
    return default


def live(default, dev):
    """Function is used by entry points for getting settings for live environment."""


def get_entry_points(group, name=None):
    """Create list of entry points."""

    return [
        pkg_resources.EntryPoint.parse('default = tests.test_get_entry_points:default'),
        pkg_resources.EntryPoint.parse('dev = tests.test_get_entry_points:dev'),
        pkg_resources.EntryPoint.parse('live = tests.test_get_entry_points:live'),
        pkg_resources.EntryPoint.parse('settings_from_object = tests.test_get_entry_points:settings_from_object'),
        pkg_resources.EntryPoint.parse(
            'settings_from_object_with_path_to_object = '
            'tests.test_get_entry_points:settings_from_object_with_path_to_object'
        ),
        pkg_resources.EntryPoint.parse(
            'settings_from_object_with_invalid_path_to_object = '
            'tests.test_get_entry_points:settings_from_object_with_invalid_path_to_object'
        ),
        pkg_resources.EntryPoint.parse('settings_from_envvar = tests.test_get_entry_points:settings_from_envvar'),
        pkg_resources.EntryPoint.parse(
            'settings_from_invalid_path = tests.test_get_entry_points:settings_from_invalid_path'
        ),
        pkg_resources.EntryPoint.parse('wrong_config_object = tests.test_get_entry_points:wrong_config_object'),
    ]


def get_duplicate_entry_points(group, name=None):
    """Create list of entry points with duplicates."""
    return [pkg_resources.EntryPoint.parse('dev = tests.test_get_entry_points:dev'),
            pkg_resources.EntryPoint.parse('dev = tests.test_get_entry_points:dev')]


def require(self, env, installer):
    """Monkeypatched function of EntryPoint class."""
    pass


@pytest.fixture
def config_environment():
    """Set CONFIG_ENVIRONMENT for tests."""
    os.environ['CONFIG_ENVIRONMENT'] = 'dev'


@pytest.fixture
def clean_config():
    """Cleaning config for tests."""
    settei.config_storage.clear()


@pytest.fixture
def monkeypatch_entrypoint(monkeypatch, clean_config):
    """Mokeypatching EntryPoint."""
    monkeypatch.setattr(pkg_resources.EntryPoint, 'require', require)


@pytest.fixture
def monkeypatch_pkg_resources(monkeypatch, monkeypatch_entrypoint):
    """Monkeypatching pkg_resources.iter_entry_points with our list of entry points."""
    monkeypatch.setattr(pkg_resources, 'iter_entry_points', get_entry_points)


@pytest.fixture
def monkeypatch_pkg_resources_duplicate(monkeypatch, monkeypatch_entrypoint):
    """Monkeypatching pkg_resources.iter_entry_points with our list of duplicated entry points."""
    monkeypatch.setattr(pkg_resources, 'iter_entry_points', get_duplicate_entry_points)


def test_default_entry_point(monkeypatch_pkg_resources):
    """Check that we are getting config for default environment correctly."""
    default_config = settei.get_config('application', 'default')

    assert default_config == default()


def test_dev_entry_point(monkeypatch_pkg_resources):
    """Check that we are getting config for dev environment correctly."""
    dev_config = settei.get_config('application', 'dev')

    assert dev_config == dev(default())


def test_duplicate_entry_point_exception(monkeypatch_pkg_resources_duplicate):
    """Check that DuplicateEntryPoint is raising if list of entry points has several entry points with the same name."""
    with pytest.raises(settei.DuplicateEntryPoint):
        settei.get_config('application', 'default')


def test_environment_not_specified(monkeypatch_pkg_resources):
    """Check that EnvironmentNotSpecified is raising if we are trying to get config without specified environment."""
    with pytest.raises(settei.EnvironmentNotSpecified):
        settei.get_config('application')


def test_environment_is_missing(monkeypatch_pkg_resources):
    """Check that EnvironmentIsMissing is raising if we are trying to get config with missing environment."""
    with pytest.raises(settei.EnvironmentIsMissing):
        settei.get_config('application', 'missing_environment')


def test_more_than_one_dependency_injection_specified(monkeypatch_pkg_resources):
    """Check that it is impossible to have more that one dependency injection for entry point."""

    with pytest.raises(settei.MoreThanOneDependencyInjection):
        settei.get_config('application', 'live')


def test_wrong_config_type(monkeypatch_pkg_resources):
    """Check that WrongConfigTypeError is raising if we are trying to get wrong type of config object."""

    with pytest.raises(settei.WrongConfigTypeError):
        settei.get_config('application', 'wrong_config_object')


def test_loading_settings_from_object(monkeypatch_pkg_resources):
    """Check that settings were loaded from object."""
    config = settei.get_config('application', 'settings_from_object')

    assert config['ANSWER'] == SettingsHandler.ANSWER
    assert config['DEBUG'] == SettingsHandler.DEBUG


def test_loading_settings_from_object_with_path_to_object(monkeypatch_pkg_resources):
    """Check that settings were loaded from object with path to object."""

    config = settei.get_config('application', 'settings_from_object_with_path_to_object')

    assert config['ANSWER'] == SettingsHandler.ANSWER
    assert config['DEBUG'] == SettingsHandler.DEBUG


def test_loading_settings_from_object_with_invalid_path_to_object(monkeypatch_pkg_resources):
    """Check that ImportStringError will raise."""

    with pytest.raises(config.ImportStringError):
       settei.get_config('application', 'settings_from_object_with_invalid_path_to_object')


def test_loading_settings_from_envvar(monkeypatch_pkg_resources):
    """Check that settings were loaded from environment variable."""

    config = settei.get_config('application', 'settings_from_envvar')

    assert config['TEST_KEY'] == TEST_KEY


def test_loading_settings_from_envvar_invalid_path(monkeypatch_pkg_resources):
    """Check that ImportStringError will raise."""

    with pytest.raises(IOError):
        settei.get_config('application', 'settings_from_invalid_path')


def test_environment_from_envvar(monkeypatch_pkg_resources, config_environment):
    """Check that settings were loaded from environment variable."""

    config = settei.get_config('application')

    assert config == dev(default())

    del(os.environ['CONFIG_ENVIRONMENT'])
