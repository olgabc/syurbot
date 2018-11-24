from config.config import engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
SESSION = Session()


