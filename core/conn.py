import configparser

config = configparser.ConfigParser()
config.read('./core/db.ini')
POSTGRESQL_URI = config["DATABASE"]["db"]
SECRET = config["DATABASE"]["secret"]
ALGO = config["DATABASE"]["algo"]