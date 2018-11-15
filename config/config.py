from utils.coll import Config
from sqlalchemy import create_engine

DB_PASSWORD = Config.get('DB.password')
DB_HOST = Config.get('DB.host')
engine = create_engine(
    'mysql+pymysql://root:{}@{}/syurbotdb'.format(DB_PASSWORD, DB_HOST),
    echo=True
)

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
