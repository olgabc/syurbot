from config.config import engine
from syurbot_db.db_requests import get_tags_ids, get_tagset_tags_names
from syurbot_db.hashing import tagset_to_hash
from syur_classes import MyWord, MyWordParamsError
from sqlalchemy import text
from libs.text_funcs import replace_word_with_case, split_by_words, replace_word_in_sentence, get_word_register
import random


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
        tagsets_ids = [tagset_id]

    else:
        required_tags_ids = get_tags_ids(required_tags)
        required_tags_qty = len(required_tags)

        if excluded_tags:
            excluded_tags_ids = get_tags_ids(excluded_tags)
            select_tagsets_ids_text = text(
                """
                SELECT tagset_id FROM tagset_has_tag 
                WHERE tag_id  IN :required_tags_ids
                AND tagset_id NOT IN (
                SELECT tagset_id FROM tagset_has_tag 
                WHERE tag_id IN :excluded_tags_ids
                )
                GROUP BY tagset_id
                HAVING COUNT(tagset_id) = :required_tags_qty
                """
            )
            select_tagsets_ids = connection.execute(
                select_tagsets_ids_text,
                required_tags_ids=required_tags_ids,
                excluded_tags_ids=excluded_tags_ids,
                required_tags_qty=required_tags_qty
            )

        else:
            select_tagsets_ids_text = text(
                    """
                    SELECT tagset_id FROM tagset_has_tag 
                    WHERE tag_id IN :required_tags_ids
                    GROUP BY tagset_id
                    HAVING COUNT(tagset_id) = :required_tags_qty
                    """
                )
            select_tagsets_ids = connection.execute(
                select_tagsets_ids_text,
                required_tags_ids=required_tags_ids,
                required_tags_qty=required_tags_qty
            )
        tagsets_ids = [row.tagset_id for row in select_tagsets_ids]

        if not tagsets_ids:
            raise TagsError(
                "No words having such tags: required: {}, excluded: ()".format(
                    required_tags,
                    excluded_tags
                )
            )

    select_words_ids_text = text(
        """
        SELECT id FROM word 
        WHERE tagset_id IN :tagsets_ids AND source_id = :source_id AND frequency >= :frequency
        """
    )
    select_words_ids = connection.execute(
        select_words_ids_text,
        tagsets_ids=tagsets_ids,
        source_id=source_id,
        frequency=frequency
    )
    ids = []
    for row in select_words_ids:
        ids.append(row.id)

    print("select_length", len(ids))

    if not ids or len(ids) < select_words_qty_min:
        print("not enough words in select")
        raise TagsError

    random_id = random.choice(ids)
    select_word_by_id_text = text(
        """
        SELECT * FROM word 
        WHERE id = :id     
        """
    )
    select_word_by_id = connection.execute(
        select_word_by_id_text,
        id=random_id
    ).fetchone()

    random_word = select_word_by_id.word
    random_tagset = select_word_by_id.tagset_id
    tagset_tags = get_tagset_tags_names(random_tagset)
    print(select_word_by_id, tagset_tags)
    myword_instance = MyWord(random_word, tags=tagset_tags, is_normal_form=True, word_register=register)
    print(myword_instance.parse_chosen)
    if not myword_instance.parse_chosen:
        return "check word"

    if inflect_tags:
        return myword_instance.parse_chosen.inflect(set(inflect_tags)).word
    else:
        return myword_instance.parse_chosen.word


