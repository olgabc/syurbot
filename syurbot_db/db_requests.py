from syurbot_db.db_models.tag import TagModel
from syurbot_db.db_models.tagset import TagsetModel
from syurbot_db.db_models.tagset_has_tag import TagsetHasTagModel
from syurbot_db.db_session import SESSION
from sqlalchemy import and_


tag_query = SESSION.query(TagModel)
tagset_query = SESSION.query(TagsetModel)
tag_dict = {row.tag: row.id for row in tag_query}
tag_names_dict = {row.id: row.tag for row in tag_query}


def get_tags_ids(tags_list, format_type=None):
    assert isinstance(tags_list, list), "tags_list must be list"

    if not format_type:
        return set([tag_dict[tag_name] for tag_name in tags_list])

    if format_type == "str":
        return set([str(tag_dict[tag_name]) for tag_name in tags_list])

    if format_type == "int":
        return set([int(tag_dict[tag_name]) for tag_name in tags_list])


def get_tagset_tags_ids(tagset_id):
    tagset_tags_query = SESSION.query(TagsetHasTagModel).filter(TagsetHasTagModel.tagset_id == tagset_id)
    return set([tag_id.tag_id for tag_id in tagset_tags_query])


def get_tagset_tags_names(tagset_id):
    tagset_ids = get_tagset_tags_ids(tagset_id)
    return [tag_names_dict[tag_id] for tag_id in tagset_ids]

