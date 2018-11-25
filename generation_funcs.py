from syurbot_db.tags_set import TagsSetModel
from syurbot_db.frequency import FrequencyModel
from syurbot_db.word import WordModel
from syurbot_db.db_session import SESSION
from syur_classes import MyWord
from libs.funcs import split_by_words, split_by_sentences
from random import choice as random_choice
import re
import os
#from sqlalchemy import in_


def generate_word(required_tags=None, inflect_tags=None, frequency=None, source="freq"):
    tags_set_nums = []
    tags_set_query = SESSION.query(TagsSetModel)

    for row in tags_set_query:
        if set(required_tags).intersection(row.tags_info.split(",")) == set(required_tags):
            tags_set_nums.append(row.id)

    word_query = SESSION.query(WordModel).\
        filter(WordModel.source==source).\
        filter(WordModel.tags_set_num.in_(tags_set_nums))

    if frequency:
        word_query = word_query.filter(WordModel.frequency >= frequency)

    if not word_query:
        print("no fitting words")
        return

    word = random_choice(word_query)

    myword_instance = MyWord(word.word, tags=word.tags_info.split(","), is_normal_form=True)
    inflected_word = myword_instance.parse_chosen.inflect(set(inflect_tags)).word

    if not myword_instance.parse_chosen:
        return "trash"

    if inflect_tags:
        return myword_instance.parse_chosen.inflect(set(inflect_tags)).word
    else:
        return myword_instance.parse_chosen.word








def check_sentence(sentence, to_print=False, for_base=True):
    """
    if (
            not "NOUN" in [MyWord(p).pos for p in sentence_words] and
            not {"он", "она", "оно", "они"}.intersection(sentence_words)
    ):
        print_if(to_print, "has no NOUN or NPRO")
        return
    """
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


def replace_with_case(word_f, word_r):
    if word_f.islower():
        return word_f.replace(word_f, word_r.lower())

    elif word_f.istitle():
        return word_f.replace(word_f, word_r.capitalize())

    elif word_f.isupper():
        return word_f.replace(word_f, word_r.upper())


def replace_word(word_f, word_r, sentence):
    word_r = replace_with_case(word_f, word_r)
    sentence = re.sub(
        r'(^|\b){}(\b|$)'.format(word_f),
        '{}'.format(replace_with_case(word_f, word_r)),
        sentence
    )
    return sentence


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
        return """
old: {}
new: {}
            """.format(book_sentence, my_sentence)
