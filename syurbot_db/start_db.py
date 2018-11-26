from syur_classes import MyWord
from config.config import engine
from syurbot_db.tag import TagModel
from syurbot_db.tagset import TagSetModel
from syurbot_db.tagset_has_tag import TagSetHasTagModel
from syurbot_db.db_session import SESSION

opencorp_tags = open("opencorp_tags.txt").readlines()
tags = opencorp_tags + MyWord.custom_tags
#TagModel.__table__.drop(engine)
#TagModel.__table__.create(engine)

for tag in tags:
    SESSION.add(TagModel(tag=tag))

SESSION.commit()

#TagSetModel.__table__.drop(engine)
TagSetModel.__table__.create(engine)
SESSION.commit()

#TagSetHasTagModel.__table__.drop(engine)
#TagSetHasTagModel.__table__.create(engine)
SESSION.commit()