#!/usr/bin/python
# -*- coding: utf-8 -*-

from syurbot_db.db_models.tagset import TagsetModel
from syurbot_db.db_models.tagset_has_tag import TagsetHasTagModel
from syurbot_db.db_models.frequency import FrequencyModel
from syurbot_db.db_models.word import WordModel
from syurbot_db.db_models.word_temp import WordTempModel
from syurbot_db.db_session import SESSION
from syur_classes import MyWord, MyWordParamsError
from syurbot_db.db_requests import get_tags_ids, get_tagset_tags_ids
from syurbot_db.hashing import row_to_hash, tagset_to_hash
from config.config import PSOS_TO_CHECK, PSOS_TO_FIND

psos_dict = {psos[0]: psos[1] for psos in zip(PSOS_TO_CHECK, PSOS_TO_FIND)}
MyWord.purpose = "add_db_source"


def get_lexeme_dict_rows(
        lexeme,
        tags=None,
        word_register=None,
        is_normal_form=False,
        source_id=None,
        frequency=None,
        score=None
):
    print("get_lexeme_dict_rows:", lexeme)
    word_instances_list = []

    try:
        word_0 = MyWord(
            lexeme,
            tags=tags,
            is_normal_form=is_normal_form,
            word_register=word_register,
            score=score,
        )
    except MyWordParamsError:
        return

    if word_0.info in ["fixed", "unchangable"] or not word_0.parses:
        return

    word_forms = set([(w.normal_form, w.tag.POS) for w in word_0.parses])
    frequency_0 = frequency / len(word_forms)

    if len(word_0.parses) == 1 and word_0.parse_chosen and word_0.parse_chosen.normal_form == word_0.word:
        word_instances_list.append((word_0, frequency_0))
    
    else:
        for word_form in word_forms:
            if word_form[1] not in PSOS_TO_CHECK:
                continue
            word_1 = MyWord(
                word=word_form[0],
                tags=psos_dict[word_form[1]],
                is_normal_form=True,
                word_register=word_register
            )

            if not word_1.parses:
                continue

            frequency_1 = frequency_0 / len(word_forms)

            if len(word_1.parses) == 1 and word_1.parse_chosen:
                word_instances_list.append((word_1, frequency_1))

            else:
                for parse in word_1.parses:
                    parse_tag = str(parse.tag).replace(" ", ",").split(",") + word_1.custom_tags
                    print("parse_tag", parse_tag)
                    word_2 = MyWord(
                        word=word_form[0],
                        tags=parse_tag,
                        is_normal_form=True,
                        word_register=word_register,
                        tagset_is_full=True
                    )
                    print("word_parse", word_2.parses)
                    if not word_2.parses:
                        continue

                    frequency_2 = frequency_1 / len(word_2.parses)
    
                    if word_2.parse_chosen:
                        word_instances_list.append((word_2, frequency_2))

    dict_rows = []

    for word_instance in word_instances_list:
        dict_row = ({
            "word": word_instance[0].word,
            "tagset_id": None,
            "source_id": source_id,
            "frequency": word_instance[1]
        })

        tags = word_instance[0].db_tags
        tagset_hash = tagset_to_hash(tags)
        tagset_hash_query_count = SESSION.query(TagsetModel).filter(TagsetModel.hash == tagset_hash).count()

        if not tagset_hash_query_count:
            SESSION.add(TagsetModel(hash=tagset_hash))
            SESSION.commit()
            tagset_id = SESSION.query(TagsetModel.id).filter(TagsetModel.hash == tagset_hash)[0][0]
            tags_ids = get_tags_ids(tags, format_type="int")

            for tag_id in tags_ids:
                SESSION.add(TagsetHasTagModel(tagset_id=tagset_id, tag_id=tag_id))
                SESSION.commit()

            dict_row["tagset_id"] = tagset_id
            dict_row["hash"] = row_to_hash([
                dict_row["word"],
                str(dict_row["tagset_id"]),
                str(dict_row["source_id"])
            ])

        else:
            tagset_id = SESSION.query(TagsetModel.id).filter(TagsetModel.hash == tagset_hash)[0][0]
            dict_row["tagset_id"] = tagset_id
            word_hash = row_to_hash([
                dict_row["word"],
                str(dict_row["tagset_id"]),
                str(dict_row["source_id"])
            ])
            dict_row["hash"] = word_hash
        dict_rows.append(dict_row)

        print(dict_row)

        SESSION.add(WordTempModel(
            word=dict_row["word"],
            tagset_id=dict_row["tagset_id"],
            source_id=dict_row["source_id"],
            hash=dict_row["hash"],
            frequency=dict_row["frequency"],
        ))
        SESSION.commit()

    return dict_rows


def add_freq_dict():
    freq_dict_query = SESSION.query(FrequencyModel)
    words_dict_query = SESSION.query(WordModel)
    old_freq_dict = words_dict_query.filter(WordModel.source_id == 1)
    old_freq_dict.delete(synchronize_session=False)

    for row in freq_dict_query:
        print(row)
        get_lexeme_dict_rows(
            lexeme=row.lexeme,
            tags=set(row.tags.split(",")),
            word_register="get_register",
            is_normal_form=True,
            source_id=1,
            frequency=row.frequency
        )


add_freq_dict()
