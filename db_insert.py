import re
from syurbot_db.frequency import FrequencyModel
from syurbot_db.word import WordModel
# from syurbot_db.sentence import SentenceModel
from syurbot_db.db_session import SESSION
from syur_classes import MyWord
from libs.funcs import split_by_words, split_by_sentences


def add_freq_dict():
    freq_dict_query = SESSION.query(FrequencyModel)
    words_dict_query = SESSION.query(WordModel)
    old_freq_dict = words_dict_query.filter(WordModel.word_json.like('%"source": "freq_dict"%'))
    old_freq_dict.delete(synchronize_session=False)
    dict_rows = []

    for row in freq_dict_query:

        word = MyWord(
            word=row.lemma,
            tags=row.pos,
            is_normal_form=True,
            word_register="get_register"
        )
        print("word:", word.word)

        if word.parses:
            frequency = (row.frequency or 1) / len(set([(w.normal_form, w.tag.POS) for w in word.parses]))

            if "multianim" in word.all_tags:
                frequency = frequency / 2

        if row.pos == "NOUN" and word.parses and len(word.parses) > 1:

            for parse in word.parses:
                tag = str(parse.tag).replace(" ", ",").split(",")

                tag += word.extra_tags

                myword = MyWord(
                        word=row.lemma,
                        tags=tag,
                        is_normal_form=True,
                        word_register="get_register"
                    )
                dict_row = {
                    "lemma": row.lemma,
                    "pos": row.pos,
                    "tags": myword.required_tags + myword.extra_tags,
                    "frequency": frequency,
                    "source": "freq_dict"
                }

                if myword.parse_chosen and myword.parse_chosen.tag.animacy:
                    dict_row["tags"].append(myword.parse_chosen.tag.animacy)

                dict_row["tags"] = set(dict_row["tags"])

                if dict_row not in dict_rows:
                    dict_rows.append(dict_row)

        else:
            dict_row = {
                "lemma": row.lemma,
                "pos": row.pos,
                "tags": word.required_tags + word.extra_tags,
                "frequency": row.frequency,
                "source": "freq_dict"
            }

            if word.parse_chosen and word.parse_chosen.tag.animacy:
                dict_row["tags"].append(word.parse_chosen.tag.animacy)

            dict_row["tags"] = set(dict_row["tags"])

            if dict_row not in dict_rows:
                dict_rows.append(dict_row)

    for d_row in dict_rows:
        d_row["tags"] = str(sorted(list(d_row["tags"])))
        # SESSION.add(WordModel(word_json=json_row))
    
    SESSION.commit()
    SESSION.close()


def add_dict(text, source, tags=None, is_normal_form=False, word_register="get_register"):

    words_dict_query = SESSION.query(WordModel)
    old_dict = words_dict_query.filter(WordModel.source == source)
    old_dict.delete(synchronize_session=False)

    if not tags:
        tags = []

    sentences = split_by_sentences(text)
    lemms = []

    for sentence in sentences:
            sentence_words = split_by_words(sentence)
            lemms.append({"lemma": sentence_words[0], "register": None})

            for sentence_word in sentence_words[1:]:
                lemms.append({"lemma": sentence_word, "register": word_register})

    dict_rows = []
    myword_instances_list = []

    for lemma in lemms:
        word_0 = MyWord(
            lemma["lemma"],
            tags=tags,
            is_normal_form=is_normal_form,
            word_register=lemma["register"]
        )

        if not word_0.parses:
            continue

        word_forms = set([(w.normal_form, w.tag.POS) for w in word_0.parses])

        frequency_0 = 1 / len(word_forms)

        for word_form in word_forms:

            word_1 = MyWord(
                word=word_form[0],
                tags=word_form[1],
                is_normal_form=True,
                word_register=lemma["register"]
            )
            frequency = frequency_0 / len(word_1.parses)

            if len(word_1.parses) == 1:
                word_2 = word_1
                myword_instances_list.append((word_2, frequency))

            else:
                for parse in word_1.parses:
                    parse_tag = str(parse.tag).replace(" ", ",").split(",") + word_1.extra_tags
                    word_2 = MyWord(
                        word=word_form[0],
                        tags=parse_tag,
                        is_normal_form=True,
                        word_register=lemma["register"]
                    )
                    if word_2.parse_chosen:
                        myword_instances_list.append((word_2, frequency))

    for myword_instance in myword_instances_list:
        dict_row = ({
            "word": myword_instance[0].word,
            "tags_num": 0,
            "tags_info": sorted(list(set(myword_instance[0].required_tags + myword_instance[0].extra_tags))),
            "frequency": myword_instance[1]
        })
        dict_row["pos"] = dict_row["tags_info"][0]

        if not dict_row in dict_rows:
            dict_rows.append(dict_row)

    for d_row in dict_rows:
        print(d_row)
        #SESSION.add


def insert_sentences_to_db(name_without_extension, folder="books"):
    sentences = split_by_sentences(name_without_extension, folder)

    for sentence in sentences:
        sentence_words = re.sub(r'[^-A-яA-z\s\d]|(?<![A-яA-z](?=.[A-яA-z]))-', "", sentence)
        sentence_words = re.sub(r'(\s+)', " ", sentence_words)
        sentence_words = re.sub(r'(^\s|\s$)', "", sentence_words)
        sentence_words = sentence_words.split(" ")
        sentence_length = len(sentence_words)

        #sentences_insert.execute({
            #'sentence': sentence,
            #'sentence_length': sentence_length,
            #'source': name_without_extension
        #})


#add_freq_dict()
add_dict("Вася обиделся. Обидевшийся, обозленный и зеленый Паша ушел к испанке", source=None)