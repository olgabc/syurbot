from config.config import engine
from syurbot_db.db_requests import get_tags_ids, get_tagset_tags_names
from syur_classes import MyWord


connection = engine.connect()


def generate_word(source_id, tagset_id=None, required_tags=None, excluded_tags=None, inflect_tags=None, frequency=0):
    if tagset_id:
        tagsets_ids = {tagset_id}

    else:
        required_tags_ids = get_tags_ids(required_tags)
        tagsets_having_tags = []
        for tag_id in required_tags_ids:
            tagsets_having_tag = connection.execute(
                """
                SELECT DISTINCT(tagset_id) tagset_id FROM tagset_has_tag 
                WHERE tag_id = {}
                """.format(tag_id)
            )
            tagsets_having_tag = {tagsets_id.tagset_id for tagsets_id in tagsets_having_tag}
            tagsets_having_tags.append(tagsets_having_tag)

        tagsets_ids = set.intersection(*tagsets_having_tags)

        if excluded_tags:
            excluded_tagsets_having_tags = []
            excluded_tags_ids = get_tags_ids(excluded_tags)
            for tag_id in excluded_tags_ids:
                excluded_tagsets_having_tag = connection.execute(
                    """
                    SELECT DISTINCT(tagset_id) tagset_id FROM tagset_has_tag 
                    WHERE tag_id = {}
                    """.format(tag_id)
                )
                excluded_tagsets_having_tag = [tagsets_id.tagset_id for tagsets_id in excluded_tagsets_having_tag]
                excluded_tagsets_having_tags += excluded_tagsets_having_tag

            excluded_tagsets_ids = set(excluded_tagsets_having_tags)
            tagsets_ids = tagsets_ids - excluded_tagsets_ids

        if not tagsets_ids:
            raise ValueError("No words having such tags")

    tagsets_ids = {str(tagset_id) for tagset_id in tagsets_ids}
    random_row = connection.execute(
        """
        SELECT * FROM word 
        WHERE tagset_id in ({}) AND source_id = {} AND frequency >= {}     
        ORDER BY RAND()
        LIMIT 1
        """.format(
            ", ".join(tagsets_ids),
            source_id,
            frequency
        )
    ).fetchone()

    random_word = random_row.word
    random_tagset = random_row.tagset_id
    tagset_tags = get_tagset_tags_names(random_tagset)

    myword_instance = MyWord(random_word, tags=tagset_tags, is_normal_form=True)

    if not myword_instance.parse_chosen:

        return "check word"

    if inflect_tags:
        return myword_instance.parse_chosen.inflect(set(inflect_tags)).word
    else:
        return myword_instance.parse_chosen.word


word = generate_word(
    source_id=1,
    tagset_id=0,
    required_tags=["NOUN"],
    excluded_tags=["femn", "anim"],
    inflect_tags=["plur", "ablt"]
)
print(word)


def generate_similar_word(word_example):
    try:
        myword_instance = MyWord(word_example)
        word = myword_instance.parse_chosen.normal_form
        required_tags = myword_instance.required_tags
        


    except:
        return word

"""def check_sentence(sentence, to_print=False, for_base=True):


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
        #return
"""
#old: {}
#new: {}
            #.format(book_sentence, my_sentence)
