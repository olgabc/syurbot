import configparser
import os


class Config:
    values = None

    @staticmethod
    def build():
        Config.values = configparser.ConfigParser()
        Config.values.read("./config/local.cfg")

    @staticmethod
    def get(path):
        if Config.values is None:
            Config.build()

        section, name = path.split(".")

        try:
            if section:
                return Config.values[section][name]

        except KeyError:
            return os.environ.get("%s.%s" % (section, name), None)
