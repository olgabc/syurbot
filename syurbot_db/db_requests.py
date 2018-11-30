from syurbot_db.db_models.tag import TagModel
from syurbot_db.db_models.tagset import TagSetModel
from syurbot_db.db_models.tagset_has_tag import TagSetHasTagModel
from syurbot_db.db_models.word import WordModel
from syurbot_db.db_session import SESSION
from sqlalchemy import and_


def get_tags_ids(tags, format=None):
    tag_query = SESSION.query(TagModel)
    tag_dict = {row.tag.strip(): row.id for row in tag_query}

    if not format:
        return set([tag_dict[tag_name] for tag_name in tags])

    if format == "str":
        return set([str(tag_dict[tag_name]) for tag_name in tags])

    if format == "int":
        return set([int(tag_dict[tag_name]) for tag_name in tags])


def get_tagset_tags_ids(tagset_id):
    tagset_tags_query = SESSION.query(TagSetHasTagModel).filter(TagSetHasTagModel.tagset_id == tagset_id)
    return [tag_id.tag_id for tag_id in tagset_tags_query]


def get_tagsets_having_tags_ids(tags_ids):
    tagsets_query = SESSION.query(TagSetModel)
    tagsets_ids = set([tagset.id for tagset in tagsets_query])

    for tag in tags_ids:
        print(tag)
        tagsets_query = SESSION.query(TagSetHasTagModel).filter(
            and_(
                TagSetHasTagModel.tag_id == tag,
                TagSetHasTagModel.tagset_id.in_(tagsets_ids)
                 )
        )
        tagsets_ids = [tagset.tagset_id for tagset in tagsets_query]
    return [tagset.tagset_id for tagset in tagsets_query]


def get_tags_names(tagset_id):
    tag_query = SESSION.query(TagModel)
    tagset_ids = get_tagset_tags_ids(tagset_id)
    tag_dict = {row.id: row.tag.strip() for row in tag_query}
    return [tag_dict[tag_id] for tag_id in tagset_ids]