def generate_similar_word(word_example, source_id, frequency=0, register=None):
    try:
        myword_instance = MyWord(word_example, word_register=register)
        print("word_example", word_example)

    except MyWordParamsError:
        print("MyWordParamsError:", word_example)
        return word_example

    if myword_instance.info in ["fixed", "trash"]:
        return word_example

    tags = myword_instance.db_tags
    print("tags", tags)

    inflect_tags = myword_instance.inflect_tags
    print("inflect_tags", inflect_tags)

    excluded_tags = []
    print("excluded_tags", excluded_tags)

    if register and get_word_register(word_example) == "lower":
        excluded_tags = ["Abbr", "Name", "Patr", "Surn", "Geox", "Orgn", "Trad"]

    tagset_hash = tagset_to_hash(tags)
    tagset_id = None

    try:
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

    except TypeError:
        print("TypeError", word_example, tags)

    try:
        word = generate_word(
            source_id=source_id,
            frequency=frequency,
            tagset_id=tagset_id,
            register=register,
            inflect_tags=inflect_tags
            )
    except (TagsError, AssertionError):
        print("TagsError: (tagset)", word_example)
        try:
            word = generate_word(
                source_id=source_id,
                frequency=frequency,
                required_tags=tags,
                excluded_tags=excluded_tags,
                register=register,
                inflect_tags=inflect_tags
            )
        except TagsError:
            print("TagsError: (db_tags)", word_example)
            tags = myword_instance.required_tags + [
                tag for tag in myword_instance.capitalized_tags if tag in [
                    "Abbr",
                    "Name",
                    "Patr",
                    "Surn",
                    "Geox",
                    "Orgn",
                    "Trad"
                ]
            ]
            try:
                word = generate_word(
                    source_id=source_id,
                    frequency=frequency,
                    required_tags=tags,
                    excluded_tags=excluded_tags,
                    register=register,
                    inflect_tags=inflect_tags
                )

            except TagsError:
                print("TagsError: (required_trags + title_tags)", word_example)
                tags = myword_instance.required_tags
                try:
                    word = generate_word(
                            source_id=source_id,
                            frequency=frequency,
                            required_tags=tags,
                            excluded_tags=excluded_tags,
                            register=register,
                            inflect_tags=inflect_tags
                        )
                except TagsError:
                    print("TagsError: (required_tags) - a very special word)", word_example)
                    word = word_example

                except AttributeError:
                    print(myword_instance.parse_chosen.word, inflect_tags)
                    word = word_example

            except AttributeError:
                print(myword_instance.parse_chosen.word, inflect_tags)
                word = word_example

        except AttributeError:
            print(myword_instance.parse_chosen.word, inflect_tags)
            word = word_example

    except AttributeError:
        print(myword_instance.parse_chosen.word, inflect_tags)
        word = word_example

    return replace_word_with_case(word_example, word)


def select_random_sentence(
        source_id,
        sentence_length_min=None,
        sentence_length_max=None,
        unchangable_words_qty_max=None,
        fixed_words_qty_max=None,
        trash_words_qty_max=None

):
    source_id_text = "SELECT * FROM sentence WHERE source_id = :source_id "
    sentence_length_min_text = ""
    sentence_length_max_text = ""
    unchangable_words_qty_max_text = ""
    fixed_words_qty_max_text = ""
    trash_words_qty_max_text = ""

    if sentence_length_min is not None:
        sentence_length_min_text = "AND sentence_length >= :sentence_length_min "

    if sentence_length_max is not None:
        sentence_length_max_text = "AND sentence_length <= :sentence_length_max "

    if unchangable_words_qty_max is not None:
        unchangable_words_qty_max_text = "AND trash_words_qty+fixed_words_qty <= :unchangable_words_qty_max "

    if fixed_words_qty_max is not None:
        fixed_words_qty_max_text = "AND fixed_words_qty <= :fixed_words_qty_max "

    if trash_words_qty_max is not None:
        trash_words_qty_max_text = "AND trash_words_qty <= :trash_words_qty_max "

    select_sentences_text = text(
            source_id_text +
            sentence_length_min_text +
            sentence_length_max_text +
            unchangable_words_qty_max_text +
            fixed_words_qty_max_text +
            trash_words_qty_max_text
        )

    sentence_rows = connection.execute(
        select_sentences_text,
        source_id=source_id,
        sentence_length_min=sentence_length_min,
        sentence_length_max=sentence_length_max,
        unchangable_words_qty_max=unchangable_words_qty_max,
        fixed_words_qty_max=fixed_words_qty_max,
        trash_words_qty_max=trash_words_qty_max
    ).fetchall()
    random_sentence = random.choice(sentence_rows).sentence
    print(random_sentence)
    print()

    return random_sentence


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
