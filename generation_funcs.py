from syur_classes import *
import re
import os


def generate_word(required_tags=None, inflect_tags=None, freq=None, source="freq"):
    if pos in ["VERB", "PRTS", "PRTF", "GRND"]:
        pos = "INFN"

    elif pos in ["ADJS", "COMP"]:
        pos = "ADJF"

    words = load_some_csv("{}_{}".format(source, pos), "bases")

    if source == "freq":
        words.drop(["R", "D", "Doc"], axis=1, inplace=True)

    if freq:
        words = words[words.Freq > freq]

    if required_tags:
        words["has_required_tags"] = words["tags"].apply(
            lambda x: set(required_tags).intersection(x.split(",")) == set(required_tags)
        )
        words = words[words.has_required_tags == True]
        if words.empty:
            print("no fitting words")
            return

    word = words.sample(n=1)
    word.index = [0]
    word = word.at[0, "Lemma"]

    w = MyWord(word, pos)

    if not w.pymorphy_parse_object:
        return "trash"

    if inflect_tags:
        return w.pymorphy_parse_object.inflect(set(inflect_tags)).word
    else:
        return w.pymorphy_parse_object.word








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
