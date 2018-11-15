from config.config import engine
from syur_classes import MyWord

from sqlalchemy import Table, MetaData
from sqlalchemy.sql import select

metadata = MetaData(engine)
conn = engine.connect()

fd = Table('fd', metadata, autoload=True)
freq_dict = Table('freq_dict', metadata, autoload=True)
freq_dict_insert = freq_dict.insert()

select_fd = select([fd])

freq_dict_list = []

for row in conn.execute(select_fd):
    word = MyWord(word=row[fd.c.lemma], tags=row[fd.c.pos], is_normal_form=True, word_register="get_register")
    if row[fd.c.pos] == "NOUN" and word.parses and len(word.parses) > 1:

        for parse in word.parses:
            tag = str(parse.tag).replace(" ", ",").split(",")

            if "multianim" in word.all_tags:
                tag.append("multianim")
            print(
                row[fd.c.lemma],
                row[fd.c.pos],
                MyWord(
                    word=row[fd.c.lemma],
                    tags=tag,
                    is_normal_form=True,
                    word_register="get_register"
                ).all_tags,
                row[fd.c.frequency]
            )
    else:
        print(
            row[fd.c.lemma],
            row[fd.c.pos],
            word.all_tags,
            row[fd.c.frequency]
        )
