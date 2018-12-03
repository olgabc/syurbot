from syurbot_db.db_models.tag import TagModel
from syurbot_db.db_models.tagset import TagSetModel
from syurbot_db.db_models.tagset_has_tag import TagSetHasTagModel
from syurbot_db.db_session import SESSION
from sqlalchemy import and_, func


tag_query = SESSION.query(TagModel)
tagset_query = SESSION.query(TagSetModel)
tag_dict = {row.tag: row.id for row in tag_query}
tag_names_dict = {row.id: row.tag for row in tag_query}
all_tagsets_ids = set([tagset.id for tagset in tagset_query])
max_tagset_id = int(SESSION.query(func.max(TagSetModel.id))[0][0] or 0)


def get_tags_ids(tags, format_type=None):
    if not format_type:
        return set([tag_dict[tag_name] for tag_name in tags])

    if format_type == "str":
        return set([str(tag_dict[tag_name]) for tag_name in tags])

    if format_type == "int":
        return set([int(tag_dict[tag_name]) for tag_name in tags])


def get_tagset_tags_ids(tagset_id):
    tagset_tags_query = SESSION.query(TagSetHasTagModel).filter(TagSetHasTagModel.tagset_id == tagset_id)
    return set([tag_id.tag_id for tag_id in tagset_tags_query])


def get_tags_names(tagset_id):
    tagset_ids = get_tagset_tags_ids(tagset_id)
    return [tag_names_dict[tag_id] for tag_id in tagset_ids]


def get_tagsets_having_tags_ids(tags_ids):
    tagsets_ids = all_tagsets_ids
    for tag in tags_ids:
        tagsets_have_tags_query = SESSION.query(TagSetHasTagModel).filter(
            and_(
                TagSetHasTagModel.tag_id == tag,
                TagSetHasTagModel.tagset_id.in_(tagsets_ids)
                 )
        )
        tagsets_ids = set([row.tagset_id for row in tagsets_have_tags_query])
    return [tagset.tagset_id for tagset in tagset_query]
