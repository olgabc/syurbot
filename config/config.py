from utils.coll import Config
from sqlalchemy import create_engine

DB_HOST = Config.get('DB.host')
DB_PASSWORD = Config.get('DB.password')

local_engine = create_engine(
    'mysql+pymysql://root:{}@{}/syurbot_db'.format(DB_PASSWORD, DB_HOST),
    #echo=True
)

DB_REMOTE_HOST = Config.get('DB_REMOTE.remote_host')
DB_REMOTE_USER = Config.get('DB_REMOTE.remote_user')
DB_REMOTE_PASSWORD = Config.get('DB_REMOTE.remote_password')

remote_engine = create_engine(
    'mysql+pymysql://{}:{}@{}/syurbot_db'.format(
        DB_REMOTE_USER,
        DB_REMOTE_PASSWORD,
        DB_REMOTE_HOST
    ),
    echo=True
)

engine_type = "remote"

if engine_type == "remote":
    engine = remote_engine

else:
    engine = local_engine

PSOS_TO_CHECK = ["NOUN", "INFN", "VERB", "PRTS", "PRTF", "GRND", "ADJF", "ADJS", "COMP", "ADVB"]
PSOS_TO_FIND = ["NOUN", "INFN", "INFN", "INFN", "INFN", "INFN", "ADJF", "ADJF", "ADJF", "ADVB"]
UNCHANGABLE_WORDS = [
    "быть",
    "стать",
    "самый",
    "который",
    "привет",
    "почему",
    "зачем",
    "потому"
]
