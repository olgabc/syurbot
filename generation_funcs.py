from config.config import engine
from syurbot_db.db_requests import get_tags_ids, get_tagset_tags_names
from syurbot_db.hashing import tagset_to_hash
from syur_classes import MyWord, MyWordParamsError
from sqlalchemy.exc import ProgrammingError
from libs.text_funcs import replace_word_with_case, split_by_words, replace_word_in_sentence, get_word_register
import random


#TODO passed_tags_settings, select_tagset_id_length
connection = engine.connect()


class TagsError (Exception):
    pass


def generate_word(
        source_id,
        tagset_id=None,
        required_tags=None,
        excluded_tags=None,
        inflect_tags=None,
        frequency=0,
        register=None,
        select_words_qty_min=10
):
    if tagset_id:
        tagsets_ids = {tagset_id}

    else:
        required_tags_ids = tuple(get_tags_ids(required_tags))
        required_tags_qty = len(required_tags)

        if excluded_tags:
            excluded_tags_ids = tuple(get_tags_ids(excluded_tags))
            tagsets_ids = connection.execute(
                """
                SELECT tagset_id FROM tagset_has_tag 
                WHERE tag_id in {}
                AND tagset_id NOT IN (
                SELECT tagset_id FROM tagset_has_tag 
                WHERE tag_id in {}
                )
                GROUP BY tagset_id
                HAVING COUNT(*) = {}
                """.format(
                    required_tags_ids,
                    excluded_tags_ids,
                    required_tags_qty
                )
            )
        else:
            tagsets_ids = connection.execute(
                    """
                    SELECT tagset_id FROM tagset_has_tag 
                    WHERE tag_id in {}
                    GROUP BY tagset_id
                    HAVING COUNT(tag_id) = {}
                    """.format(
                        required_tags_ids,
                        required_tags_qty
                    )
                )
        tagsets_ids = [row.tagset_id for row in tagsets_ids]

        if not tagsets_ids:
            raise TagsError(
                "No words having such tags: required: {}, excluded: ()".format(
                    required_tags,
                    excluded_tags
                )
            )

    tagsets_ids = {str(tagset_id) for tagset_id in tagsets_ids}
    select_words_ids = connection.execute(
        """
        SELECT id FROM word 
        WHERE tagset_id in ({}) AND source_id = {} AND frequency >= {}     
        """.format(
            ", ".join(tagsets_ids),
            source_id,
            frequency
        )
    )
    ids = []
    for row in select_words_ids:
        ids.append(row.id)

    print(len(ids), ids)

    if not ids or len(ids) < select_words_qty_min:
        raise TagsError("not enough words in select")

    random_id = random.sample(ids, 1)[0]
    random_row = connection.execute(
        """
        SELECT * FROM word 
        WHERE id = {}     
        """.format(random_id)
    ).fetchone()
    random_word = random_row.word
    random_tagset = random_row.tagset_id
    tagset_tags = get_tagset_tags_names(random_tagset)
    print(random_row, tagset_tags)
    myword_instance = MyWord(random_word, tags=tagset_tags, is_normal_form=True, word_register=register)
    print(myword_instance.parse_chosen)
    if not myword_instance.parse_chosen:
        return "check word"

    if inflect_tags:
        print(inflect_tags)
        print("myword_instance.parse_chosen", myword_instance.parse_chosen)
        return myword_instance.parse_chosen.inflect(set(inflect_tags)).word
    else:
        return myword_instance.parse_chosen.word


