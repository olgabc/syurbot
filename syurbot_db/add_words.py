from syur_classes import MyWord, MyWordParamsError
from syurbot_db.db_requests import get_tags_ids
from syurbot_db.hashing import row_to_hash, tagset_to_hash
from config.config import PSOS_TO_CHECK, PSOS_TO_FIND
from config.config import engine
from sqlalchemy import text


connection = engine.connect()
psos_dict = {psos[0]: psos[1] for psos in zip(PSOS_TO_CHECK, PSOS_TO_FIND)}

for tag in ["CONJ", "INTJ", "NUMR", "PREP", "PRED", "PRCL", "NPRO"]:
    psos_dict[tag] = tag


def get_lexeme_dict_rows(
        lexeme,
        tags=None,
        word_register=None,
        is_normal_form=False,
        source_id=None,
        frequency=None,
        score=None,
        purpose=None
):
    if purpose:
        MyWord.purpose = purpose

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
        return []

    if (MyWord.purpose != "add_db_freq_dict" and word_0.info == "fixed") or not word_0.parses:
        return []

    word_forms = set([(w.normal_form, w.tag.POS) for w in word_0.parses])
    frequency_0 = frequency / len(word_forms)

    if len(word_0.parses) == 1 and word_0.parse_chosen and word_0.parse_chosen.normal_form == word_0.word:
        word_instances_list.append((word_0, frequency_0))

    else:
        for word_form in word_forms:
            if MyWord.purpose != "add_db_freq_dict" and word_form[1] not in PSOS_TO_CHECK:
                continue
            try:
                word_1 = MyWord(
                    word=word_form[0],
                    tags=psos_dict[word_form[1]],
                    is_normal_form=True,
                    word_register=word_register
                )
            except MyWordParamsError:
                continue

            if not word_1.parses:
                continue

            frequency_1 = frequency_0 / len(word_forms)

            if len(word_1.parses) == 1 and word_1.parse_chosen:
                word_instances_list.append((word_1, frequency_1))

            else:
                for parse in word_1.parses:
                    parse_tag = str(parse.tag).replace(" ", ",").split(",") + word_1.custom_tags
                    word_2 = MyWord(
                        word=word_form[0],
                        tags=parse_tag,
                        is_normal_form=True,
                        word_register=word_register,
                        tagset_is_full=True
                    )
                    if not word_2.parses:
                        continue

                    frequency_2 = frequency_1 / len(word_1.parses)

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
        select_tagset_exists_text = text(
            """
            SELECT COUNT(1) FROM tagset
            WHERE hash = :tagset_hash
            """
        )
        tagset_exists = connection.execute(
            select_tagset_exists_text,
            tagset_hash=tagset_hash
        ).fetchone()[0]
        print("tagset_exists", tagset_exists)

        if tagset_exists:
            select_tagset_id_text = text(
                """
               SELECT id FROM tagset
               WHERE hash = :tagset_hash
               """
            )

            tagset_id = connection.execute(
                select_tagset_id_text,
                tagset_hash=tagset_hash
            ).fetchone()[0]

            dict_row["tagset_id"] = tagset_id
            word_hash = row_to_hash([
                dict_row["word"],
                str(dict_row["tagset_id"]),
                str(dict_row["source_id"])
            ])
            dict_row["hash"] = word_hash

        else:
            insert_into_tagset_text = text(
                """
                INSERT INTO tagset (hash) VALUES (:tagset_hash)
                """
            )
            connection.execute(
                insert_into_tagset_text,
                tagset_hash=tagset_hash
            )
            select_tagset_id_text = text(
                """
               SELECT id FROM tagset
               WHERE hash = :tagset_hash
               """
            )
            tagset_id = connection.execute(
                select_tagset_id_text,
                tagset_hash=tagset_hash
            ).fetchone()[0]

            tags_ids = get_tags_ids(tags)

            for tag_id in tags_ids:
                insert_into_tagset_has_tag_text = text(
                    """
                    INSERT INTO tagset_has_tag (tagset_id, tag_id) VALUES (:tagset_id, :tag_id)
                    """
                )

                connection.execute(
                    insert_into_tagset_has_tag_text,
                    tagset_id=tagset_id,
                    tag_id=tag_id
                )

            dict_row["tagset_id"] = tagset_id
            dict_row["hash"] = row_to_hash([
                dict_row["word"],
                str(dict_row["tagset_id"]),
                str(dict_row["source_id"])
            ])

        dict_rows.append(dict_row)
    return dict_rows


def write_words_rows(rows):
    for row in rows:
        insert_into_word_temp_text = text(
            """
            INSERT INTO word_temp (word, tagset_id, source_id, hash, frequency) 
            VALUES (:word, :tagset_id, :source_id, :hash, :frequency)
            """
        )

        connection.execute(
            insert_into_word_temp_text,
            word=row["word"],
            tagset_id=row["tagset_id"],
            source_id=row["source_id"],
            hash=row["hash"],
            frequency=row["frequency"]
        )


def group_word_temp_rows():
    grouped_word_temp = connection.execute(
        """
        SELECT word, tagset_id, source_id, hash, sum(frequency) as frequency
        FROM word_temp 
        GROUP BY hash
        ORDER BY word
        """
    )

    for row in grouped_word_temp:
        insert_into_word_text = text(
            """
            INSERT INTO word (word, tagset_id, source_id, hash, frequency) 
            VALUES (:word, :tagset_id, :source_id, :hash, :frequency)
            """
        )
        connection.execute(
            insert_into_word_text,
            word=row[0],
            tagset_id=row[1],
            source_id=row[2],
            hash=row[3],
            frequency=row[4]
        )

    connection.execute(
        """
        TRUNCATE TABLE word_temp
        """
    )
