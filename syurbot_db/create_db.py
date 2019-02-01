import csv
from syur_classes import MyWord
from config.config import engine
from syurbot_db.db_models.frequency import FrequencyModel
from syurbot_db.db_models.tag import TagModel
from syurbot_db.db_models.tagset import TagSetModel
from syurbot_db.db_models.tagset_has_tag import TagSetHasTagModel
from syurbot_db.db_models.word import WordModel
from syurbot_db.db_models.sentence import SentenceModel
from syurbot_db.db_session import SESSION


def create_tables():
    FrequencyModel.__table__.create(engine)
    TagModel.__table__.create(engine)
    TagSetModel.__table__.create(engine)
    TagSetHasTagModel.__table__.create(engine)
    WordModel.__table__.create(engine)
    SentenceModel.__table__.create(engine)


def add_tag_data():
    opencorp_tags = open("opencorp_tags.txt").readlines()
    tags = [opencorp_tag.rstrip() for opencorp_tag in opencorp_tags] + MyWord.custom_tags

    for tag in tags:
        SESSION.add(TagModel(tag=tag))
    SESSION.commit()


def add_frequency_data():

    dict_rows = []
    with open("freq_dict.csv", 'r', encoding='utf-8') as freq_dict:
        file_dialect = csv.Sniffer().sniff(freq_dict.read(1024))
        freq_dict.seek(0)
        dict_reader = csv.DictReader(freq_dict, dialect=file_dialect)

        for dict_row in dict_reader:
            dict_row = dict(dict_row)
            dict_row["lemma"] = dict_row.pop("\ufefflemma")
            dict_row["frequency"] = float(dict_row["frequency"].replace(",", "."))
            dict_rows.append(dict_row)

    frequency_query = SESSION.query(FrequencyModel)
    old_frequency = frequency_query.filter(FrequencyModel.lemma != "")
    old_frequency.delete(synchronize_session=False)

    for dict_row in dict_rows:
        SESSION.add(
            FrequencyModel(
                lemma=dict_row["lemma"],
                dict_pos=dict_row["dict_pos"],
                pos=dict_row["pos"],
                by_hands_tags=dict_row["by_hands_tags"],
                frequency=float(dict_row["frequency"])
            )
        )

    SESSION.commit()


from libs.text_funcs import load_some_text
text = load_some_text("ann_kar_ex")
#create_tables()
#from syurbot_db.db_add_words import add_freq_dict
from syurbot_db.db_add_words import add_dict
#add_freq_dict() # 18:16 - 18:23
add_dict(text=text, word_source="ann_kar_ex") #18:29 18:45

SESSION.add(WordModel(word='jopa'))
a = SESSION.query(WordModel).filter(WordModel.word.like("j%"))
b = [r.word for r in a]
SESSION.add(WordModel(word='jjj'))
for row in a: print(row.word)
print("b", b)

a = SESSION.query(WordModel).filter(WordModel.word.like("j%"))
#a = SESSION.add(WordModel(word='jjj'))