def generate_similar_word(word_example, source_id, frequency=0, register=None):
    try:
        myword_instance = MyWord(word_example, word_register=register)
        print("word_example", word_example)
        tags = myword_instance.db_tags
        print("tags", tags)
        inflect_tags = myword_instance.inflect_tags
        print("inflect_tags", inflect_tags)
        excluded_tags = []
        print("excluded_tags", excluded_tags)

        if register and get_word_register(word_example) == "lower":
            excluded_tags = ["Abbr", "Name", "Patr", "Surn", "Geox", "Orgn", "Trad"]

        tagset_hash = tagset_to_hash(tags)
        tagset_id_select = connection.execute(
                """
                SELECT id FROM tagset
                WHERE hash = '{}'
                """.format(tagset_hash)
            ).fetchone()

        if tagset_id_select:
            tagset_id = tagset_id_select[0]
            word = generate_word(
                source_id=source_id,
                frequency=frequency,
                tagset_id=tagset_id,
                register=register,
                inflect_tags=inflect_tags
                )

        else:
            word = generate_word(
                source_id=source_id,
                frequency=frequency,
                required_tags=tags,
                excluded_tags=excluded_tags,
                register=register,
                inflect_tags=inflect_tags
            )
            print("ok:", word_example)
        return replace_word_with_case(word_example, word)

    except MyWordParamsError:
        print("MyWordsError:", word_example)
        return word_example
    except TagsError:
        print("TagsError:", word_example)
        return word_example
    except ProgrammingError:
        print("ProgrammingError:", word_example)
        return word_example


def select_random_sentence(
        source_id,
        sentence_length_min=None,
        sentence_length_max=None,
        unchangable_words_qty_max=None,
        fixed_words_qty_max=None,
        trash_words_qty_max=None

):
    sentence_length_min_select_row = ""
    sentence_length_max_select_row = ""
    unchangable_words_qty_select_row = ""
    fixed_words_qty_select_row = ""
    trash_words_qty_select_row = ""

    if sentence_length_min is not None:
        sentence_length_min_select_row = "AND sentence_length >= {}".format(sentence_length_min)

    if sentence_length_max is not None:
        sentence_length_max_select_row = "AND sentence_length <= {}".format(sentence_length_max)

    if unchangable_words_qty_max is not None:
        unchangable_words_qty_select_row = "AND trash_words_qty+fixed_words_qty <= {}".format(unchangable_words_qty_max)

    if fixed_words_qty_max is not None:
        fixed_words_qty_select_row = "AND fixed_words_qty <= {}".format(fixed_words_qty_max)

    if trash_words_qty_max is not None:
        trash_words_qty_select_row = "AND trash_words_qty <= {}".format(trash_words_qty_max)

    sentence_row = connection.execute(
        """
        SELECT * FROM sentence
        WHERE source_id = {} 
        {}
        {}
        {}
        {}
        {}
        ORDER BY RAND()
        LIMIT 1
        """.format(
            source_id,
            sentence_length_min_select_row,
            sentence_length_max_select_row,
            unchangable_words_qty_select_row,
            fixed_words_qty_select_row,
            trash_words_qty_select_row
        )
    ).fetchone()

    print(sentence_row)

    return sentence_row.sentence


def generate_sentence(
        my_sentence="",
        word_source_id=None,
        sentence_source_id=None,
        sentence_length_min=None,
        sentence_length_max=None,
        unchangable_words_qty_max=None,
        fixed_words_qty_max=None,
        trash_words_qty_max=None,
        print_old_sentence=False
):
    if my_sentence:
        sentence = my_sentence
        if sentence[-1] == "?":
            sentence = sentence[:-1] + "."

    else:
        sentence = select_random_sentence(
            source_id=sentence_source_id,
            sentence_length_min=sentence_length_min,
            sentence_length_max=sentence_length_max,
            unchangable_words_qty_max=unchangable_words_qty_max,
            fixed_words_qty_max=fixed_words_qty_max,
            trash_words_qty_max=trash_words_qty_max
        )

    sentence_words = split_by_words(sentence)
    sentence_words_with_registers = [{"word": word, "register": "get_register"} for word in sentence_words]
    sentence_words_with_registers[0]["register"] = None

    new_sentence = sentence

    for word in sentence_words_with_registers:
        new_word = generate_similar_word(
            word_example=word["word"],
            source_id=word_source_id,
            frequency=0,
            register=word["register"]
        )
        new_sentence = replace_word_in_sentence(word["word"], new_word, new_sentence)

    if print_old_sentence:

        return """
        old_sentence: {}
        new_sentence: {}
        """.format(sentence, new_sentence)

    return new_sentence
