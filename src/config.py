
"""This module contains the config info
    The class in this modules stores all of the various
    configuration information. The class itself does not
    contain any methods it only contains constants that is
    referred by other modules
"""
import os


class BaseConfig(object):
    """Class that contains the base config"""
    APP_NAME = "app"
    ENV = os.getenv('ENV', 'dev')