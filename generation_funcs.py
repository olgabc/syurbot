from syurbot_db.db_models.tag import TagModel
from syurbot_db.db_models.tagset import TagSetModel
from syurbot_db.db_models.tagset_has_tag import TagSetHasTagModel
from syurbot_db.db_models.word import WordModel
from syurbot_db.db_session import SESSION
from syur_classes import MyWord
from syurbot_db.db_requests import get_tags_ids, get_tagsets_having_tags_ids, get_tags_names
from random import choice as random_choice
import re
import os
from sqlalchemy import and_

tag_query = SESSION.query(TagModel)
tagset_query = SESSION.query(TagSetModel)
tagsethastag_query = SESSION.query(TagSetHasTagModel)


def generate_word(required_tags, inflect_tags, frequency=0, word_source="freq_dict"):
    word_query = SESSION.query(WordModel)
    word_tags_ids = get_tags_ids(required_tags)
    tagsets_ids = get_tagsets_having_tags_ids(word_tags_ids)
    word_query = word_query.filter(
        and_(
            WordModel.tagset_id.in_(tagsets_ids),
            WordModel.word_source == word_source,
            WordModel.frequency >= frequency
        )
    )

    if not word_query:
        print("no fitting words")
        return

    word = random_choice([word.word for word in word_query])
    myword_instance = MyWord(word.word, tags=get_tags_names(word.tagset_id), is_normal_form=True)

    if not myword_instance.parse_chosen:
        return "check word"

    if inflect_tags:
        return myword_instance.parse_chosen.inflect(set(inflect_tags)).word
    else:
        return myword_instance.parse_chosen.word





"""


def check_sentence(sentence, to_print=False, for_base=True):

    if (
            not "NOUN" in [MyWord(p).pos for p in sentence_words] and
            not {"он", "она", "оно", "они"}.intersection(sentence_words)
    ):
        print_if(to_print, "has no NOUN or NPRO")
        return

    sentence_words = sentence.split(" ")
    check_results = {sw: "trash" for sw in sentence_words}

    for key in check_results.keys():
        check_results[key] = check_word(key, to_print=to_print)

    if not for_base:
        return check_results

    else:
        if "trash" in check_results.values():
            return "trash"

        else:
            return check_results
"""

def choose_sentences(name_without_extension, folder="books_splited", delete_na=True):
    sentences_frame = load_some_csv(name_without_extension, folder)
    sentences_frame["check"] = sentences_frame["sentence"].apply(
        lambda x: check_sentence_words(x, to_print=False)
    )

    if delete_na:
        sentences_frame = sentences_frame[sentences_frame["check"] == "trash"]
        sentences_frame.drop(["check"], axis=1, inplace=True)

    sentences_frame["words_qty"] = sentences_frame["sentence"].apply(
        lambda x: len(x.split(" "))
    )
    print(sentences_frame.head(20))
    write_some_csv(sentences_frame, name_without_extension, "filtered_sentences")


def generate_sentence(book=None, freq=None, to_print=True, words_qty=None, my_sentence=None):
    if my_sentence:
        has_sentence = True
    else:
        has_sentence = False

    if not book:
        book = "freq"

    if not my_sentence:
        if not book:
            books = [load_some_csv(file[:-4], "filtered_sentences") for file in os.listdir("filtered_sentences")]
            book_sentence = pd.concat(books)

        else:
            book_sentence = load_some_csv(book, "filtered_sentences")

        if words_qty:
            book_sentence = book_sentence[book_sentence["words_qty"] < words_qty]

        book_sentence = book_sentence.sample(n=1)
        book_sentence.index = [0]
        book_sentence = book_sentence.at[0, "sentence"]
        my_sentence = book_sentence

    end_symbol = "."

    if my_sentence[-1] in "!?.:":
        end_symbol = my_sentence[-1]
        my_sentence = my_sentence[:-1]

    sentence = re.sub(r'[^-A-яA-z\s\d]|(?<![A-яA-z](?=.[A-яA-z]))-', "", my_sentence)
    sentence_words = check_sentence_words(sentence, to_print=to_print, for_base=False)

    print("sw", sentence_words)

    for key in sentence_words.keys():

        if sentence_words[key] not in ['fixed', 'trash']:
            w = MyWord(key)
            word_for_replace = generate_word(
                pos=sentence_words[key],
                required_tags=w.get_required_tags(),
                inflect_tags=w.get_inflect_tags(),
                freq=freq,
                source=book
            )

            if word_for_replace == "trash":
                continue

            my_sentence = replace_word(
                key,
                word_for_replace,
                my_sentence
            )

    my_sentence += end_symbol

    if has_sentence:
        return my_sentence
    else:
        #return """
#old: {}
#new: {}
            #""".format(book_sentence, my_sentence)
"""