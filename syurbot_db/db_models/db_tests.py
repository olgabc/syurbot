from syurbot_db.db_session import SESSION
from syurbot_db.db_models.tagset import TagsetModel
from syurbot_db.db_models.tag import TagModel
from syurbot_db.db_models.tagset_has_tag import TagsetHasTagModel
from syurbot_db.db_models.frequency import FrequencyModel
from syurbot_db.db_models.word import WordModel
from sqlalchemy import func
from config.config import engine

"""
tagset_query = SESSION.query(TagsetModel)
max_tagset_id = SESSION.query(func.max(TagsetModel.id))


tag_query = SESSION.query(TagModel)
tagset_query = SESSION.query(TagsetModel)
tag_dict = {row.tag: row.id for row in tag_query}
tag_names_dict = {row.id: row.tag for row in tag_query}
all_tagsets_ids = set([tagset.id for tagset in tagset_query])
"""

TagModel.__table__.create(engine)
TagsetModel.__table__.create(engine)
TagsetHasTagModel.__table__.create(engine)
WordModel.__table__.create(engine)
